import json

from django.core import signing
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .multilingual import analyze_multilingual
from .translation import TranslationUnavailable
from .speech import MAX_BYTES, SpeechUnavailable, transcribe_audio


TOKEN_SALT = "civiclens-analysis-v1"


def verify_analysis(token, user_id, text, language):
    try:
        payload = signing.loads(token, salt=TOKEN_SALT, max_age=900)
        result = payload["analysis"]
        if (payload["user_id"] != user_id or result["original_text"] != text
                or result["original_language"] != language):
            raise ValueError("Analysis does not match this report. Analyze it again.")
        return result
    except (signing.BadSignature, KeyError, TypeError) as exc:
        raise ValueError("Analysis expired or is invalid. Analyze again or submit without it.") from exc


@require_POST
def classify(request):
    if not request.user.is_authenticated:
        return JsonResponse({"errors": {"__all__": ["Not authenticated."]}}, status=401)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object.")
        text = data.get("text")
        language = data.get("language", "en")
        if not isinstance(language, str):
            raise ValueError("Invalid language.")
        result = analyze_multilingual(text, language)
    except TranslationUnavailable as exc:
        return JsonResponse({"errors": {"__all__": [str(exc)]}}, status=503)
    except (ValueError, UnicodeDecodeError) as exc:
        return JsonResponse({"errors": {"__all__": [str(exc)]}}, status=400)
    token = signing.dumps({"user_id": request.user.pk, "analysis": result},
                          salt=TOKEN_SALT, compress=True)
    return JsonResponse({"analysis": result, "analysis_token": token})


@require_POST
def transcribe(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated."}, status=401)
    audio = request.FILES.get("audio")
    if audio is None:
        return JsonResponse({"error": "Upload an audio recording."}, status=400)
    if audio.size > MAX_BYTES:
        return JsonResponse({"error": "Audio must be 10 MB or smaller."}, status=413)
    try:
        result = transcribe_audio(audio.read(MAX_BYTES + 1), request.POST.get("language", "en"))
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except SpeechUnavailable as exc:
        return JsonResponse({"error": str(exc)}, status=503)
    if not result["text"]:
        return JsonResponse({"error": "No speech detected. Record again in a quieter place."}, status=422)
    return JsonResponse(result)
