
import json
from uuid import uuid4

from django.core.paginator import Paginator
from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from .forms import ComplaintForm
from .models import Complaint, ComplaintMedia, StatusHistory


def error(message, status=400):
    return JsonResponse(
        {"errors": {"__all__": [message]}}, status=status
    )


def serialize(complaint, detail=False):
    data = {
        "id": complaint.pk,
        "description": complaint.description,
        "category": complaint.category,
        "status": complaint.status,
        "priority": complaint.priority,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "created_at": complaint.created_at.isoformat(),
    }
    if detail:
        data["history"] = [
            {
                "status": entry.status,
                "note": entry.note,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in complaint.history.order_by("created_at", "id")
        ]
        data["media"] = [
            {
                "id": media.pk,
                "url": f"/api/complaints/media/{media.pk}/",
            }
            for media in complaint.media.all()
        ]
    return data


@require_GET
def csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_http_methods(["GET", "POST"])
def complaints(request):
    if not request.user.is_authenticated:
        return error("Not authenticated.", 401)

    if request.method == "GET":
        queryset = Complaint.objects.filter(reporter=request.user)

        if request.GET.get("scope") == "officer":
            if not request.user.is_staff:
                return error("Officer access required.", 403)
            queryset = Complaint.objects.all()

        for field in ("status", "category"):
            value = request.GET.get(field)
            if value:
                queryset = queryset.filter(**{field: value})

        page = Paginator(queryset, 20).get_page(request.GET.get("page", 1))
        return JsonResponse({
            "results": [serialize(item) for item in page],
            "page": page.number,
            "pages": page.paginator.num_pages,
            "count": page.paginator.count,
        })

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except (ValueError, UnicodeDecodeError):
            return error("Invalid JSON.")
        if not isinstance(data, dict):
            return error("Expected a JSON object.")
    elif request.content_type == "multipart/form-data":
        data = request.POST.copy()
    else:
        return error("Use JSON or multipart form data.", 415)

    if not data.get("category"):
        data["category"] = "other"

    form = ComplaintForm(data, request.FILES)
    if not form.is_valid():
        return JsonResponse({
            "errors": {
                key: [str(message) for message in messages]
                for key, messages in form.errors.items()
            }
        }, status=400)

    media = None
    try:
        with transaction.atomic():
            complaint = form.save(commit=False)
            complaint.reporter = request.user
            complaint.save()

            StatusHistory.objects.create(
                complaint=complaint,
                status="submitted",
                changed_by=request.user,
                note="Complaint submitted.",
            )

            photo = form.cleaned_data.get("photo")
            if photo:
                extension = {
                    "JPEG": ".jpg",
                    "PNG": ".png",
                    "WEBP": ".webp",
                }[photo.image.format]
                photo.name = uuid4().hex + extension
                photo.seek(0)
                media = ComplaintMedia(complaint=complaint, file=photo)
                media.save()
    except Exception:
        if media and media.file.name:
            media.file.delete(save=False)
        raise

    return JsonResponse(serialize(complaint, detail=True), status=201)


@require_GET
def complaint_detail(request, pk):
    if not request.user.is_authenticated:
        return error("Not authenticated.", 401)

    queryset = Complaint.objects.all()
    if not request.user.is_staff:
        queryset = queryset.filter(reporter=request.user)

    complaint = get_object_or_404(queryset, pk=pk)
    return JsonResponse(serialize(complaint, detail=True))


@require_GET
def complaint_media(request, pk):
    if not request.user.is_authenticated:
        return error("Not authenticated.", 401)

    queryset = ComplaintMedia.objects.all()
    if not request.user.is_staff:
        queryset = queryset.filter(complaint__reporter=request.user)

    media = get_object_or_404(queryset, pk=pk)
    try:
        response = FileResponse(media.file.open("rb"))
    except FileNotFoundError:
        return error("Photo not found.", 404)

    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


NEXT_STATUS = {
    "submitted": "verified",
    "verified": "assigned",
    "assigned": "in_progress",
    "in_progress": "resolved",
}


@require_http_methods(["PATCH"])
def update_status(request, pk):
    if not request.user.is_authenticated:
        return error("Not authenticated.", 401)
    if not request.user.is_active or not request.user.is_staff:
        return error("Officer access required.", 403)

    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return error("Invalid JSON.")

    if not isinstance(data, dict):
        return error("Expected a JSON object.")

    expected = data.get("expected_status")
    target = data.get("status")
    note = data.get("note", "")

    if not isinstance(expected, str) or not isinstance(target, str):
        return error("Current and next status are required.")
    if NEXT_STATUS.get(expected) != target:
        return error("This status transition is not allowed.")
    if not isinstance(note, str) or len(note) > 1000:
        return error("Note must be text, at most 1000 characters.")

    with transaction.atomic():
        get_object_or_404(Complaint, pk=pk)

        updated = Complaint.objects.filter(
            pk=pk,
            status=expected,
        ).update(
            status=target,
            updated_at=timezone.now(),
        )

        if not updated:
            return error(
                "Status changed elsewhere. Refresh and try again.",
                409,
            )

        StatusHistory.objects.create(
            complaint_id=pk,
            status=target,
            changed_by=request.user,
            note=note.strip(),
        )
        complaint = Complaint.objects.get(pk=pk)

    return JsonResponse(serialize(complaint, detail=True))
