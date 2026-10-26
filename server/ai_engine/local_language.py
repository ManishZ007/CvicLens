"""Conservative Hindi/Marathi keyword fallback; never fabricates translation."""
import unicodedata
from .contracts import AnalysisResult, Category, Language, Priority

TERMS = {
    Category.POTHOLE: ("गड्ढा", "गड्ढे", "खड्डा", "खड्डे", "खड्ड्य"),
    Category.GARBAGE: ("कचरा", "कचऱ", "कूड़ा", "कूड़े"),
    Category.WATER: ("पाणी", "पाण्य", "पानी", "जलापूर्ति", "पाइप", "पाईप"),
    Category.LIGHT: ("स्ट्रीट लाइट", "पथदिव", "पथ दिव", "सड़क की बत्ती", "रस्त्यावरील दिव"),
    Category.DRAIN: ("नाली", "नाला", "नाल्या", "गटार", "सीवर", "सांडपाणी"),
}
RISKS = ("अपघात", "दुर्घटना", "जखमी", "घायल", "खतरा", "धोका", "वीज तार", "बिजली का तार")


def analyze_local(text, language):
    normalized = unicodedata.normalize("NFC", text)
    matched = [category for category, terms in TERMS.items() if any(term in normalized for term in terms)]
    category = matched[0] if len(matched) == 1 else Category.OTHER
    risks = [term for term in RISKS if term in normalized]
    return AnalysisResult(
        original_text=text, original_language=Language(language), category=category,
        priority=Priority.HIGH if risks else Priority.MEDIUM, confidence=None,
        reason="Local language keyword rules; confirm the category. " +
               ("Ambiguous or unmatched wording." if len(matched) != 1 else "One civic category matched."),
        method="rules", translated_text=None, priority_method="rules",
        priority_reason="Reported safety terms: " + ", ".join(risks) if risks else
                        "No supported safety term matched; medium priority needs officer review.",
    ).to_dict()
