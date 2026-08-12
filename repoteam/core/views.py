import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from .models import ActivityEvent, Notification, Profile, Project, ProjectApplication, ProjectMembership, ProjectRole, UserPreference


def _record_activity(event_type, actor=None, project=None, application=None, **metadata):
    return ActivityEvent.objects.create(
        event_type=event_type,
        actor=actor,
        project=project,
        application=application,
        metadata=metadata,
    )


def _create_notification(recipient, notification_type, title, body, actor=None, project=None, application=None):
    if not recipient or (actor and recipient.pk == actor.pk):
        return None
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        body=body,
        actor=actor,
        project=project,
        application=application,
    )


def _notify_project_members(project, notification_type, title, body, actor=None, application=None):
    recipients = User.objects.filter(
        Q(pk=project.owner_id) | Q(project_memberships__project=project)
    ).distinct().exclude(pk=getattr(actor, "pk", None))
    for recipient in recipients:
        _create_notification(recipient, notification_type, title, body, actor=actor, project=project, application=application)


def _serialize_notification(notification):
    actor_profile = None
    if notification.actor_id:
        actor_profile, _ = Profile.objects.get_or_create(user=notification.actor)
    actor_name = (actor_profile.display_name if actor_profile else "") or (notification.actor.username if notification.actor_id else "RepoTeam")
    return {
        "id": notification.id,
        "type": notification.notification_type,
        "title": notification.title,
        "body": notification.body,
        "actor": {"id": notification.actor_id, "username": notification.actor.username if notification.actor_id else "", "display_name": actor_name} if notification.actor_id else None,
        "project": {"slug": notification.project.slug, "title": notification.project.title} if notification.project_id else None,
        "application_id": notification.application_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
    }


def _serialize_preferences(preferences):
    return {
        "email_applications": preferences.email_applications,
        "email_decisions": preferences.email_decisions,
        "email_invitations": preferences.email_invitations,
        "email_project_updates": preferences.email_project_updates,
        "show_availability": preferences.show_availability,
        "show_activity": preferences.show_activity,
        "compact_project_cards": preferences.compact_project_cards,
        "reduce_motion": preferences.reduce_motion,
        "updated_at": preferences.updated_at.isoformat(),
    }

def api_info(request):
    return JsonResponse(
        {
            "service": "RepoTeam API",
            "status": "ok",
            "backend": "Django",
        }
    )


def health_api(request):
    return JsonResponse(
        {
            "service": "RepoTeam API",
            "status": "ok",
            "backend": "Django",
        }
    )


def me_api(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"authenticated": False, "user": None})

    profile, _ = Profile.objects.get_or_create(user=user)
    return JsonResponse({"authenticated": True, "user": _serialize_profile(profile, include_email=True)})


def _parse_json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return None


def _serialize_profile(profile, include_email=False):
    user = profile.user
    preferences, _ = UserPreference.objects.get_or_create(user=user)
    data = {
        "id": user.id, "username": user.username, "display_name": profile.display_name or user.username,
        "title": profile.title, "bio": profile.bio, "location": profile.location, "skills": profile.skills,
        "experience": profile.experience, "availability": profile.availability if include_email or preferences.show_availability else "", "github_url": profile.github_url,
        "linkedin_url": profile.linkedin_url, "is_public": profile.is_public,
        "created_at": profile.created_at.isoformat(), "updated_at": profile.updated_at.isoformat(),
    }
    if include_email:
        data["email"] = user.email
    return data


def _require_authenticated_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)
    return None


def _profile_payload_error(data):
    skills = data.get("skills")
    if skills is not None and (not isinstance(skills, list) or any(not isinstance(skill, str) or not skill.strip() for skill in skills)):
        return "Skills must be a list of non-empty strings."
    experience = data.get("experience")
    if experience is not None and experience not in {"", *Profile.Experience.values}:
        return "Invalid experience value."
    availability = data.get("availability")
    if availability is not None and availability not in Profile.Availability.values:
        return "Invalid availability value."
    return None


@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    username = data.get("username", "")
    password = data.get("password", "")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {"error": "Invalid username and/or password."},
            status=400,
        )

    login(request, user)
    profile, _ = Profile.objects.get_or_create(user=user)
    return JsonResponse({"message": "Logged in successfully.", "user": _serialize_profile(profile, include_email=True)})


@csrf_exempt
def logout_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    logout(request)
    return JsonResponse({"message": "Logged out successfully."})


@csrf_exempt
def register_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    username = data.get("username", "")
    email = data.get("email", "")
    display_name = data.get("display_name", data.get("name", ""))
    password = data.get("password", "")
    confirmation = data.get("confirmation", "")

    if password != confirmation:
        return JsonResponse({"error": "Passwords must match."}, status=400)

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
    except IntegrityError:
        return JsonResponse({"error": "Username already taken."}, status=400)

    profile = Profile.objects.create(user=user, display_name=display_name.strip())
    login(request, user)
    return JsonResponse(
        {
            "message": "Account created successfully.",
            "user": _serialize_profile(profile, include_email=True),
        },
        status=201,
    )


