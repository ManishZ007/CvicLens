import json
import unittest

from .contracts import AnalysisRequest, AnalysisResult, Category, Coordinates, Language, Priority


class ContractTests(unittest.TestCase):
    def test_request_preserves_marathi(self):
        request = AnalysisRequest("  रस्त्यावर खड्डा आहे.  ", language="mr")
        self.assertEqual(request.text, "रस्त्यावर खड्डा आहे.")
        self.assertEqual(request.language, Language.MARATHI)

    def test_invalid_requests(self):
        for fields in ({"text": " "}, {"text": "x" * 5001},
                       {"text": "road", "language": "xx"},
                       {"text": "road", "selected_category": "unknown"},
                       {"text": "road", "location": {}}):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                AnalysisRequest(**fields)

    def test_coordinates(self):
        self.assertEqual(Coordinates(18.52, 73.85).latitude, 18.52)
        for lat, lng in ((91, 0), (0, 181), (float("nan"), 0),
                         (0, float("inf")), (True, 0), ("18", 0)):
            with self.subTest(lat=lat, lng=lng), self.assertRaises(ValueError):
                Coordinates(lat, lng)

    def test_result_is_json_serializable(self):
        result = AnalysisResult("pothole", Language.ENGLISH, Category.POTHOLE,
                                Priority.MEDIUM, None, "Keyword match", "rules")
        data = json.loads(json.dumps(result.to_dict()))
        self.assertEqual(data["category"], "pothole")
        self.assertIsNone(data["confidence"])

    def test_invalid_confidence(self):
        for value in (-1, 2, float("nan"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                AnalysisResult("road", "en", "other", "low", value, "", "model")
