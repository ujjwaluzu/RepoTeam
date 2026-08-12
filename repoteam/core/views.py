import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from .models import Profile, Project, ProjectRole

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
    data = {
        "id": user.id, "username": user.username, "display_name": profile.display_name or user.username,
        "title": profile.title, "bio": profile.bio, "location": profile.location, "skills": profile.skills,
        "experience": profile.experience, "availability": profile.availability, "github_url": profile.github_url,
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
        profiles = profiles.filter(availability=availability)
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


def _serialize_project(project, request_user=None):
    profile, _ = Profile.objects.get_or_create(user=project.owner)
    owner_name = profile.display_name or project.owner.username
    open_roles = [role for role in project.roles.all() if role.status == ProjectRole.Status.OPEN]
    is_owner = bool(request_user and request_user.is_authenticated and request_user.pk == project.owner_id)
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
        "contributors": 1,
        "technologies": project.technologies,
        "stack": project.technologies,
        "workflow_status": project.workflow_status,
        "roles": [_serialize_role(role) for role in open_roles],
        "owner": {"username": project.owner.username, "display_name": owner_name},
        "owner_name": owner_name,
        "owner_username": project.owner.username,
        "is_owner": is_owner,
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
    return JsonResponse({"message": f"Project {action} successfully.", "project": _serialize_project(project, request.user)})


@csrf_exempt
def publish_project_api(request, slug):
    return _project_workflow_api(request, slug, Project.WorkflowStatus.PUBLISHED, "published")


@csrf_exempt
def archive_project_api(request, slug):
    return _project_workflow_api(request, slug, Project.WorkflowStatus.ARCHIVED, "archived")
