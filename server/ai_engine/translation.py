"""Azure Translator adapter. No credentials or fabricated translations included."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .contracts import Language


class TranslationUnavailable(RuntimeError):
    pass


def translate_to_english(text, source=None):
    key = os.environ.get("AZURE_TRANSLATOR_KEY", "").strip()
    if not key:
        raise TranslationUnavailable("Translation is not configured. Select English or submit without AI analysis.")
    params = {"api-version": "3.0", "to": "en"}
    if source is not None:
        params["from"] = Language(source).value
    headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": key}
    region = os.environ.get("AZURE_TRANSLATOR_REGION", "").strip()
    if region:
        headers["Ocp-Apim-Subscription-Region"] = region
    request = Request(
        "https://api.cognitive.microsofttranslator.com/translate?" + urlencode(params),
        data=json.dumps([{"Text": text}], ensure_ascii=False).encode("utf-8"),
        headers=headers, method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read(131073)
        if len(raw) > 131072:
            raise TranslationUnavailable("Translation response was too large.")
        item = json.loads(raw)[0]
        language = source or item["detectedLanguage"]["language"]
        if language not in {"en", "hi", "mr"}:
            raise ValueError("Only English, Hindi and Marathi are supported.")
        if source is None and item["detectedLanguage"].get("score", 0) < 0.7:
            raise ValueError("Language detection is uncertain. Select the complaint language.")
        translated = next(entry["text"] for entry in item["translations"] if entry["to"] == "en")
        if not isinstance(translated, str) or not translated.strip():
            raise TranslationUnavailable("Translation returned no text.")
        return Language(language), translated
    except HTTPError as exc:
        raise TranslationUnavailable("Translation provider rejected the request. Check configuration or try later.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise TranslationUnavailable("Translation service is temporarily unavailable.") from exc
    except (KeyError, IndexError, TypeError, StopIteration, json.JSONDecodeError) as exc:
        raise TranslationUnavailable("Translation service returned an invalid response.") from exc
