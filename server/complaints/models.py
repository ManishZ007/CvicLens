
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


CATEGORIES = [
    ("pothole", "Pothole"),
    ("garbage", "Garbage"),
    ("water", "Water"),
    ("light", "Streetlight"),
    ("drain", "Drainage"),
    ("other", "Other"),
]

STATUSES = [
    ("submitted", "Submitted"),
    ("verified", "Verified"),
    ("assigned", "Assigned"),
    ("in_progress", "In progress"),
    ("resolved", "Resolved"),
]


class Department(models.Model):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=100)


class Ward(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)


class Worker(models.Model):
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)


class Complaint(models.Model):
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="complaints",
    )
    description = models.TextField(max_length=5000)
    category = models.CharField(
        max_length=20, choices=CATEGORIES, default="other"
    )
    status = models.CharField(
        max_length=20, choices=STATUSES, default="submitted"
    )
    priority = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
    )
    latitude = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.PROTECT
    )
    ward = models.ForeignKey(
        Ward, null=True, blank=True, on_delete=models.PROTECT
    )
    assigned_worker = models.ForeignKey(
        Worker, null=True, blank=True, on_delete=models.PROTECT
    )
    routing_mode = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class StatusHistory(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name="history"
    )
    status = models.CharField(max_length=20, choices=STATUSES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ComplaintMedia(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name="media"
    )
    file = models.FileField(upload_to="complaints/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
