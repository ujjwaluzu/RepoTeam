import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )


def _parse_json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
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
    return JsonResponse(
        {
            "message": "Logged in successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )


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
    password = data.get("password", "")
    confirmation = data.get("confirmation", "")

    if password != confirmation:
        return JsonResponse({"error": "Passwords must match."}, status=400)

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
    except IntegrityError:
        return JsonResponse({"error": "Username already taken."}, status=400)

    login(request, user)
    return JsonResponse(
        {
            "message": "Account created successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        },
        status=201,
    )
