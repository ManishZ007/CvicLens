"""English keyword baseline; not a trained model or an urgency assessment."""

import re

from .contracts import AnalysisRequest, AnalysisResult, Category, Language, Priority


KEYWORDS = {
    Category.POTHOLE: ("pothole", "potholes", "hole in the road", "holes in the road"),
    Category.GARBAGE: ("garbage", "trash", "rubbish", "uncollected waste"),
    Category.WATER: ("water leak", "water leakage", "leaking pipe", "burst pipe",
                     "burst water pipe", "water supply", "no water"),
    Category.LIGHT: ("streetlight", "streetlights", "street light", "street lights",
                     "street lamp", "street lamps"),
    Category.DRAIN: ("drain", "drains", "drainage", "sewage", "sewer"),
}


def classify_text(request: AnalysisRequest) -> AnalysisResult:
    """Return an explainable suggestion. Ambiguous reports require manual review.

    Language is supplied by the caller, not detected. Unsupported languages fail
    explicitly until the translation pipeline exists. Citizen category selection
    is intentionally not used as evidence for the text prediction.
    """
    if request.language != Language.ENGLISH:
        raise NotImplementedError("The Day 2 baseline supports English only.")

    normalized = re.sub(r"[\W_]+", " ", request.text.casefold()).strip()
    matches = {
        category: [term for term in terms
                   if re.search(r"\b" + re.escape(term) + r"\b", normalized)]
        for category, terms in KEYWORDS.items()
    }
    matches = {category: terms for category, terms in matches.items() if terms}

    if len(matches) == 1:
        category = next(iter(matches))
        reason = "Keyword matches: " + ", ".join(matches[category]) + "."
    elif matches:
        category = Category.OTHER
        reason = "Multiple categories matched; manual review required: " + ", ".join(
            category.value for category in matches
        ) + "."
    else:
        category = Category.OTHER
        reason = "No supported keyword matched; manual review required."

    return AnalysisResult(
        original_text=request.text,
        original_language=request.language,
        category=category,
        priority=Priority.MEDIUM,
        confidence=None,
        reason=reason + " Priority is a placeholder, not assessed by this classifier.",
        method="rules",
    )
