import importlib.util
import os
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from complaints.models import Department, Ward, Worker


class Command(BaseCommand):
    help = "Read-only readiness checks for a local CivicLens showcase; never prints credentials."

    def handle(self, *args, **options):
        executor = MigrationExecutor(connection)
        if executor.migration_plan(executor.loader.graph.leaf_nodes()):
            raise CommandError("Pending migrations. Run manage.py migrate before the showcase.")
        self.stdout.write(self.style.SUCCESS("Database migrations: ready"))
        if not Department.objects.exists() or not Ward.objects.exists() or not Worker.objects.filter(active=True).exists():
            raise CommandError("Routing data missing. Run manage.py seed_routing.")
        self.stdout.write(self.style.SUCCESS("Departments, wards and active workers: ready"))
        if not get_user_model().objects.filter(is_staff=True, is_active=True).exists():
            raise CommandError("No active officer account. Run manage.py createsuperuser or create a staff account.")
        self.stdout.write(self.style.SUCCESS("Active officer account: ready"))
        model = Path(os.environ.get("CIVICLENS_WHISPER_MODEL", str(settings.BASE_DIR / "models/whisper-base")))
        speech = importlib.util.find_spec("faster_whisper") is not None and (model / "model.bin").is_file()
        self.stdout.write("Speech: " + ("local package/model present; test microphone in browser" if speech else "unavailable; follow ai_engine/SPEECH_SETUP.md"))
        translation = bool(os.environ.get("AZURE_TRANSLATOR_KEY", "").strip())
        self.stdout.write("Translation: " + ("key configured; verify provider access" if translation else "not configured; Hindi/Marathi use labelled keyword suggestions"))
        self.stdout.write("Demo routing and keyword suggestions are not official municipal decisions.")
