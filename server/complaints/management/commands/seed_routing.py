from django.core.management.base import BaseCommand
from django.db import transaction

from complaints.models import Complaint, Department, Ward, Worker
from complaints.routing import apply_routing
from ai_engine.location import DEPARTMENTS as ROUTING_DEPARTMENTS, DEMO_WARDS as ROUTING_WARDS


DEPARTMENTS = [
    ("roads", "Roads"),
    ("sanitation", "Sanitation"),
    ("water", "Water"),
    ("street-lighting", "Street Lighting"),
    ("drainage", "Drainage"),
]


DEMO_WARDS = [
    ("W01", "Ward 01"),
    ("W02", "Ward 02"),
    ("W03", "Ward 03"),
    ("W04", "Ward 04"),
    ("W05", "Ward 05"),
]


class Command(BaseCommand):
    help = "Seed demo departments and wards for complaint routing."

    @transaction.atomic
    def handle(self, *args, **options):
        departments = []
        for code, name in ROUTING_DEPARTMENTS.items():
            department, _ = Department.objects.get_or_create(
                code=code,
                defaults={"name": name},
            )
            departments.append(department)

        for zone in ROUTING_WARDS:
            ward, _ = Ward.objects.get_or_create(
                code=zone.code,
                defaults={"name": zone.name},
            )
            for department in departments:
                Worker.objects.get_or_create(
                    name=f"Demo worker — {department.name} — {zone.code}",
                    department=department, ward=ward,
                )
        for code, name in DEMO_WARDS:
            Ward.objects.filter(code=code, name=name).update(
                name=f"Legacy demo zone {code} (not an official ward)"
            )
        for complaint in Complaint.objects.filter(
            status__in=["submitted", "verified"], assigned_worker__isnull=True
        ):
            apply_routing(complaint)
            complaint.save(update_fields=["department", "ward", "routing_mode"])

        self.stdout.write(
            self.style.SUCCESS(
                "Demo departments, wards and workers ready (not official municipal wards)."
            )
        )
