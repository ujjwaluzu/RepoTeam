import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Profile

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
