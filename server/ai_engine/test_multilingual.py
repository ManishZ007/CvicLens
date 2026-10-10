import json
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import path, include

from .multilingual import analyze_multilingual
from .translation import TranslationUnavailable, translate_to_english
from .views import verify_analysis


urlpatterns = [path("api/ai/", include("ai_engine.urls"))]


@override_settings(ROOT_URLCONF=__name__)
class MultilingualTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="language@example.com", full_name="Citizen", age=22,
        )
        self.client.force_login(self.user)

    @patch("ai_engine.multilingual.translate_to_english")
    def test_english_stays_local(self, translate):
        result = analyze_multilingual("Pothole near school", "en")
        translate.assert_not_called()
        self.assertEqual(result["category"], "pothole")
        self.assertIsNone(result["translated_text"])

    @patch("ai_engine.multilingual.translate_to_english", return_value=("mr", "Deep pothole near school"))
    def test_marathi_original_is_preserved(self, translate):
        text = "शाळेजवळ मोठा खड्डा आहे."
        result = analyze_multilingual(text, "mr")
        self.assertEqual(result["original_text"], text)
        self.assertEqual(result["translated_text"], "Deep pothole near school")
        self.assertEqual(result["priority"], "high")

    @patch.dict("os.environ", {"AZURE_TRANSLATOR_KEY": ""})
    def test_missing_credentials_are_explicit(self):
        with self.assertRaises(TranslationUnavailable):
            analyze_multilingual("सड़क पर गड्ढा है", "hi")

    @patch.dict("os.environ", {"AZURE_TRANSLATOR_KEY": "test-not-a-real-key"})
    @patch("ai_engine.translation.urlopen")
    def test_provider_request_and_auto_detection(self, open_url):
        response = MagicMock()
        response.read.return_value = json.dumps([{
            "detectedLanguage": {"language": "hi", "score": 0.99},
            "translations": [{"to": "en", "text": "Pothole on road"}],
        }]).encode()
        open_url.return_value.__enter__.return_value = response
        language, text = translate_to_english("सड़क पर गड्ढा है")
        self.assertEqual(language, "hi")
        self.assertEqual(text, "Pothole on road")
        self.assertEqual(open_url.call_args.kwargs["timeout"], 10)

    def test_signed_result_bound_to_user_and_text(self):
        response = self.client.post("/api/ai/classify/", {
            "text": "Deep pothole", "language": "en",
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        token = response.json()["analysis_token"]
        self.assertEqual(verify_analysis(token, self.user.pk, "Deep pothole", "en")["priority"], "high")
        for user_id, text in ((self.user.pk + 1, "Deep pothole"), (self.user.pk, "Changed")):
            with self.assertRaises(ValueError):
                verify_analysis(token, user_id, text, "en")

    def test_authentication_required(self):
        self.client.logout()
        self.assertEqual(self.client.post("/api/ai/classify/", {}, content_type="application/json").status_code, 401)

    def test_invalid_language(self):
        self.assertEqual(self.client.post("/api/ai/classify/", {
            "text": "Pothole", "language": "xx",
        }, content_type="application/json").status_code, 400)

    @patch.dict("os.environ", {"AZURE_TRANSLATOR_KEY": ""})
    def test_unavailable_service_returns_503(self):
        self.assertEqual(self.client.post("/api/ai/classify/", {
            "text": "खड्डा", "language": "mr",
        }, content_type="application/json").status_code, 503)
