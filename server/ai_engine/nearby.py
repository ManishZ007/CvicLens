"""Explainable proximity/text suggestions; never merge complaints automatically."""
import json
import math
import unicodedata
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from complaints.models import Complaint
from .contracts import AnalysisRequest, Category, Coordinates

MAX_CANDIDATES = 1000


def distance_metres(lat1, lng1, lat2, lng2):
    a, b = math.radians(lat1), math.radians(lat2)
    dlat, dlng = b - a, math.radians(lng2 - lng1)
    value = math.sin(dlat / 2) ** 2 + math.cos(a) * math.cos(b) * math.sin(dlng / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(min(1, max(0, value))))


def tokens(text):
    # Retain combining marks in Hindi/Marathi. No claim of semantic translation.
    text = unicodedata.normalize("NFC", text).casefold()
    return set("".join(c if unicodedata.category(c)[0] in "LNM" else " "
                       for c in text).split())


def nearby_candidates(location, radius, category=None):
    delta = math.degrees(radius / 6371000)
    rows = Complaint.objects.exclude(status="resolved").filter(
        latitude__range=(location.latitude - delta, location.latitude + delta),
        longitude__isnull=False, created_at__gte=timezone.now() - timedelta(days=30),
    )
    if category:
        rows = rows.filter(category=category)
    # Bound SQL work before calculating precise distances; report truncation honestly.
    rows = list(rows.order_by("-created_at", "-id")[:MAX_CANDIDATES + 1])
    found = []
    for row in rows[:MAX_CANDIDATES]:
        distance = distance_metres(location.latitude, location.longitude, row.latitude, row.longitude)
        if distance <= radius:
            found.append((row, distance))
    return sorted(found, key=lambda item: (item[1], -item[0].pk)), len(rows) > MAX_CANDIDATES


def public_summary(row, distance):
    # Never expose another citizen's text, identity, photo or precise coordinates.
    return {"id": row.pk, "category": row.category, "status": row.status,
            "distance_metres": round(distance), "created_at": row.created_at.isoformat()}


def response(payload, status=200):
    result = JsonResponse(payload, status=status)
    result["Cache-Control"] = "private, no-store"
    return result


@require_POST
def duplicates(request):
    if not request.user.is_authenticated:
        return response({"error": "Sign in first."}, 401)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object.")
        location = Coordinates(data.get("latitude"), data.get("longitude"))
        category = Category(data.get("category"))
        text = AnalysisRequest(data.get("text")).text
    except (ValueError, TypeError, UnicodeDecodeError) as exc:
        return response({"error": str(exc)}, 400)
    candidates, truncated = nearby_candidates(location, 200, category.value)
    query_tokens = tokens(text)
    results = []
    for row, distance in candidates:
        existing = tokens(row.description)
        union = query_tokens | existing
        similarity = len(query_tokens & existing) / len(union) if union else 0
        if similarity >= 0.35:
            results.append({**public_summary(row, distance), "similarity": round(similarity, 3)})
    results.sort(key=lambda item: (-item["similarity"], item["distance_metres"], -item["id"]))
    return response({"results": results[:5], "truncated": truncated,
                     "method": "token_overlap_and_distance", "radius_metres": 200,
                     "lookback_days": 30, "automatic_merge": False})


@require_GET
def nearby(request):
    if not request.user.is_authenticated:
        return response({"error": "Sign in first."}, 401)
    try:
        location = Coordinates(float(request.GET.get("latitude", "")),
                               float(request.GET.get("longitude", "")))
    except (TypeError, ValueError):
        return response({"error": "Provide valid latitude and longitude."}, 400)
    candidates, truncated = nearby_candidates(location, 2000)
    return response({"results": [public_summary(row, distance) for row, distance in candidates[:50]],
                     "truncated": truncated or len(candidates) > 50,
                     "radius_metres": 2000, "lookback_days": 30})
