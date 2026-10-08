import unittest

from .analysis import analyze_text
from .contracts import AnalysisRequest, Priority
from .priority import suggest_priority


class PriorityTests(unittest.TestCase):
    def test_high_risk_examples(self):
        for text, category in (
            ("Deep pothole causing skidding", "pothole"),
            ("Exposed wires beside a pole", "light"),
            ("Open manhole near market", "drain"),
            ("Pothole near school", "pothole"),
        ):
            with self.subTest(text=text):
                self.assertEqual(suggest_priority(AnalysisRequest(text), category).priority, Priority.HIGH)

    def test_minor_issue(self):
        result = suggest_priority(AnalysisRequest("Streetlight is slightly flickering"), "light")
        self.assertEqual(result.priority, Priority.LOW)

    def test_standard_issue(self):
        result = suggest_priority(AnalysisRequest("Garbage collection missed"), "garbage")
        self.assertEqual(result.priority, Priority.MEDIUM)

    def test_negated_hazard_does_not_escalate(self):
        result = suggest_priority(AnalysisRequest("No injuries or accidents reported"), "other")
        self.assertEqual(result.priority, Priority.MEDIUM)

    def test_high_signal_wins_over_minor_signal(self):
        result = suggest_priority(AnalysisRequest("Minor flicker but exposed wires are sparking"), "light")
        self.assertEqual(result.priority, Priority.HIGH)

    def test_word_boundaries(self):
        result = suggest_priority(AnalysisRequest("Hospitality sign needs cleaning"), "other")
        self.assertEqual(result.priority, Priority.MEDIUM)

    def test_combined_analysis_labels_methods(self):
        result = analyze_text(AnalysisRequest("Deep pothole near school"))
        self.assertEqual(result.priority, Priority.HIGH)
        self.assertEqual(result.method, "model")
        self.assertEqual(result.priority_method, "rules")
        self.assertTrue(result.priority_reason)
        self.assertIsNone(result.confidence)

    def test_unsupported_language_rejected(self):
        with self.assertRaises(NotImplementedError):
            suggest_priority(AnalysisRequest("खड्डा", language="mr"), "pothole")