def developers_api(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    profiles = Profile.objects.select_related("user").filter(is_public=True)
    query, skill = request.GET.get("q", "").strip(), request.GET.get("skill", "").strip()
    experience, availability = request.GET.get("experience", "").strip(), request.GET.get("availability", "").strip()
    ordering = request.GET.get("ordering", "recommended")
    try:
        page = max(int(request.GET.get("page", 1)), 1)
        page_size = min(max(int(request.GET.get("page_size", 12)), 1), 50)
    except ValueError:
        return JsonResponse({"error": "page and page_size must be integers."}, status=400)
    if query:
        profiles = profiles.filter(Q(user__username__icontains=query) | Q(display_name__icontains=query) | Q(title__icontains=query) | Q(bio__icontains=query) | Q(location__icontains=query) | Q(skills__icontains=query))
    if skill:
        profiles = profiles.filter(skills__icontains=skill)
    if experience:
        profiles = profiles.filter(experience=experience)
    if availability:
        profiles = profiles.filter(availability=availability, user__preferences__show_availability=True)
    ordering_map = {"name": "display_name", "recent": "-created_at", "recommended": "-updated_at"}
    profiles = profiles.order_by(ordering_map.get(ordering, "-updated_at"), "user__username")
    count = profiles.count()
    start = (page - 1) * page_size
    return JsonResponse({
        "count": count,
        "page": page,
        "page_size": page_size,
        "has_next": start + page_size < count,
        "results": [_serialize_profile(profile) for profile in profiles[start:start + page_size]],
    })


def developer_detail_api(request, username):
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    profile = get_object_or_404(Profile.objects.select_related("user"), user__username=username, is_public=True)
    return JsonResponse({"developer": _serialize_profile(profile)})


@csrf_exempt
def my_profile_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "GET":
        return JsonResponse({"profile": _serialize_profile(profile, include_email=True)})
    if request.method != "PATCH":
        return JsonResponse({"error": "GET or PATCH required."}, status=405)
    data = _parse_json_body(request)
    if data is None or not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    error = _profile_payload_error(data)
    if error:
        return JsonResponse({"error": error}, status=400)
    profile_fields = {"display_name", "title", "bio", "location", "skills", "experience", "availability", "github_url", "linkedin_url", "is_public"}
    for field in profile_fields.intersection(data):
        value = data[field]
        if field == "skills":
            value = [skill.strip() for skill in value]
        elif isinstance(value, str):
            value = value.strip()
        setattr(profile, field, value)
    if "email" in data:
        request.user.email = str(data["email"]).strip()
        request.user.save(update_fields=["email"])
    profile.save()
    return JsonResponse({"message": "Profile updated successfully.", "profile": _serialize_profile(profile, include_email=True)})


def _serialize_role(role):
    return {
        "id": role.id,
        "title": role.title,
        "description": role.description,
        "required_skills": role.required_skills,
        "experience": role.experience,
        "status": role.status,
        "created_at": role.created_at.isoformat(),
        "updated_at": role.updated_at.isoformat(),
    }


def _serialize_membership(membership):
    profile, _ = Profile.objects.get_or_create(user=membership.user)
    return {
        "id": membership.id,
        "project_id": membership.project.slug,
        "project_title": membership.project.title,
        "user": {"id": membership.user_id, "username": membership.user.username, "display_name": profile.display_name or membership.user.username},
        "username": membership.user.username,
        "display_name": profile.display_name or membership.user.username,
        "member_role": membership.member_role,
        "role": _serialize_role(membership.role) if membership.role else None,
        "role_title": membership.role.title if membership.role else ("Project owner" if membership.member_role == ProjectMembership.MemberRole.OWNER else "Project contributor"),
        "joined_at": membership.joined_at.isoformat(),
    }


def _serialize_application(application):
    applicant_profile, _ = Profile.objects.get_or_create(user=application.applicant)
    owner_profile, _ = Profile.objects.get_or_create(user=application.project.owner)
    return {
        "id": application.id,
        "status": application.status,
        "message": application.message,
        "role": _serialize_role(application.role) if application.role else None,
        "role_title": application.role.title if application.role else "Project contributor",
        "project_id": application.project.slug,
        "project_title": application.project.title,
        "applicant_username": application.applicant.username,
        "project": {
            "id": application.project.slug,
            "slug": application.project.slug,
            "title": application.project.title,
            "owner_username": application.project.owner.username,
            "owner_name": owner_profile.display_name or application.project.owner.username,
        },
        "applicant": {
            "id": application.applicant_id,
            "username": application.applicant.username,
            "display_name": applicant_profile.display_name or application.applicant.username,
        },
        "created_at": application.created_at.isoformat(),
        "updated_at": application.updated_at.isoformat(),
        "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
    }


def _ensure_owner_membership(project):
    membership, _ = ProjectMembership.objects.get_or_create(
        project=project,
        user=project.owner,
        defaults={"member_role": ProjectMembership.MemberRole.OWNER},
    )
    if membership.member_role != ProjectMembership.MemberRole.OWNER:
        membership.member_role = ProjectMembership.MemberRole.OWNER
        membership.role = None
        membership.save(update_fields=["member_role", "role", "updated_at"])
    return membership


def _project_membership_for_user(project, user):
    if not user or not user.is_authenticated:
        return None
    return ProjectMembership.objects.filter(project=project, user=user).select_related("role").first()


def _serialize_project(project, request_user=None):
    profile, _ = Profile.objects.get_or_create(user=project.owner)
    owner_name = profile.display_name or project.owner.username
    open_roles = [role for role in project.roles.all() if role.status == ProjectRole.Status.OPEN]
    is_owner = bool(request_user and request_user.is_authenticated and request_user.pk == project.owner_id)
    membership = _project_membership_for_user(project, request_user)
    member_count = project.memberships.count()
    if not project.memberships.filter(user_id=project.owner_id).exists():
        member_count += 1
    application = None
    if request_user and request_user.is_authenticated and not is_owner:
        application = project.applications.filter(applicant=request_user).order_by("-created_at").first()
    return {
        "id": project.slug,
        "slug": project.slug,
        "title": project.title,
        "name": project.title,
        "short_description": project.short_description,
        "description": project.short_description,
        "long_description": project.description or project.short_description,
        "repository_url": project.repository_url,
        "project_type": project.project_type,
        "type": project.project_type,
        "difficulty": project.difficulty,
        "status": project.status,
        "team_capacity": project.team_capacity,
        "team_size": project.team_capacity,
        "contributors": member_count,
        "member_count": member_count,
        "technologies": project.technologies,
        "stack": project.technologies,
        "workflow_status": project.workflow_status,
        "roles": [_serialize_role(role) for role in open_roles],
        "owner": {"username": project.owner.username, "display_name": owner_name},
        "owner_name": owner_name,
        "owner_username": project.owner.username,
        "is_owner": is_owner,
        "is_member": bool(membership) or is_owner,
        "membership": _serialize_membership(membership) if membership else ({"member_role": "owner", "role": None} if is_owner else None),
        "application": _serialize_application(application) if application else None,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "published_at": project.published_at.isoformat() if project.published_at else None,
    }


def _project_payload_error(data, creating=False):
    required = {"title", "short_description", "project_type", "difficulty"}
    aliases = {"name": "title", "description_short": "short_description", "type": "project_type", "team_size": "team_capacity", "stack": "technologies"}
    normalized = {aliases.get(key, key): value for key, value in data.items()}
    if creating:
        missing = [field for field in required if not str(normalized.get(field, "")).strip()]
        if missing:
            return "Missing required fields: " + ", ".join(sorted(missing)) + "."
    if "title" in normalized and (not isinstance(normalized["title"], str) or len(normalized["title"].strip()) > 160):
        return "Title must be a non-empty string up to 160 characters."
    if "short_description" in normalized and (not isinstance(normalized["short_description"], str) or not normalized["short_description"].strip() or len(normalized["short_description"].strip()) > 500):
        return "Short description must be a non-empty string up to 500 characters."
    if "project_type" in normalized and normalized["project_type"] not in Project.ProjectType.values:
        return "Invalid project type."
    if "difficulty" in normalized and normalized["difficulty"] not in Project.Difficulty.values:
        return "Invalid difficulty."
    if "status" in normalized and normalized["status"] not in Project.Status.values:
        return "Invalid project status."
    if "team_capacity" in normalized:
        try:
            if not 1 <= int(normalized["team_capacity"]) <= 1000:
                return "Team capacity must be between 1 and 1000."
        except (TypeError, ValueError):
            return "Team capacity must be an integer."
    if "technologies" in normalized and (not isinstance(normalized["technologies"], list) or any(not isinstance(item, str) or not item.strip() for item in normalized["technologies"])):
        return "Technologies must be a list of non-empty strings."
    if "roles" in normalized:
        if not isinstance(normalized["roles"], list):
            return "Roles must be a list."
        for role in normalized["roles"]:
            if not isinstance(role, dict) or not isinstance(role.get("title"), str) or not role["title"].strip():
                return "Each role requires a title."
            if len(role["title"].strip()) > 120:
                return "Role titles must be at most 120 characters."
            if role.get("experience", ProjectRole.Experience.ANY) not in ProjectRole.Experience.values:
                return "Invalid role experience value."
            if role.get("status", ProjectRole.Status.OPEN) not in ProjectRole.Status.values:
                return "Invalid role status."
            skills = role.get("required_skills", [])
            if not isinstance(skills, list) or any(not isinstance(skill, str) or not skill.strip() for skill in skills):
                return "Role required skills must be a list of non-empty strings."
    return None


def _normalized_project_data(data):
    aliases = {"name": "title", "description_short": "short_description", "type": "project_type", "team_size": "team_capacity", "stack": "technologies"}
    return {aliases.get(key, key): value for key, value in data.items()}


def _unique_project_slug(title, project=None):
    base = slugify(title)[:180] or "project"
    candidate, suffix = base, 2
    projects = Project.objects.exclude(pk=project.pk) if project else Project.objects.all()
    while projects.filter(slug=candidate).exists():
        candidate = f"{base[:185]}-{suffix}"
        suffix += 1
    return candidate


def _replace_roles(project, roles):
    project.roles.all().delete()
    ProjectRole.objects.bulk_create([
        ProjectRole(
            project=project,
            title=role["title"].strip(),
            description=str(role.get("description", "")).strip(),
            required_skills=[skill.strip() for skill in role.get("required_skills", [])],
            experience=role.get("experience", ProjectRole.Experience.ANY),
            status=role.get("status", ProjectRole.Status.OPEN),
        )
        for role in roles
    ])


def _member_count(project):
    count = project.memberships.count()
    if not project.memberships.filter(user_id=project.owner_id).exists():
        count += 1
    return count


def _application_payload_error(data):
    if not isinstance(data, dict):
        return "Invalid JSON body."
    message = data.get("message", "")
    if message is not None and not isinstance(message, str):
        return "Message must be a string."
    if isinstance(message, str) and len(message.strip()) > 2000:
        return "Message must be at most 2000 characters."
    return None


def _published_project_for_action(request, slug):
    project = get_object_or_404(Project.objects.select_related("owner"), slug=slug)
    if project.workflow_status != Project.WorkflowStatus.PUBLISHED:
        return None
    return project


@csrf_exempt
def join_project_api(request, slug):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    project = _published_project_for_action(request, slug)
    if project is None:
        return JsonResponse({"error": "Project not found."}, status=404)
    if project.owner_id == request.user.id:
        return JsonResponse({"error": "The project owner is already a member."}, status=400)
    with transaction.atomic():
        project = Project.objects.select_for_update().get(pk=project.pk)
        if ProjectMembership.objects.filter(project=project, user=request.user).exists():
            return JsonResponse({"error": "You are already a member of this project."}, status=400)
        if _member_count(project) >= project.team_capacity:
            return JsonResponse({"error": "This project has reached its team capacity."}, status=400)
        membership = ProjectMembership.objects.create(project=project, user=request.user)
        _record_activity(ActivityEvent.EventType.MEMBER_JOINED, actor=request.user, project=project)
        _notify_project_members(
            project,
            Notification.NotificationType.PROJECT_UPDATE,
            "New project teammate",
            f"{request.user.get_full_name() or request.user.username} joined {project.title}.",
            actor=request.user,
        )
    return JsonResponse({"message": "You joined the project successfully.", "membership": _serialize_membership(membership)}, status=201)


@csrf_exempt
def apply_project_api(request, slug, role_id=None):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    project = _published_project_for_action(request, slug)
    if project is None:
        return JsonResponse({"error": "Project not found."}, status=404)
    if project.owner_id == request.user.id:
        return JsonResponse({"error": "Project owners cannot apply to their own project."}, status=400)
    if ProjectMembership.objects.filter(project=project, user=request.user).exists():
        return JsonResponse({"error": "You are already a member of this project."}, status=400)
    data = _parse_json_body(request)
    if data is None or not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    error = _application_payload_error(data)
    if error:
        return JsonResponse({"error": error}, status=400)
    if role_id is None:
        role_id = data.get("role_id", data.get("role"))
    try:
        role = ProjectRole.objects.get(pk=role_id, project=project)
    except (ProjectRole.DoesNotExist, TypeError, ValueError):
        return JsonResponse({"error": "An open project role is required."}, status=400)
    if role.status != ProjectRole.Status.OPEN:
        return JsonResponse({"error": "This project role is closed."}, status=400)
    if project.applications.filter(applicant=request.user, status=ProjectApplication.Status.PENDING).exists():
        return JsonResponse({"error": "You already have a pending application for this project."}, status=400)
    application = ProjectApplication.objects.create(
        project=project,
        applicant=request.user,
        role=role,
        message=str(data.get("message", "")).strip(),
    )
    _record_activity(ActivityEvent.EventType.APPLICATION_SUBMITTED, actor=request.user, project=project, application=application, role_title=role.title)
    _create_notification(
        project.owner,
        Notification.NotificationType.APPLICATION,
        "New application",
        f"{request.user.get_full_name() or request.user.username} applied for {role.title} on {project.title}.",
        actor=request.user,
        project=project,
        application=application,
    )
    return JsonResponse({"message": "Application submitted successfully.", "application": _serialize_application(application)}, status=201)


def applications_api(request, box=None):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    applications = ProjectApplication.objects.select_related(
        "project", "project__owner", "project__owner__profile", "applicant", "applicant__profile", "role", "reviewed_by"
    )
    kind = (box or request.GET.get("kind", request.GET.get("box", "sent"))).lower()
    if kind == "received":
        applications = applications.filter(project__owner=request.user)
    elif kind == "sent":
        applications = applications.filter(applicant=request.user)
    elif kind in {"all", ""}:
        applications = applications.filter(Q(applicant=request.user) | Q(project__owner=request.user)).distinct()
    else:
        return JsonResponse({"error": "kind must be sent, received, or all."}, status=400)
    status = request.GET.get("status", "").lower()
    if status:
        if status not in ProjectApplication.Status.values:
            return JsonResponse({"error": "Invalid application status."}, status=400)
        applications = applications.filter(status=status)
    return JsonResponse({
        "kind": kind or "all",
        "count": applications.count(),
        "results": [_serialize_application(application) for application in applications],
    })


@csrf_exempt
def application_detail_api(request, application_id):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    application = get_object_or_404(ProjectApplication.objects.select_related("project", "project__owner", "applicant", "role"), pk=application_id)
    if request.user.id not in {application.applicant_id, application.project.owner_id}:
        return JsonResponse({"error": "You do not have access to this application."}, status=403)
    if request.method == "GET":
        return JsonResponse({"application": _serialize_application(application)})
    if request.method != "PATCH":
        return JsonResponse({"error": "GET or PATCH required."}, status=405)
    data = _parse_json_body(request)
    if not isinstance(data, dict) or data.get("status") not in ProjectApplication.Status.values:
        return JsonResponse({"error": "A valid application status is required."}, status=400)
    desired_status = data["status"]
    if desired_status == ProjectApplication.Status.WITHDRAWN:
        if request.user.id != application.applicant_id:
            return JsonResponse({"error": "Only the applicant can withdraw an application."}, status=403)
        return withdraw_application_api(request, application_id)
    if desired_status in {ProjectApplication.Status.ACCEPTED, ProjectApplication.Status.REJECTED}:
        if request.user.id != application.project.owner_id:
            return JsonResponse({"error": "Only the project owner can review applications."}, status=403)
        return review_application_api(request, application_id, desired_status)
    return JsonResponse({"error": "Applications can only be withdrawn, accepted, or rejected."}, status=400)


@csrf_exempt
def withdraw_application_api(request, application_id):
    if request.method != "POST" and request.method != "PATCH":
        return JsonResponse({"error": "POST required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    application = get_object_or_404(ProjectApplication, pk=application_id)
    if application.applicant_id != request.user.id:
        return JsonResponse({"error": "Only the applicant can withdraw an application."}, status=403)
    if application.status != ProjectApplication.Status.PENDING:
        return JsonResponse({"error": "Only pending applications can be withdrawn."}, status=400)
    application.status = ProjectApplication.Status.WITHDRAWN
    application.save(update_fields=["status", "updated_at"])
    _record_activity(ActivityEvent.EventType.APPLICATION_WITHDRAWN, actor=request.user, project=application.project, application=application)
    return JsonResponse({"message": "Application withdrawn.", "application": _serialize_application(application)})


@csrf_exempt
def review_application_api(request, application_id, decision):
    if request.method != "POST" and request.method != "PATCH":
        return JsonResponse({"error": "POST required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    application = get_object_or_404(ProjectApplication.objects.select_related("project", "role", "applicant"), pk=application_id)
    if application.project.owner_id != request.user.id:
        return JsonResponse({"error": "Only the project owner can review applications."}, status=403)
    if decision not in {ProjectApplication.Status.ACCEPTED, ProjectApplication.Status.REJECTED}:
        return JsonResponse({"error": "Invalid application decision."}, status=400)
    if application.status != ProjectApplication.Status.PENDING:
        return JsonResponse({"error": "Only pending applications can be reviewed."}, status=400)
    with transaction.atomic():
        project = Project.objects.select_for_update().get(pk=application.project_id)
        application = ProjectApplication.objects.select_for_update().select_related("role", "applicant", "project").get(pk=application_id)
        if application.status != ProjectApplication.Status.PENDING:
            return JsonResponse({"error": "Only pending applications can be reviewed."}, status=400)
        if decision == ProjectApplication.Status.ACCEPTED:
            membership, created = ProjectMembership.objects.get_or_create(
                project=project,
                user=application.applicant,
                defaults={"role": application.role},
            )
            if not created:
                return JsonResponse({"error": "The applicant is already a member of this project."}, status=400)
            if _member_count(project) > project.team_capacity:
                membership.delete()
                return JsonResponse({"error": "This project has reached its team capacity."}, status=400)
            _record_activity(ActivityEvent.EventType.MEMBER_JOINED, actor=application.applicant, project=project, application=application, source="application")
        application.status = decision
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        _record_activity(
            ActivityEvent.EventType.APPLICATION_ACCEPTED if decision == ProjectApplication.Status.ACCEPTED else ActivityEvent.EventType.APPLICATION_REJECTED,
            actor=request.user,
            project=project,
            application=application,
            applicant_name=application.applicant.get_full_name() or application.applicant.username,
        )
        decision_label = "accepted" if decision == ProjectApplication.Status.ACCEPTED else "declined"
        _create_notification(
            application.applicant,
            Notification.NotificationType.DECISION,
            f"Application {decision_label}",
            f"Your application for {project.title} was {decision_label}.",
            actor=request.user,
            project=project,
            application=application,
        )
    return JsonResponse({"message": f"Application {decision}.", "application": _serialize_application(application)})


@csrf_exempt
def accept_application_api(request, application_id):
    return review_application_api(request, application_id, ProjectApplication.Status.ACCEPTED)


@csrf_exempt
def reject_application_api(request, application_id):
    return review_application_api(request, application_id, ProjectApplication.Status.REJECTED)


@csrf_exempt
def invite_to_project_api(request, slug):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    project = get_object_or_404(Project.objects.select_related("owner"), slug=slug)
    if project.owner_id != request.user.id:
        return JsonResponse({"error": "Only the project owner can invite collaborators."}, status=403)
    data = _parse_json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    identifier = str(data.get("username", data.get("email", ""))).strip()
    invited_user = None
    if data.get("user_id"):
        invited_user = User.objects.filter(pk=data["user_id"]).first()
    if invited_user is None and identifier:
        invited_user = User.objects.filter(Q(username=identifier) | Q(email__iexact=identifier)).first()
    if invited_user is None:
        return JsonResponse({"error": "A valid RepoTeam username or email is required."}, status=400)
    if invited_user.pk == request.user.pk:
        return JsonResponse({"error": "You cannot invite yourself."}, status=400)
    if ProjectMembership.objects.filter(project=project, user=invited_user).exists():
        return JsonResponse({"error": "That person is already a project member."}, status=400)
    notification = _create_notification(
        invited_user,
        Notification.NotificationType.INVITATION,
        f"Invitation to {project.title}",
        f"{request.user.get_full_name() or request.user.username} invited you to collaborate on {project.title}.",
        actor=request.user,
        project=project,
    )
    return JsonResponse({"message": "Invitation sent.", "notification": _serialize_notification(notification)}, status=201)


def project_members_api(request, slug):
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    project = get_object_or_404(Project.objects.select_related("owner"), slug=slug)
    if project.workflow_status != Project.WorkflowStatus.PUBLISHED and project.owner_id != getattr(request.user, "id", None):
        return JsonResponse({"error": "Project not found."}, status=404)
    memberships = ProjectMembership.objects.filter(project=project).select_related("user", "user__profile", "role")
    if not memberships.filter(user_id=project.owner_id).exists():
        _ensure_owner_membership(project)
        memberships = memberships | ProjectMembership.objects.filter(project=project, user_id=project.owner_id).select_related("user", "user__profile", "role")
    return JsonResponse({"project": project.slug, "count": memberships.count(), "results": [_serialize_membership(member) for member in memberships]})


def my_memberships_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    for project in Project.objects.filter(owner=request.user):
        _ensure_owner_membership(project)
    memberships = ProjectMembership.objects.filter(user=request.user).select_related("project", "role")
    return JsonResponse({
        "count": memberships.count(),
        "results": [{
            "project": membership.project.slug,
            "project_title": membership.project.title,
            "member_role": membership.member_role,
            "role": _serialize_role(membership.role) if membership.role else None,
            "joined_at": membership.joined_at.isoformat(),
        } for membership in memberships],
    })


def _serialize_activity(event):
    actor_profile = None
    if event.actor_id:
        actor_profile, _ = Profile.objects.get_or_create(user=event.actor)
    actor_name = (actor_profile.display_name if actor_profile else "") or (event.actor.username if event.actor_id else "A builder")
    project_title = event.project.title if event.project_id else "the workspace"
    messages = {
        ActivityEvent.EventType.PROJECT_CREATED: f"created {project_title}",
        ActivityEvent.EventType.PROJECT_PUBLISHED: f"published {project_title}",
        ActivityEvent.EventType.MEMBER_JOINED: f"joined {project_title}",
        ActivityEvent.EventType.APPLICATION_SUBMITTED: f"applied to {project_title}",
        ActivityEvent.EventType.APPLICATION_ACCEPTED: f"accepted an application for {project_title}",
        ActivityEvent.EventType.APPLICATION_REJECTED: f"reviewed an application for {project_title}",
        ActivityEvent.EventType.APPLICATION_WITHDRAWN: f"withdrew an application from {project_title}",
    }
    return {
        "id": event.id,
        "event_type": event.event_type,
        "actor": {"id": event.actor_id, "username": event.actor.username if event.actor_id else "", "display_name": actor_name},
        "project": {"id": event.project.slug, "slug": event.project.slug, "title": project_title} if event.project_id else None,
        "application_id": event.application_id,
        "message": messages.get(event.event_type, project_title),
        "metadata": event.metadata,
        "created_at": event.created_at.isoformat(),
    }


def _recommend_projects(user, limit=6):
    profile, _ = Profile.objects.get_or_create(user=user)
    user_skills = {str(skill).strip().casefold() for skill in (profile.skills or []) if str(skill).strip()}
    member_project_ids = set(ProjectMembership.objects.filter(user=user).values_list("project_id", flat=True))
    member_project_ids.update(Project.objects.filter(owner=user).values_list("id", flat=True))
    candidates = Project.objects.filter(workflow_status=Project.WorkflowStatus.PUBLISHED).exclude(id__in=member_project_ids).prefetch_related("roles")
    scored = []
    for project in candidates:
        project_skills = {str(skill).strip().casefold() for skill in (project.technologies or []) if str(skill).strip()}
        role_skills = {str(skill).strip().casefold() for role in project.roles.filter(status=ProjectRole.Status.OPEN) for skill in (role.required_skills or []) if str(skill).strip()}
        matches = sorted(user_skills.intersection(project_skills | role_skills))
        if profile.availability == Profile.Availability.UNAVAILABLE:
            continue
        score = len(matches) * 25
        if project.status == Project.Status.RECRUITING:
            score += 10
        if project.roles.filter(status=ProjectRole.Status.OPEN).exists():
            score += 5
        if not user_skills:
            score = 1 if project.status == Project.Status.RECRUITING else 0
        scored.append((score, project.updated_at, matches, project))
    scored.sort(key=lambda item: (-item[0], -item[1].timestamp(), item[3].title.casefold()))
    results = []
    for score, _, matches, project in scored[:limit]:
        serialized = _serialize_project(project, user)
        serialized["match_score"] = score
        serialized["matched_skills"] = matches
        serialized["match_reasons"] = ([f"Matches your {', '.join(matches)} skills"] if matches else [])
        if project.status == Project.Status.RECRUITING:
            serialized["match_reasons"].append("Actively recruiting")
        results.append(serialized)
    return results


def _visible_activity(user, limit=None):
    events = ActivityEvent.objects.filter(
        Q(actor=user) | Q(project__owner=user) | Q(project__memberships__user=user) | Q(application__applicant=user)
    ).select_related("actor", "actor__profile", "project", "application").distinct()
    return events[:limit] if limit else events


def _dashboard_payload(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    owned = Project.objects.filter(owner=user).select_related("owner", "owner__profile").prefetch_related("roles")
    contributing = Project.objects.filter(memberships__user=user).exclude(owner=user).distinct().select_related("owner", "owner__profile").prefetch_related("roles")
    for project in owned:
        _ensure_owner_membership(project)
    project_ids = list(owned.values_list("id", flat=True)) + list(contributing.values_list("id", flat=True))
    team_members = ProjectMembership.objects.filter(project_id__in=project_ids).exclude(user=user).values("user_id").distinct().count()
    sent = ProjectApplication.objects.filter(applicant=user)
    received = ProjectApplication.objects.filter(project__owner=user)
    visible_activity = _visible_activity(user, 12)
    open_roles = ProjectRole.objects.filter(project__owner=user, status=ProjectRole.Status.OPEN).count()
    return {
        "user": _serialize_profile(profile, include_email=True),
        "summary": {
            "owned_projects": owned.count(),
            "contributing_projects": contributing.count(),
            "projects": owned.count() + contributing.count(),
            "team_members": team_members,
            "applications_sent": sent.count(),
            "pending_applications": sent.filter(status=ProjectApplication.Status.PENDING).count(),
            "applications_to_review": received.filter(status=ProjectApplication.Status.PENDING).count(),
            "open_roles": open_roles,
            "contributions": ProjectMembership.objects.filter(user=user).exclude(member_role=ProjectMembership.MemberRole.OWNER).count(),
        },
        "owned_projects": [_serialize_project(project, user) for project in owned[:12]],
        "contributing_projects": [_serialize_project(project, user) for project in contributing[:12]],
        "activity": [_serialize_activity(event) for event in visible_activity],
        "recommendations": _recommend_projects(user),
    }


def dashboard_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    return JsonResponse(_dashboard_payload(request.user))


def dashboard_projects_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    payload = _dashboard_payload(request.user)
    return JsonResponse({"summary": payload["summary"], "owned_projects": payload["owned_projects"], "contributing_projects": payload["contributing_projects"]})


def activity_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    try:
        limit = min(max(int(request.GET.get("limit", 30)), 1), 100)
    except ValueError:
        return JsonResponse({"error": "limit must be an integer."}, status=400)
    events = _visible_activity(request.user)
    return JsonResponse({"count": events.count(), "results": [_serialize_activity(event) for event in events[:limit]]})


def recommendations_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)
    try:
        limit = min(max(int(request.GET.get("limit", 6)), 1), 24)
    except ValueError:
        return JsonResponse({"error": "limit must be an integer."}, status=400)
    results = _recommend_projects(request.user, limit)
    return JsonResponse({"count": len(results), "results": results})


@csrf_exempt
def notifications_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if request.method == "GET":
        notifications = Notification.objects.filter(recipient=request.user).select_related("actor", "actor__profile", "project", "application")
        unread = request.GET.get("unread", "").lower()
        if unread in {"1", "true", "yes"}:
            notifications = notifications.filter(is_read=False)
        try:
            limit = min(max(int(request.GET.get("limit", 30)), 1), 100)
        except ValueError:
            return JsonResponse({"error": "limit must be an integer."}, status=400)
        return JsonResponse({
            "count": notifications.count(),
            "unread_count": notifications.filter(is_read=False).count(),
            "results": [_serialize_notification(notification) for notification in notifications[:limit]],
        })
    if request.method != "PATCH":
        return JsonResponse({"error": "GET or PATCH required."}, status=405)
    data = _parse_json_body(request)
    if not isinstance(data, dict) or not isinstance(data.get("ids"), list) or not isinstance(data.get("is_read"), bool):
        return JsonResponse({"error": "ids must be a list and is_read must be a boolean."}, status=400)
    ids = [item for item in data["ids"] if isinstance(item, int)]
    updated = Notification.objects.filter(recipient=request.user, id__in=ids).update(is_read=data["is_read"])
    return JsonResponse({"message": "Notifications updated.", "updated": updated})


@csrf_exempt
def notification_detail_api(request, notification_id):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    notification = get_object_or_404(Notification.objects.select_related("actor", "actor__profile", "project", "application"), pk=notification_id, recipient=request.user)
    if request.method == "GET":
        return JsonResponse({"notification": _serialize_notification(notification)})
    if request.method != "PATCH":
        return JsonResponse({"error": "GET or PATCH required."}, status=405)
    data = _parse_json_body(request)
    if not isinstance(data, dict) or not isinstance(data.get("is_read"), bool):
        return JsonResponse({"error": "is_read must be a boolean."}, status=400)
    notification.is_read = data["is_read"]
    notification.save(update_fields=["is_read"])
    return JsonResponse({"message": "Notification updated.", "notification": _serialize_notification(notification)})


@csrf_exempt
def mark_all_notifications_read_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    updated = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"message": "All notifications marked as read.", "updated": updated})


@csrf_exempt
def preferences_api(request):
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == "GET":
        return JsonResponse({"preferences": _serialize_preferences(preferences)})
    if request.method != "PATCH":
        return JsonResponse({"error": "GET or PATCH required."}, status=405)
    data = _parse_json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    fields = {
        "email_applications", "email_decisions", "email_invitations", "email_project_updates",
        "show_availability", "show_activity", "compact_project_cards", "reduce_motion",
    }
    invalid = [field for field in fields.intersection(data) if not isinstance(data[field], bool)]
    if invalid:
        return JsonResponse({"error": f"{invalid[0]} must be a boolean."}, status=400)
    for field in fields.intersection(data):
        setattr(preferences, field, data[field])
    preferences.save()
    return JsonResponse({"message": "Preferences updated successfully.", "preferences": _serialize_preferences(preferences)})


@csrf_exempt
def projects_api(request):
    if request.method == "POST":
        auth_error = _require_authenticated_user(request)
        if auth_error:
            return auth_error
        data = _parse_json_body(request)
        if not isinstance(data, dict):
            return JsonResponse({"error": "Invalid JSON body."}, status=400)
        data = _normalized_project_data(data)
        error = _project_payload_error(data, creating=True)
        if error:
            return JsonResponse({"error": error}, status=400)
        workflow_status = data.get("workflow_status", Project.WorkflowStatus.DRAFT)
        if workflow_status not in {Project.WorkflowStatus.DRAFT, Project.WorkflowStatus.PUBLISHED}:
            return JsonResponse({"error": "New projects can only be drafts or published."}, status=400)
        project = Project.objects.create(
            owner=request.user,
            title=data["title"].strip(),
            slug=_unique_project_slug(data["title"]),
            short_description=data["short_description"].strip(),
            description=str(data.get("description", "")).strip(),
            repository_url=str(data.get("repository_url", "")).strip(),
            project_type=data["project_type"],
            difficulty=data["difficulty"],
            status=data.get("status", Project.Status.PLANNING),
            team_capacity=int(data.get("team_capacity", 5)),
            technologies=[item.strip() for item in data.get("technologies", [])],
            workflow_status=workflow_status,
            published_at=timezone.now() if workflow_status == Project.WorkflowStatus.PUBLISHED else None,
        )
        _replace_roles(project, data.get("roles", []))
        _ensure_owner_membership(project)
        _record_activity(ActivityEvent.EventType.PROJECT_CREATED, actor=request.user, project=project)
        project = Project.objects.prefetch_related("roles").select_related("owner").get(pk=project.pk)
        return JsonResponse({"message": "Project created successfully.", "project": _serialize_project(project, request.user)}, status=201)

    if request.method != "GET":
        return JsonResponse({"error": "GET or POST required."}, status=405)
    projects = Project.objects.select_related("owner", "owner__profile").prefetch_related("roles")
    mine = request.GET.get("mine", "").lower() in {"1", "true", "yes"}
    if mine:
        auth_error = _require_authenticated_user(request)
        if auth_error:
            return auth_error
        projects = projects.filter(owner=request.user)
    else:
        projects = projects.filter(workflow_status=Project.WorkflowStatus.PUBLISHED)
    query = request.GET.get("q", "").strip()
    technology = request.GET.get("technology", request.GET.get("tech", "")).strip()
    project_type = request.GET.get("type", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    status = request.GET.get("status", "").strip()
    ordering = request.GET.get("ordering", "recent")
    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(short_description__icontains=query) | Q(description__icontains=query) | Q(technologies__icontains=query))
    if technology:
        projects = projects.filter(technologies__icontains=technology)
    if project_type:
        projects = projects.filter(project_type=project_type)
    if difficulty:
        projects = projects.filter(difficulty=difficulty)
    if status:
        projects = projects.filter(status=status)
    try:
        page = max(int(request.GET.get("page", 1)), 1)
        page_size = min(max(int(request.GET.get("page_size", 12)), 1), 50)
    except ValueError:
        return JsonResponse({"error": "page and page_size must be integers."}, status=400)
    ordering_map = {"recent": "-published_at", "title": "title", "team_capacity": "-team_capacity"}
    projects = projects.order_by(ordering_map.get(ordering, "-published_at"), "title")
    count = projects.count()
    start = (page - 1) * page_size
    return JsonResponse({
        "count": count,
        "page": page,
        "page_size": page_size,
        "has_next": start + page_size < count,
        "results": [_serialize_project(project, request.user) for project in projects[start:start + page_size]],
    })


def _project_detail_for_request(request, slug):
    project = get_object_or_404(Project.objects.select_related("owner", "owner__profile").prefetch_related("roles"), slug=slug)
    if project.workflow_status != Project.WorkflowStatus.PUBLISHED and project.owner_id != getattr(request.user, "id", None):
        return None
    return project


@csrf_exempt
def project_detail_api(request, slug):
    project = _project_detail_for_request(request, slug)
    if project is None:
        return JsonResponse({"error": "Project not found."}, status=404)
    if request.method == "GET":
        return JsonResponse({"project": _serialize_project(project, request.user)})
    if request.method != "PATCH":
        return JsonResponse({"error": "GET or PATCH required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    if project.owner_id != request.user.id:
        return JsonResponse({"error": "Only the project owner can update this project."}, status=403)
    data = _parse_json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    data = _normalized_project_data(data)
    error = _project_payload_error(data)
    if error:
        return JsonResponse({"error": error}, status=400)
    editable_fields = {"title", "short_description", "description", "repository_url", "project_type", "difficulty", "status", "team_capacity", "technologies"}
    for field in editable_fields.intersection(data):
        value = data[field]
        if field in {"title", "short_description", "description", "repository_url"}:
            value = str(value).strip()
        elif field == "team_capacity":
            value = int(value)
        elif field == "technologies":
            value = [item.strip() for item in value]
        setattr(project, field, value)
    if "title" in data:
        project.slug = _unique_project_slug(project.title, project)
    project.save()
    if "roles" in data:
        _replace_roles(project, data["roles"])
    project = Project.objects.select_related("owner", "owner__profile").prefetch_related("roles").get(pk=project.pk)
    if editable_fields.intersection(data) or "roles" in data:
        _notify_project_members(
            project,
            Notification.NotificationType.PROJECT_UPDATE,
            f"{project.title} was updated",
            f"{request.user.get_full_name() or request.user.username} shared updates to {project.title}.",
            actor=request.user,
        )
    return JsonResponse({"message": "Project updated successfully.", "project": _serialize_project(project, request.user)})


def _project_workflow_api(request, slug, workflow_status, action):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    auth_error = _require_authenticated_user(request)
    if auth_error:
        return auth_error
    project = get_object_or_404(Project.objects.select_related("owner").prefetch_related("roles"), slug=slug)
    if project.owner_id != request.user.id:
        return JsonResponse({"error": f"Only the project owner can {action} this project."}, status=403)
    project.workflow_status = workflow_status
    if workflow_status == Project.WorkflowStatus.PUBLISHED and project.published_at is None:
        project.published_at = timezone.now()
    project.save(update_fields=["workflow_status", "published_at", "updated_at"])
    if workflow_status == Project.WorkflowStatus.PUBLISHED:
        _record_activity(ActivityEvent.EventType.PROJECT_PUBLISHED, actor=request.user, project=project)
        _notify_project_members(
            project,
            Notification.NotificationType.PROJECT_UPDATE,
            f"{project.title} is now published",
            f"{request.user.get_full_name() or request.user.username} published {project.title}.",
            actor=request.user,
        )
    return JsonResponse({"message": f"Project {action} successfully.", "project": _serialize_project(project, request.user)})


@csrf_exempt
def publish_project_api(request, slug):
    return _project_workflow_api(request, slug, Project.WorkflowStatus.PUBLISHED, "published")


@csrf_exempt
def archive_project_api(request, slug):
    return _project_workflow_api(request, slug, Project.WorkflowStatus.ARCHIVED, "archived")
