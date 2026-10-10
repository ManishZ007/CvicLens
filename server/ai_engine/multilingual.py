from dataclasses import replace

from .analysis import analyze_text
from .contracts import AnalysisRequest, Language
from .translation import translate_to_english


def analyze_multilingual(text, language="en"):
    # Validate original text even when automatic detection was requested.
    validated = AnalysisRequest(text=text)
    if language not in {"en", "hi", "mr", "auto"}:
        raise ValueError("Select English, Hindi, Marathi or automatic detection.")
    source = Language.ENGLISH
    translated = None
    processing_text = validated.text
    if language != "en":
        source, processing_text = translate_to_english(
            validated.text, None if language == "auto" else language
        )
        if source != Language.ENGLISH:
            translated = processing_text
    result = analyze_text(AnalysisRequest(text=processing_text))
    return replace(result, original_text=text, original_language=source,
                   translated_text=translated).to_dict()
