from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .models import Complaint, Department, Ward, Worker
from .routing import apply_routing


class RoutingIntegrationTests(TestCase):
    def test_seed_is_repeatable_and_matches_service(self):
        for _ in range(2):
            call_command("seed_routing", stdout=StringIO())
        self.assertEqual(Department.objects.count(), 6)
        self.assertEqual(Ward.objects.count(), 2)
        self.assertEqual(Worker.objects.count(), 12)
        complaint = Complaint(category="light", latitude=18.52, longitude=73.82)
        apply_routing(complaint)
        self.assertEqual(complaint.department.code, "electrical")
        self.assertEqual(complaint.ward.code, "DEMO-A")
        self.assertEqual(complaint.routing_mode, "demo")

    def test_seed_routes_existing_unassigned_report(self):
        user = get_user_model().objects.create_user(
            email="routing@example.com", full_name="Citizen", age=22,
        )
        report = Complaint.objects.create(
            reporter=user, description="Pothole", category="pothole",
            latitude=18.52, longitude=73.86,
        )
        call_command("seed_routing", stdout=StringIO())
        report.refresh_from_db()
        self.assertEqual(report.ward.code, "DEMO-B")
        self.assertEqual(report.department.code, "roads")
