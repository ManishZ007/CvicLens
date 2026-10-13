# Day 7 — Naman: persisted status notifications

Append to `server/complaints/models.py`:

```python
class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
```

Create `server/complaints/notification_views.py`:

```python
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
        "results": [{
            "id": row.pk, "complaint_id": row.complaint_id,
            "message": row.message, "is_read": row.is_read,
            "created_at": row.created_at.isoformat(),
        } for row in page],
    })
    response["Cache-Control"] = "private, no-store"
    return response


@require_http_methods(["PATCH"])
def mark_read(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Sign in first."}, status=401)
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return JsonResponse({"id": notification.pk, "is_read": True})
```

In `server/complaints/urls.py`, add this import and these entries **inside the existing urlpatterns**. Keep all current routes:

```python
from . import notification_views

# Inside urlpatterns:
path("notifications/", notification_views.notifications, name="notifications"),
path("notifications/<int:pk>/read/", notification_views.mark_read, name="notification-read"),
```

In `server/complaints/views.py`, add `Notification` to the `.models` import.
Inside `update_status`, insert this **after `StatusHistory.objects.create(...)` and still inside `transaction.atomic()`**:

```python
        Notification.objects.create(
            recipient_id=complaint.reporter_id,
            complaint_id=pk,
            message=f"Complaint #{pk} is now {target.replace('_', ' ')}.",
        )
```

Create `server/complaints/test_notifications.py`:

```python
from django.test import Client, TestCase
from users.models import User
from .models import Complaint, Notification


class NotificationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com", full_name="Owner", age=22, password="test-password")
        self.other = User.objects.create_user(
            email="other@example.com", full_name="Other", age=22, password="test-password")
        self.officer = User.objects.create_user(
            email="officer@example.com", full_name="Officer", age=22,
            password="test-password", is_staff=True)
        self.complaint = Complaint.objects.create(reporter=self.owner, description="Broken road")

    def test_transition_creates_one_notification_and_conflict_creates_none(self):
        self.client.force_login(self.officer)
        url = f"/api/complaints/{self.complaint.pk}/status/"
        data = {"expected_status": "submitted", "status": "verified"}
        self.assertEqual(self.client.patch(url, data, content_type="application/json").status_code, 200)
        self.assertEqual(self.client.patch(url, data, content_type="application/json").status_code, 409)
        self.assertEqual(Notification.objects.filter(recipient=self.owner).count(), 1)

    def test_private_list_and_csrf_protected_read(self):
        row = Notification.objects.create(recipient=self.owner, complaint=self.complaint, message="Updated")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get("/api/complaints/notifications/").json()["results"], [])
        url = f"/api/complaints/notifications/{row.pk}/read/"
        self.assertEqual(self.client.patch(url).status_code, 404)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.patch(url).status_code, 403)
        token = client.get("/api/complaints/csrf/").json()["csrfToken"]
        self.assertEqual(client.patch(url, HTTP_X_CSRFTOKEN=token).status_code, 200)
        row.refresh_from_db()
        self.assertTrue(row.is_read)
```

Run from `server`, and **commit the generated migration too**:

```powershell
.\venv\Scripts\python.exe manage.py makemigrations complaints
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py test
```

Notifications cover future successful status changes; they do not backfill old history.
Do not add `csrf_exempt` to these endpoints.

Commit: `feat(notifications): persist private complaint status alerts`
