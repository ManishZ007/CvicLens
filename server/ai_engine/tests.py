import json
import unittest

from .contracts import AnalysisRequest, AnalysisResult, Category, Coordinates, Language, Priority
from .classifier import classify_text


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


class ClassifierTests(unittest.TestCase):
    def test_representative_categories(self):
        examples = {
            "Large POTHOLES near the school.": Category.POTHOLE,
            "Garbage has not been collected for four days.": Category.GARBAGE,
            "A burst water pipe near my house.": Category.WATER,
            "The street lights are not working.": Category.LIGHT,
            "The drain is overflowing.": Category.DRAIN,
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                self.assertEqual(classify_text(AnalysisRequest(text)).category, expected)

    def test_word_boundaries(self):
        result = classify_text(AnalysisRequest("I feel drained after work."))
        self.assertEqual(result.category, Category.OTHER)

    def test_whitespace_and_punctuation(self):
        result = classify_text(AnalysisRequest("Broken STREET-LIGHT near the park."))
        self.assertEqual(result.category, Category.LIGHT)

    def test_ambiguous_report_requires_review(self):
        result = classify_text(AnalysisRequest("Garbage is blocking the drain."))
        self.assertEqual(result.category, Category.OTHER)
        self.assertIn("Multiple categories", result.reason)

    def test_user_selection_is_not_prediction(self):
        result = classify_text(AnalysisRequest("Pothole near the school", selected_category="water"))
        self.assertEqual(result.category, Category.POTHOLE)

    def test_no_fabricated_confidence_or_translation(self):
        result = classify_text(AnalysisRequest("A pothole near the school"))
        self.assertIsNone(result.confidence)
        self.assertIsNone(result.translated_text)
        self.assertEqual(result.method, "rules")
        self.assertIn("not assessed", result.reason)

    def test_unsupported_language_is_explicit(self):
        for language in ("hi", "mr"):
            with self.subTest(language=language), self.assertRaises(NotImplementedError):
                classify_text(AnalysisRequest("रस्त्यावर खड्डा आहे.", language=language))
