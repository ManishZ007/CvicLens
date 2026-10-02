import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import User


@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"errors": {"__all__": ["Invalid JSON."]}},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"errors": {"__all__": ["Invalid request body."]}},
            status=400,
        )

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    errors = {}

    if not email:
        errors["email"] = ["Email is required."]

    if not password:
        errors["password"] = ["Password is required."]

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    user = authenticate(
        request,
        username=email,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {"errors": {"__all__": ["Invalid email or password."]}},
            status=400,
        )

    login(request, user)

    return JsonResponse(
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
        }
    )


@csrf_exempt
@require_POST
def register_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"errors": {"__all__": ["Invalid JSON."]}},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"errors": {"__all__": ["Invalid request body."]}},
            status=400,
        )

    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    errors = {}

    if not full_name:
        errors["full_name"] = ["Full name is required."]
    elif len(full_name) > 150:
        errors["full_name"] = [
            "Full name must be 150 characters or fewer."
        ]

    if not email:
        errors["email"] = ["Email is required."]
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = ["Enter a valid email address."]
        else:
            if User.objects.filter(email=email).exists():
                errors["email"] = [
                    "An account with this email already exists."
                ]

    age = data.get("age")

    if age is None or age == "":
        errors["age"] = ["Age is required."]
    else:
        try:
            age = int(age)
        except (TypeError, ValueError):
            errors["age"] = ["Age must be a number."]
        else:
            if age < 13 or age > 120:
                errors["age"] = [
                    "Age must be between 13 and 120."
                ]

    if not password:
        errors["password"] = ["Password is required."]

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    user_for_validation = User(
        full_name=full_name,
        email=email,
        age=age,
    )

    try:
        validate_password(password, user=user_for_validation)
    except ValidationError as exc:
        errors["password"] = exc.messages

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    try:
        user = User(
            full_name=full_name,
            email=email,
            age=age,
        )

        user.set_password(password)
        user.save()

    except IntegrityError:
        return JsonResponse(
            {
                "errors": {
                    "email": [
                        "An account with this email already exists."
                    ]
                }
            },
            status=400,
        )

    return JsonResponse(
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "age": user.age,
        },
        status=201,
    )


@require_GET
def current_user_view(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"errors": {"__all__": ["Not authenticated."]}},
            status=401,
        )

    user = request.user

    return JsonResponse(
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "age": user.age,
        }
    )


@csrf_exempt
@require_POST
def logout_view(request):
    logout(request)

    return JsonResponse(
        {"message": "Logged out successfully."}
    )