from django.test import Client, TestCase
from users.models import User
from .models import Complaint, Department, Ward, Worker


class ManualRoutingTests(TestCase):
    def setUp(self):
        self.citizen = User.objects.create_user(email="routing-citizen@example.com", full_name="Citizen", age=22)
        self.officer = User.objects.create_user(email="routing-officer@example.com", full_name="Officer", age=22, is_staff=True)
        self.report = Complaint.objects.create(reporter=self.citizen, description="Issue outside demo bounds")
        self.department = Department.objects.create(code="roads", name="Roads")
        self.ward = Ward.objects.create(code="DEMO-A", name="Demo zone A")
        Worker.objects.create(name="Demo worker", department=self.department, ward=self.ward)
        self.url = f"/api/complaints/{self.report.pk}/routing/"
        self.data = {"department_id": self.department.pk, "ward_id": self.ward.pk,
                     "expected_status": "submitted", "note": "Demo reassignment"}

    def test_auth_and_csrf(self):
        self.assertEqual(self.client.patch(self.url, self.data, content_type="application/json").status_code, 401)
        self.client.force_login(self.citizen)
        self.assertEqual(self.client.patch(self.url, self.data, content_type="application/json").status_code, 403)
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.officer)
        self.assertEqual(secure.patch(self.url, self.data, content_type="application/json").status_code, 403)

    def test_routes_with_audit_and_rejects_post_assignment_changes(self):
        self.client.force_login(self.officer)
        self.assertEqual(self.client.patch(self.url, self.data, content_type="application/json").status_code, 200)
        self.report.refresh_from_db()
        self.assertEqual(self.report.routing_mode, "manual")
        self.assertEqual(self.report.ward, self.ward)
        self.assertIn("Demo reassignment", self.report.history.get().note)
        Complaint.objects.filter(pk=self.report.pk).update(status="assigned")
        self.assertEqual(self.client.patch(self.url, self.data, content_type="application/json").status_code, 409)

    def test_invalid_ids_and_unstaffed_ward(self):
        self.client.force_login(self.officer)
        for changes in ({"ward_id": True}, {"ward_id": 999}, {"note": ""}, {"expected_status": "resolved"}):
            self.assertEqual(self.client.patch(self.url, {**self.data, **changes}, content_type="application/json").status_code, 400)
        Worker.objects.update(active=False)
        self.assertEqual(self.client.patch(self.url, self.data, content_type="application/json").status_code, 400)
