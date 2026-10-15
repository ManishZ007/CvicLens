
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods

from .models import Notification


@require_GET
def notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Sign in first."}, status=401)

    own = Notification.objects.filter(recipient=request.user)
    page = Paginator(own, 20).get_page(request.GET.get("page", 1))

    response = JsonResponse({
        "unread_count": own.filter(is_read=False).count(),
        "page": page.number,
        "pages": page.paginator.num_pages,
        "results": [
            {
                "id": row.pk,
                "complaint_id": row.complaint_id,
                "message": row.message,
                "is_read": row.is_read,
                "created_at": row.created_at.isoformat(),
            }
            for row in page
        ],
    })
    response["Cache-Control"] = "private, no-store"
    return response


@require_http_methods(["PATCH"])
def mark_read(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Sign in first."}, status=401)

    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user,
    )
    notification.is_read = True
    notification.save(update_fields=["is_read"])

    return JsonResponse({
        "id": notification.pk,
        "is_read": True,
    })
