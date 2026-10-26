import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Complaint, Department, Ward, Worker, StatusHistory


@require_http_methods(["PATCH"])
def update_routing(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Sign in first."}, status=401)
    if not request.user.is_staff:
        return JsonResponse({"error": "Officer access required."}, status=403)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError()
        department, ward = data.get("department_id"), data.get("ward_id")
        note, expected = data.get("note"), data.get("expected_status")
        if (type(department) is not int or type(ward) is not int or
                expected not in ("submitted", "verified") or not isinstance(note, str) or
                not note.strip() or len(note) > 1000):
            raise ValueError()
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Select department and ward, and provide a routing note."}, status=400)
    if not Department.objects.filter(pk=department).exists() or not Ward.objects.filter(pk=ward).exists():
        return JsonResponse({"error": "Selected department or ward is unavailable."}, status=400)
    if not Worker.objects.filter(department_id=department, ward_id=ward, active=True).exists():
        return JsonResponse({"error": "No active worker covers this department and ward."}, status=400)
    with transaction.atomic():
        complaint = get_object_or_404(Complaint, pk=pk)
        changed = Complaint.objects.filter(pk=pk, status=expected, assigned_worker__isnull=True).update(
            department_id=department, ward_id=ward, routing_mode="manual", updated_at=timezone.now())
        if not changed:
            return JsonResponse({"error": "Routing can only change before assignment. Refresh first."}, status=409)
        StatusHistory.objects.create(complaint=complaint, status=expected, changed_by=request.user,
                                     note="Officer routing: " + note.strip())
    return JsonResponse({"id": pk, "routing_mode": "manual"})
