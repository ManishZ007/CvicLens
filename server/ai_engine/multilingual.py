from dataclasses import replace

from .analysis import analyze_text
from .contracts import AnalysisRequest, Language
from .translation import TranslationUnavailable, translate_to_english
from .local_language import analyze_local


def analyze_multilingual(text, language="en"):
    # Validate original text even when automatic detection was requested.
    validated = AnalysisRequest(text=text)
    if language not in {"en", "hi", "mr", "auto"}:
        raise ValueError("Select English, Hindi, Marathi or automatic detection.")
    source = Language.ENGLISH
    translated = None
    processing_text = validated.text
    if language != "en":
        try:
            source, processing_text = translate_to_english(
                validated.text, None if language == "auto" else language
            )
        except TranslationUnavailable:
            if language == "auto":
                raise
            result = analyze_local(validated.text, language)
            result["notice"] = "Local keyword rules used. English translation is unavailable; confirm the category and priority."
            return result
        if source != Language.ENGLISH:
            translated = processing_text
    result = analyze_text(AnalysisRequest(text=processing_text))
    return replace(result, original_text=validated.text, original_language=source,
                   translated_text=translated).to_dict()
