
from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
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
                    "/api/complaints/",
                    data=data,
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
            "/api/complaints/",
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        token = client.get("/api/complaints/csrf/").json()["csrfToken"]
        response = client.post(
            "/api/complaints/",
            data=payload,
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)


class ComplaintReadTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="Strong!Pass934",
            full_name="Owner",
            age=22,
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="Strong!Pass935",
            full_name="Other",
            age=23,
        )
        self.report = Complaint.objects.create(
            reporter=self.owner,
            description="Pothole near school",
        )

    def test_other_citizen_cannot_read_report(self):
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.get(
                f"/api/complaints/{self.report.pk}/"
            ).status_code,
            404,
        )
        response = self.client.get("/api/complaints/")
        self.assertEqual(response.json()["count"], 0)

    def test_photo_upload_and_private_download(self):
        image = BytesIO()
        Image.new("RGB", (2, 2)).save(image, format="PNG")
        with TemporaryDirectory() as directory, self.settings(MEDIA_ROOT=directory):
            self.client.force_login(self.owner)
            response = self.client.post("/api/complaints/", {
                "description": "Pothole with photo", "category": "pothole",
                "latitude": "18.52", "longitude": "73.85",
                "photo": SimpleUploadedFile("issue.png", image.getvalue(), content_type="image/png"),
            })
            self.assertEqual(response.status_code, 201)
            media_url = response.json()["media"][0]["url"]
            response = self.client.get(media_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"".join(response.streaming_content), image.getvalue())
            response.close()
            self.client.force_login(self.other)
            self.assertEqual(self.client.get(media_url).status_code, 404)

    def test_fake_image_rejected_without_creating_report(self):
        self.client.force_login(self.owner)
        before = Complaint.objects.count()
        response = self.client.post("/api/complaints/", {
            "description": "Fake photo",
            "photo": SimpleUploadedFile("fake.png", b"not an image", content_type="image/png"),
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("photo", response.json()["errors"])
        self.assertEqual(Complaint.objects.count(), before)

    def test_officer_scope_requires_staff(self):
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.get(
                "/api/complaints/?scope=officer"
            ).status_code,
            403,
        )
        self.other.is_staff = True
        self.other.save()
        response = self.client.get("/api/complaints/?scope=officer")
        self.assertEqual(response.json()["count"], 1)
