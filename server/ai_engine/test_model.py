import unittest

from .contracts import AnalysisRequest, Category
from .model_classifier import NaiveBayesClassifier, classify_with_model
from .training_data import TRAINING, EVALUATION


class ModelTests(unittest.TestCase):
    def test_holdout_is_not_training_text(self):
        training = {text.casefold() for texts in TRAINING.values() for text in texts}
        self.assertTrue(all(text.casefold() not in training for _, text in EVALUATION))

    def test_model_is_trained_from_supplied_labels(self):
        custom = {category.value: [f"signal{word}"] for category, word in zip(
            Category, ("alpha", "beta", "gamma", "delta", "epsilon", "zeta")
        )}
        model = NaiveBayesClassifier(custom)
        self.assertEqual(model.classify(AnalysisRequest("signalalpha")).category, Category.POTHOLE)
        custom["pothole"], custom["garbage"] = custom["garbage"], custom["pothole"]
        model = NaiveBayesClassifier(custom)
        self.assertEqual(model.classify(AnalysisRequest("signalalpha")).category, Category.GARBAGE)

    def test_unknown_input_abstains(self):
        self.assertEqual(classify_with_model(AnalysisRequest("xyzzy quux")).category, Category.OTHER)

    def test_untranslated_input_is_rejected(self):
        with self.assertRaises(NotImplementedError):
            classify_with_model(AnalysisRequest("खड्डा", language="mr"))

    def test_output_has_no_calibrated_confidence(self):
        result = classify_with_model(AnalysisRequest("streetlight flickering"))
        self.assertEqual(result.category, Category.LIGHT)
        self.assertEqual(result.method, "model")
        self.assertIsNone(result.confidence)
        self.assertIsNone(result.translated_text)
        self.assertIn("not assessed", result.reason)

    def test_incomplete_training_rejected(self):
        with self.assertRaises(ValueError):
            NaiveBayesClassifier({"pothole": ["road"]})
