
from django.test import Client, TestCase

from users.models import User
from .models import Complaint, Notification


class NotificationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            full_name="Owner",
            age=22,
            password="test-password",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            full_name="Other",
            age=22,
            password="test-password",
        )
        self.officer = User.objects.create_user(
            email="officer@example.com",
            full_name="Officer",
            age=22,
            password="test-password",
            is_staff=True,
        )
        self.complaint = Complaint.objects.create(
            reporter=self.owner,
            description="Broken road",
        )

    def test_transition_creates_one_notification_and_conflict_creates_none(self):
        self.client.force_login(self.officer)
        url = f"/api/complaints/{self.complaint.pk}/status/"
        data = {
            "expected_status": "submitted",
            "status": "verified",
        }

        first = self.client.patch(
            url,
            data,
            content_type="application/json",
        )
        second = self.client.patch(
            url,
            data,
            content_type="application/json",
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(
            Notification.objects.filter(recipient=self.owner).count(),
            1,
        )

    def test_private_list_and_csrf_protected_read(self):
        row = Notification.objects.create(
            recipient=self.owner,
            complaint=self.complaint,
            message="Updated",
        )

        self.client.force_login(self.other)
        response = self.client.get("/api/complaints/notifications/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

        url = f"/api/complaints/notifications/{row.pk}/read/"
        self.assertEqual(self.client.patch(url).status_code, 404)

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)

        self.assertEqual(client.patch(url).status_code, 403)

        token = client.get("/api/complaints/csrf/").json()["csrfToken"]
        response = client.patch(url, HTTP_X_CSRFTOKEN=token)

        self.assertEqual(response.status_code, 200)

        row.refresh_from_db()
        self.assertTrue(row.is_read)
