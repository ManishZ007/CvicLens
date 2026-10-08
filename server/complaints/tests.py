from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import Complaint, Department, Ward, Worker


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
                "description": "Pothole with photo",
                "category": "pothole",
                "latitude": "18.52",
                "longitude": "73.85",
                "photo": SimpleUploadedFile(
                    "issue.png",
                    image.getvalue(),
                    content_type="image/png",
                ),
            })
            self.assertEqual(response.status_code, 201)
            media_url = response.json()["media"][0]["url"]
            response = self.client.get(media_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                b"".join(response.streaming_content),
                image.getvalue(),
            )
            response.close()
            self.client.force_login(self.other)
            self.assertEqual(self.client.get(media_url).status_code, 404)

    def test_fake_image_rejected_without_creating_report(self):
        self.client.force_login(self.owner)
        before = Complaint.objects.count()
        response = self.client.post("/api/complaints/", {
            "description": "Fake photo",
            "photo": SimpleUploadedFile(
                "fake.png",
                b"not an image",
                content_type="image/png",
            ),
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


class StatusUpdateTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.citizen = User.objects.create_user(
            email="status-citizen@example.com",
            password="Strong!Pass934",
            full_name="Citizen",
            age=22,
        )
        self.officer = User.objects.create_user(
            email="status-officer@example.com",
            password="Strong!Pass935",
            full_name="Officer",
            age=25,
            is_staff=True,
        )

        self.department = Department.objects.create(
            code="roads",
            name="Roads",
        )
        self.ward = Ward.objects.create(
            code="W01",
            name="Ward 01",
        )
        self.worker = Worker.objects.create(
            name="Test Worker",
            department=self.department,
            ward=self.ward,
            active=True,
        )

        self.report = Complaint.objects.create(
            reporter=self.citizen,
            description="Pothole",
            department=self.department,
            ward=self.ward,
        )
        self.url = f"/api/complaints/{self.report.pk}/status/"

    def update(self, expected, target, worker_id=None):
        data = {
            "expected_status": expected,
            "status": target,
            "note": "Checked by officer",
        }
        if worker_id is not None:
            data["worker_id"] = worker_id

        return self.client.patch(
            self.url,
            data=data,
            content_type="application/json",
        )

    def test_citizen_cannot_update(self):
        self.client.force_login(self.citizen)
        self.assertEqual(
            self.update("submitted", "verified").status_code,
            403,
        )

    def test_complete_lifecycle_and_history(self):
        self.client.force_login(self.officer)
        states = [
            "submitted",
            "verified",
            "assigned",
            "in_progress",
            "resolved",
        ]

        self.assertEqual(
            self.update("submitted", "verified").status_code,
            200,
        )

        self.assertEqual(
            self.update(
                "verified",
                "assigned",
                worker_id=self.worker.pk,
            ).status_code,
            200,
        )

        self.assertEqual(
            self.update("assigned", "in_progress").status_code,
            200,
        )

        self.assertEqual(
            self.update("in_progress", "resolved").status_code,
            200,
        )

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "resolved")
        self.assertEqual(self.report.assigned_worker, self.worker)
        self.assertEqual(self.report.history.count(), 4)

    def test_skipped_and_stale_updates_rejected(self):
        self.client.force_login(self.officer)

        self.assertEqual(
            self.update("submitted", "resolved").status_code,
            400,
        )

        self.assertEqual(
            self.update("submitted", "verified").status_code,
            200,
        )

        self.assertEqual(
            self.update("submitted", "verified").status_code,
            409,
        )

        self.assertEqual(self.report.history.count(), 1)

    def test_inactive_worker_rejected(self):
        self.client.force_login(self.officer)

        self.worker.active = False
        self.worker.save()

        self.assertEqual(
            self.update(
                "submitted",
                "verified",
            ).status_code,
            200,
        )

        self.assertEqual(
            self.update(
                "verified",
                "assigned",
                worker_id=self.worker.pk,
            ).status_code,
            400,
        )