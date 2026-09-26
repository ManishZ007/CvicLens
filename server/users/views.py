import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import RegistrationForm


@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"errors": {"__all__": ["Invalid JSON."]}}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"errors": {"__all__": ["Invalid request body."]}}, status=400)

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    errors = {}
    if not email:
        errors["email"] = ["Email is required."]
    if not password:
        errors["password"] = ["Password is required."]
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    # USERNAME_FIELD is email, so Django's backend treats "username" as the email
    user = authenticate(request, username=email, password=password)
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
        return JsonResponse({"errors": {"__all__": ["Invalid JSON."]}}, status=400)

    if not isinstance(data, dict):
        return JsonResponse(
            {"errors": {"__all__": ["Invalid request body."]}},
            status=400,
        )

    form = RegistrationForm(data=data)

    if not form.is_valid():
        errors = {
            field: [str(error) for error in error_list]
            for field, error_list in form.errors.items()
        }
        return JsonResponse({"errors": errors}, status=400)

    user = form.save(commit=False)
    user.set_password(form.cleaned_data["password"])
    user.save()

    return JsonResponse(
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
        },
        status=201,
    )