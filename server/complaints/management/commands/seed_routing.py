from django.core.management.base import BaseCommand

from complaints.models import Department, Ward


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

    def handle(self, *args, **options):
        for code, name in DEPARTMENTS:
            Department.objects.get_or_create(
                code=code,
                defaults={"name": name},
            )

        for code, name in DEMO_WARDS:
            Ward.objects.get_or_create(
                code=code,
                defaults={"name": name},
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Routing departments and demo wards seeded successfully."
            )
        )