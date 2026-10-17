import io
from tempfile import TemporaryDirectory
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from users.models import User
from .models import Complaint, ComplaintMedia, Feedback, StatusHistory


class CompletionTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.directory.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.owner = User.objects.create_user(email="done-owner@example.com", full_name="Owner", age=22, password="test-password")
        self.other = User.objects.create_user(email="done-other@example.com", full_name="Other", age=22, password="test-password")
        self.officer = User.objects.create_user(email="done-officer@example.com", full_name="Officer", age=22, password="test-password", is_staff=True)
        self.report = Complaint.objects.create(reporter=self.owner, description="Road damage", status="in_progress")
        StatusHistory.objects.create(complaint=self.report, status="in_progress", changed_by=self.officer)
        self.root = f"/api/complaints/{self.report.pk}/"
        self.client.force_login(self.officer)

    def upload(self):
        output = io.BytesIO()
        Image.new("RGB", (4, 4), "blue").save(output, "PNG")
        return self.client.post(self.root + "resolution-photo/", {
            "photo": SimpleUploadedFile("proof.png", output.getvalue(), content_type="image/png")})

    def resolve(self, note="Road repaired"):
        return self.client.patch(self.root + "status/", {
            "expected_status": "in_progress", "status": "resolved", "note": note}, content_type="application/json")

    def test_evidence_required_validated_and_private(self):
        self.assertEqual(self.resolve().status_code, 400)
        invalid = self.client.post(self.root + "resolution-photo/", {
            "photo": SimpleUploadedFile("bad.png", b"not an image", content_type="image/png")})
        self.assertEqual(invalid.status_code, 400)
        self.assertFalse(ComplaintMedia.objects.exists())
        uploaded = self.upload()
        self.assertEqual(uploaded.status_code, 201)
        self.assertEqual(self.resolve(note=" ").status_code, 400)
        self.assertEqual(self.resolve().status_code, 200)
        self.assertEqual(self.resolve().status_code, 409)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(uploaded.json()["url"]).status_code, 404)
        self.assertEqual(self.upload().status_code, 403)
        self.client.force_login(self.owner)
        download = self.client.get(uploaded.json()["url"])
        self.assertEqual(download.status_code, 200)
        download.close()

    def test_feedback_validated_persisted_and_private(self):
        self.client.force_login(self.owner)
        url = self.root + "feedback/"
        self.assertEqual(self.client.post(url, {"rating": 5}, content_type="application/json").status_code, 409)
        Complaint.objects.filter(pk=self.report.pk).update(status="resolved")
        for rating in (0, 6, True, "5"):
            self.assertEqual(self.client.post(url, {"rating": rating}, content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(url, {"rating": 4, "comment": "Fixed"}, content_type="application/json").status_code, 200)
        self.assertEqual(self.client.get(url).json()["feedback"]["rating"], 4)
        self.assertEqual(Feedback.objects.count(), 1)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_reopen_preserves_history_but_requires_new_cycle_evidence(self):
        self.upload()
        self.assertEqual(self.resolve().status_code, 200)
        self.client.force_login(self.owner)
        url = self.root + "reopen/"
        self.assertEqual(self.client.post(url, {"reason": "Still broken"}, content_type="application/json").status_code, 200)
        self.assertEqual(self.client.post(url, {"reason": "Still broken"}, content_type="application/json").status_code, 409)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "verified")
        self.assertIsNone(self.report.assigned_worker)
        self.assertTrue(self.report.history.filter(status="resolved").exists())
        Complaint.objects.filter(pk=self.report.pk).update(status="in_progress")
        StatusHistory.objects.create(complaint=self.report, status="in_progress", changed_by=self.officer)
        self.client.force_login(self.officer)
        self.assertEqual(self.resolve().status_code, 400)
        self.assertEqual(self.upload().status_code, 201)
        self.assertEqual(self.resolve().status_code, 200)

    def test_csrf_and_officer_only_analytics(self):
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.owner)
        self.assertEqual(secure.post(self.root + "reopen/", {"reason": "Still broken"}, content_type="application/json").status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/api/complaints/analytics/").status_code, 403)
        self.client.force_login(self.officer)
        data = self.client.get("/api/complaints/analytics/").json()
        self.assertEqual(data["open"], 1)
        self.assertEqual(data["resolved"], 0)
        self.assertIsNone(data["average_resolution_hours"])
