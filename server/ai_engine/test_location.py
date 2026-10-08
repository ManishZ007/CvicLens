import unittest

from .location import route_complaint


class LocationRoutingTests(unittest.TestCase):
    def test_category_department_mapping(self):
        for category, department in {
            "pothole": "roads", "garbage": "sanitation", "water": "water",
            "light": "electrical", "drain": "drainage", "other": "general",
        }.items():
            with self.subTest(category=category):
                self.assertEqual(route_complaint(category).department_code, department)

    def test_demo_zone_a(self):
        result = route_complaint("pothole", 18.52, 73.82)
        self.assertEqual(result.ward_code, "DEMO-A")
        self.assertEqual(result.mode, "demo")
        self.assertIn("not an official", result.reason)

    def test_shared_edge_belongs_to_zone_b(self):
        self.assertEqual(route_complaint("water", 18.52, 73.85).ward_code, "DEMO-B")

    def test_upper_edges_are_outside(self):
        for lat, lng in ((18.55, 73.82), (18.52, 73.90)):
            with self.subTest(lat=lat, lng=lng):
                self.assertEqual(route_complaint("water", lat, lng).mode, "outside_demo")

    def test_outside_does_not_invent_ward(self):
        result = route_complaint("drain", 0, 0)
        self.assertIsNone(result.ward_code)
        self.assertEqual(result.mode, "outside_demo")

    def test_missing_location_is_pending(self):
        self.assertEqual(route_complaint("other").mode, "pending")

    def test_invalid_coordinates(self):
        for lat, lng in ((None, 73), (18, None), (91, 0), (0, -181),
                         (float("nan"), 0), (True, 0), ("18.52", 73.82)):
            with self.subTest(lat=lat, lng=lng), self.assertRaises(ValueError):
                route_complaint("pothole", lat, lng)

    def test_unknown_category_rejected(self):
        with self.assertRaises(ValueError):
            route_complaint("unknown", 18.52, 73.82)
