import json
from datetime import timedelta
from uuid import uuid4
from django.db import transaction
from django.db.models import Count, Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .forms import ComplaintForm
from .models import Complaint, ComplaintMedia, Feedback, Notification, StatusHistory


def reply(data, status=200):
    response = JsonResponse(data, status=status)
    response["Cache-Control"] = "private, no-store"
    return response


@require_POST
def resolution_photo(request, pk):
    if not request.user.is_authenticated:
        return reply({"error": "Sign in first."}, 401)
    if not request.user.is_staff:
        return reply({"error": "Officer access required."}, 403)
    if not request.FILES.get("photo"):
        return reply({"error": "Choose a resolution photo."}, 400)
    form = ComplaintForm({"description": "Resolution evidence", "category": "other", "original_language": "en"}, request.FILES)
    if not form.is_valid():
        return reply({"error": "Choose a valid JPG, PNG or WebP up to 5 MB."}, 400)
    photo = form.cleaned_data["photo"]
    extension = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}[photo.image.format]
    media = None
    try:
        with transaction.atomic():
            complaint = get_object_or_404(Complaint.objects.select_for_update(), pk=pk)
            if complaint.status != "in_progress":
                return reply({"error": "Upload evidence only while work is in progress."}, 409)
            cycle = complaint.history.filter(status="in_progress").order_by("-created_at", "-id").first()
            if cycle is None:
                return reply({"error": "The in-progress history entry is missing."}, 409)
            if complaint.media.filter(kind="resolution", created_at__gte=cycle.created_at).count() >= 5:
                return reply({"error": "This work cycle already has five evidence photos."}, 400)
            media = ComplaintMedia(complaint=complaint, kind="resolution")
            media.file.save(f"{uuid4().hex}.{extension}", photo, save=False)
            media.save()
    except Exception:
        if media and media.file.name:
            media.file.delete(save=False)
        raise
    return reply({"id": media.pk, "url": f"/api/complaints/media/{media.pk}/", "kind": "resolution"}, 201)


@require_http_methods(["GET", "POST"])
def feedback(request, pk):
    if not request.user.is_authenticated:
        return reply({"error": "Sign in first."}, 401)
    complaint = get_object_or_404(Complaint, pk=pk, reporter=request.user)
    if request.method == "GET":
        row = Feedback.objects.filter(complaint=complaint).first()
        return reply({"feedback": {"rating": row.rating, "comment": row.comment} if row else None})
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError()
        rating, comment = data.get("rating"), data.get("comment", "")
        if type(rating) is not int or not 1 <= rating <= 5 or not isinstance(comment, str) or len(comment) > 1000:
            raise ValueError()
    except (ValueError, UnicodeDecodeError):
        return reply({"error": "Use a rating from 1 to 5 and a comment up to 1000 characters."}, 400)
    with transaction.atomic():
        complaint = get_object_or_404(Complaint.objects.select_for_update(), pk=pk, reporter=request.user)
        if complaint.status != "resolved":
            return reply({"error": "Only resolved complaints accept feedback."}, 409)
        Feedback.objects.update_or_create(complaint=complaint, defaults={"rating": rating, "comment": comment.strip()})
    return reply({"feedback": {"rating": rating, "comment": comment.strip()}})


@require_POST
def reopen(request, pk):
    if not request.user.is_authenticated:
        return reply({"error": "Sign in first."}, 401)
    try:
        data = json.loads(request.body)
        reason = data.get("reason") if isinstance(data, dict) else None
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 1000:
            raise ValueError()
    except (ValueError, UnicodeDecodeError):
        return reply({"error": "Explain why the issue remains (1–1000 characters)."}, 400)
    with transaction.atomic():
        complaint = get_object_or_404(Complaint.objects.select_for_update(), pk=pk, reporter=request.user)
        changed = Complaint.objects.filter(pk=pk, status="resolved").update(
            status="verified", assigned_worker=None, updated_at=timezone.now())
        if not changed:
            return reply({"error": "Only a currently resolved complaint can be reopened."}, 409)
        StatusHistory.objects.create(complaint=complaint, status="verified", changed_by=request.user,
                                     note="Reopened by citizen: " + reason.strip())
        Notification.objects.create(recipient=request.user, complaint=complaint,
                                     message=f"Complaint #{pk} reopened for reassignment.")
    return reply({"id": pk, "status": "verified"})


@require_GET
def analytics(request):
    if not request.user.is_authenticated:
        return reply({"error": "Sign in first."}, 401)
    if not request.user.is_staff:
        return reply({"error": "Officer access required."}, 403)
    all_reports = Complaint.objects.all()
    opened = all_reports.exclude(status="resolved")
    resolved = all_reports.filter(status="resolved").annotate(
        resolved_at=Max("history__created_at", filter=Q(history__status="resolved")))
    durations = [(row.resolved_at - row.created_at).total_seconds() / 3600
                 for row in resolved if row.resolved_at]
    return reply({
        "open": opened.count(), "resolved": resolved.count(),
        "overdue": opened.filter(created_at__lt=timezone.now() - timedelta(hours=72)).count(),
        "sla_hours": 72,
        "average_resolution_hours": round(sum(durations) / len(durations), 1) if durations else None,
        "by_category": list(opened.order_by().values("category").annotate(count=Count("id")).order_by("category")),
        "by_ward": list(opened.order_by().values("ward__name").annotate(count=Count("id")).order_by("ward__name")),
    })
