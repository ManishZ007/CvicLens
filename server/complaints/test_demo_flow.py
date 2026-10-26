"""Repeat the public API demo with real sessions and CSRF enforcement."""
from io import BytesIO, StringIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from users.models import User


class DemoFlowTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        media = override_settings(MEDIA_ROOT=self.directory.name)
        media.enable()
        self.addCleanup(media.disable)
        call_command("seed_routing", stdout=StringIO())
        User.objects.create_user(email="demo-officer@example.com", password="Demo!Officer846",
                                 full_name="Demo Officer", age=25, is_staff=True)
        self.officer = self.sign_in("demo-officer@example.com", "Demo!Officer846")

    def sign_in(self, email, password):
        client = Client(enforce_csrf_checks=True)
        client.defaults["HTTP_X_CSRFTOKEN"] = client.get("/api/complaints/csrf/").json()["csrfToken"]
        response = client.post("/api/users/login/", {"email": email, "password": password},
                               content_type="application/json")
        self.assertEqual(response.status_code, 200)
        client.defaults["HTTP_X_CSRFTOKEN"] = client.get("/api/complaints/csrf/").json()["csrfToken"]
        return client

    def photo(self):
        image = BytesIO()
        Image.new("RGB", (8, 8), "blue").save(image, "PNG")
        return SimpleUploadedFile("demo.png", image.getvalue(), content_type="image/png")

    def transition(self, pk, current, target, worker_id=None):
        response = self.officer.patch(f"/api/complaints/{pk}/status/", {
            "expected_status": current, "status": target,
            "worker_id": worker_id, "note": "Work checked and repaired.",
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)

    def test_two_complete_citizen_officer_flows(self):
        for index in range(2):
            with self.subTest(run=index + 1):
                email = f"demo-citizen-{index}@example.com"
                registration = self.client.post("/api/users/register/", {
                    "email": email, "password": "Demo!Citizen846", "full_name": "Demo Citizen", "age": 22,
                }, content_type="application/json")
                self.assertEqual(registration.status_code, 201)
                citizen = self.sign_in(email, "Demo!Citizen846")
                description = "Large pothole near school causing accidents"
                analysis = citizen.post("/api/ai/classify/", {"text": description, "language": "en"},
                                        content_type="application/json")
                self.assertEqual(analysis.status_code, 200)
                report = citizen.post("/api/complaints/", {
                    "description": description, "category": "pothole", "original_language": "en",
                    "analysis_token": analysis.json()["analysis_token"], "latitude": 18.52,
                    "longitude": 73.82, "photo": self.photo(),
                })
                self.assertEqual(report.status_code, 201, report.content)
                detail = report.json()
                pk = detail["id"]
                self.assertTrue(detail["ai_analysis"])
                self.assertEqual(detail["routing_mode"], "demo")
                options = self.officer.get("/api/complaints/routing-options/").json()
                worker = next(item for item in options["workers"]
                              if item["department_id"] == detail["department_id"] and item["ward_id"] == detail["ward_id"])
                self.transition(pk, "submitted", "verified")
                self.transition(pk, "verified", "assigned", worker["id"])
                self.transition(pk, "assigned", "in_progress")
                evidence = self.officer.post(f"/api/complaints/{pk}/resolution-photo/", {"photo": self.photo()})
                self.assertEqual(evidence.status_code, 201)
                self.transition(pk, "in_progress", "resolved")
                updated = citizen.get(f"/api/complaints/{pk}/").json()
                self.assertEqual(updated["status"], "resolved")
                self.assertEqual({item["kind"] for item in updated["media"]}, {"report", "resolution"})
                download = citizen.get(evidence.json()["url"])
                self.assertEqual(download.status_code, 200)
                download.close()
                inbox = citizen.get("/api/complaints/notifications/").json()
                self.assertEqual(inbox["unread_count"], 4)
                self.assertEqual(citizen.patch(f"/api/complaints/notifications/{inbox['results'][0]['id']}/read/").status_code, 200)
                self.assertEqual(citizen.get("/api/complaints/notifications/").json()["unread_count"], 3)
                feedback = citizen.post(f"/api/complaints/{pk}/feedback/", {"rating": 5, "comment": "Fixed"}, content_type="application/json")
                self.assertEqual(feedback.status_code, 200)
                self.assertEqual(citizen.get(f"/api/complaints/{pk}/feedback/").json()["feedback"]["rating"], 5)
                reopened = citizen.post(f"/api/complaints/{pk}/reopen/", {"reason": "Damage returned"}, content_type="application/json")
                self.assertEqual(reopened.status_code, 200)
                self.transition(pk, "verified", "assigned", worker["id"])
                self.transition(pk, "assigned", "in_progress")
                self.assertEqual(self.officer.post(f"/api/complaints/{pk}/resolution-photo/", {"photo": self.photo()}).status_code, 201)
                self.transition(pk, "in_progress", "resolved")
                self.assertEqual(self.officer.get("/api/complaints/analytics/").json()["resolved"], index + 1)
