from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import Complaint


class ComplaintTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="citizen@example.com",
            password="River!Window49Cloud",
            full_name="Test Citizen",
            age=22,
        )
        self.client.force_login(self.user)

    def test_creation_sets_owner_and_initial_history(self):
        response = self.client.post(
            "/api/complaints/",
            data={
                "description": "Pothole near school",
                "category": "pothole",
                "status": "resolved",
                "reporter": 999,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        complaint = Complaint.objects.get()
        self.assertEqual(complaint.reporter, self.user)
        self.assertEqual(complaint.status, "submitted")
        self.assertEqual(complaint.history.get().status, "submitted")

    def test_invalid_input_creates_nothing(self):
        for data in (
            {"description": ""},
            {"description": "Road issue", "category": "invalid"},
            {"description": "Road issue", "latitude": 18.52},
        ):
            with self.subTest(data=data):
                response = self.client.post(
                    "/api/complaints/", data=data,
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)
        self.assertFalse(Complaint.objects.exists())

    def test_authentication_required(self):
        self.client.logout()
        response = self.client.post(
            "/api/complaints/",
            data={"description": "Road issue"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_csrf_required_and_valid_token_works(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        payload = {"description": "Road issue"}

        response = client.post(
            "/api/complaints/", data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        token = client.get("/api/complaints/csrf/").json()["csrfToken"]
        response = client.post(
            "/api/complaints/", data=payload,
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)