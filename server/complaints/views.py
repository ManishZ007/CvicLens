import json

from django.db import transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_POST

from .forms import ComplaintForm
from .models import StatusHistory


@require_GET
def csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
def create_complaint(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"errors": {"__all__": ["Not authenticated."]}}, status=401
        )

    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse(
            {"errors": {"__all__": ["Invalid JSON."]}}, status=400
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"errors": {"__all__": ["Expected a JSON object."]}}, status=400
        )

    data.setdefault("category", "other")
    if data["category"] == "":
        data["category"] = "other"

    form = ComplaintForm(data)
    if not form.is_valid():
        return JsonResponse({
            "errors": {
                field: [str(message) for message in messages]
                for field, messages in form.errors.items()
            }
        }, status=400)

    with transaction.atomic():
        complaint = form.save(commit=False)
        complaint.reporter = request.user
        complaint.save()
        StatusHistory.objects.create(
            complaint=complaint,
            status=complaint.status,
            changed_by=request.user,
            note="Complaint submitted.",
        )

    return JsonResponse({
        "id": complaint.pk,
        "description": complaint.description,
        "category": complaint.category,
        "status": complaint.status,
        "priority": complaint.priority,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "created_at": complaint.created_at.isoformat(),
    }, status=201)