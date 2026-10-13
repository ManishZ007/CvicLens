import io
import wave
from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, SimpleTestCase
from users.models import User

from .speech import SpeechUnavailable, decode_audio, transcribe_audio


def wav(seconds=1):
    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\x00\x00" * (seconds * 16000))
    return output.getvalue()


class SpeechTests(SimpleTestCase):
    def test_decoder_validates_audio_and_duration(self):
        self.assertEqual(len(decode_audio(wav())), 16000)
        for data in (b"not audio", wav(61)):
            with self.assertRaises(ValueError):
                decode_audio(data)

    @patch("ai_engine.speech.get_model")
    def test_language_hint_and_transcript(self, get_model):
        for language, text in (("en", "Broken road"), ("hi", "सड़क टूटी है"), ("mr", "रस्ता खराब आहे")):
            get_model.return_value.transcribe.return_value = ([SimpleNamespace(text=text)], None)
            result = transcribe_audio(wav(), language)
            self.assertEqual(result["text"], text)
            self.assertEqual(result["language"], language)
            self.assertEqual(get_model.return_value.transcribe.call_args.kwargs["language"], language)

    def test_rejects_unsupported_language(self):
        with self.assertRaises(ValueError):
            transcribe_audio(wav(), "fr")


class SpeechApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="voice@example.com", password="test-password",
                                             full_name="Voice Tester", age=22)
        self.client.force_login(self.user)

    def upload(self, client=None, **extra):
        return (client or self.client).post("/api/ai/transcribe/", {
            "audio": SimpleUploadedFile("voice.wav", wav(), content_type="audio/wav"),
            "language": "en",
        }, **extra)

    @patch("ai_engine.views.transcribe_audio")
    def test_api_success_empty_and_unavailable(self, transcribe):
        transcribe.return_value = {"text": "Broken road", "language": "en"}
        self.assertEqual(self.upload().json()["text"], "Broken road")
        transcribe.return_value = {"text": ""}
        self.assertEqual(self.upload().status_code, 422)
        transcribe.side_effect = SpeechUnavailable("Model unavailable")
        self.assertEqual(self.upload().status_code, 503)

    def test_auth_input_and_size(self):
        self.assertEqual(self.client.post("/api/ai/transcribe/").status_code, 400)
        with patch("ai_engine.views.MAX_BYTES", 1):
            self.assertEqual(self.upload().status_code, 413)
        self.client.logout()
        self.assertEqual(self.upload().status_code, 401)

    @patch("ai_engine.views.transcribe_audio", return_value={"text": "Road"})
    def test_csrf(self, transcribe):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(self.upload(client).status_code, 403)
        token = client.get("/api/complaints/csrf/").json()["csrfToken"]
        self.assertEqual(self.upload(client, HTTP_X_CSRFTOKEN=token).status_code, 200)

    def test_preferences_require_csrf_and_persist(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        url = "/api/users/preferences/"
        body = '{"preferred_language":"mr"}'
        self.assertEqual(client.patch(url, body, content_type="application/json").status_code, 403)
        token = client.get("/api/complaints/csrf/").json()["csrfToken"]
        self.assertEqual(client.patch(url, body, content_type="application/json",
                                      HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_language, "mr")
