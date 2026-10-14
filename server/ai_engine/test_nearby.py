from datetime import timedelta
from django.test import Client, TestCase
from django.utils import timezone
from users.models import User
from complaints.models import Complaint
from .nearby import distance_metres, tokens


class NearbyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="near@example.com", full_name="Near", age=22,
                                             password="test-password")
        self.other = User.objects.create_user(email="other@example.com", full_name="Other", age=22,
                                              password="test-password")
        self.client.force_login(self.user)
        self.data = {"text": "Large pothole near school", "category": "pothole",
                     "latitude": 18.52, "longitude": 73.82}

    def report(self, **changes):
        fields = dict(reporter=self.other, description=self.data["text"], category="pothole",
                      latitude=18.5201, longitude=73.82)
        fields.update(changes)
        return Complaint.objects.create(**fields)

    def check_duplicates(self, **changes):
        return self.client.post("/api/ai/duplicates/", {**self.data, **changes},
                                content_type="application/json")

    def test_near_match_without_private_fields_or_merging(self):
        row = self.report()
        payload = self.check_duplicates().json()
        self.assertEqual(payload["results"][0]["id"], row.pk)
        self.assertFalse(payload["automatic_merge"])
        self.assertEqual(set(payload["results"][0]),
                         {"id", "category", "status", "distance_metres", "created_at", "similarity"})
        self.assertEqual(Complaint.objects.count(), 1)

    def test_excludes_far_old_resolved_and_different_category(self):
        self.report(latitude=19)
        self.report(status="resolved")
        self.report(category="garbage")
        self.report(description="The street lights are flickering")
        old = self.report()
        Complaint.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=31))
        self.assertEqual(self.check_duplicates().json()["results"], [])

    def test_nearby_includes_other_categories_and_is_distance_sorted(self):
        far = self.report(latitude=18.53, category="water")
        near = self.report()
        self.report(latitude=19)
        result = self.client.get("/api/ai/nearby/?latitude=18.52&longitude=73.82").json()
        self.assertEqual([item["id"] for item in result["results"]], [near.pk, far.pk])
        self.assertNotIn("description", result["results"][0])

    def test_input_auth_and_csrf(self):
        for invalid in (None, True, "18", 91):
            self.assertEqual(self.check_duplicates(latitude=invalid).status_code, 400)
        self.assertEqual(self.check_duplicates(category="invalid").status_code, 400)
        self.assertEqual(self.client.get("/api/ai/nearby/?latitude=nan&longitude=2").status_code, 400)
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.user)
        self.assertEqual(secure.post("/api/ai/duplicates/", self.data, content_type="application/json").status_code, 403)
        token = secure.get("/api/complaints/csrf/").json()["csrfToken"]
        self.assertEqual(secure.post("/api/ai/duplicates/", self.data, content_type="application/json",
                                    HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.client.logout()
        self.assertEqual(self.check_duplicates().status_code, 401)
        self.assertEqual(self.client.get("/api/ai/nearby/").status_code, 401)

    def test_devanagari_tokens_and_dateline(self):
        self.assertIn("रस्ता", tokens("रस्ता खराब आहे."))
        self.assertLess(distance_metres(0, 179.9995, 0, -179.9995), 120)
