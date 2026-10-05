"""Explainable English priority suggestions, not a trained urgency model."""

from dataclasses import dataclass
import re

from .contracts import AnalysisRequest, Category, Language, Priority


@dataclass(frozen=True)
class PrioritySuggestion:
    priority: Priority
    reason: str
    method: str = "rules"


HIGH_SIGNALS = (
    "exposed wire", "exposed wires", "live wire", "live wires",
    "sparking", "electric shock", "electrocution", "injured", "injuries",
    "accident", "accidents", "skidding", "open manhole", "deep pothole",
    "sewage entering homes", "sewage entering houses",
)
VULNERABLE_PLACES = ("school", "hospital", "playground")
MINOR_SIGNALS = ("slightly flickering", "minor flicker", "cosmetic damage")


def active_phrases(text, phrases):
    """Ignore simple nearby negation, without claiming full language understanding."""
    found = []
    for phrase in phrases:
        for match in re.finditer(r"\b" + re.escape(phrase) + r"\b", text):
            prefix = re.split(r"[.!?;,]|\b(?:but|however)\b", text[:match.start()])[-1]
            preceding = re.findall(r"\w+", prefix)[-3:]
            if not {"no", "not", "without", "never"}.intersection(preceding):
                found.append(phrase)
                break
    return found


def suggest_priority(request: AnalysisRequest, category: Category) -> PrioritySuggestion:
    if request.language != Language.ENGLISH:
        raise NotImplementedError("Priority suggestions currently support English only.")
    category = Category(category)
    text = re.sub(r"[\s_-]+", " ", request.text.casefold())
    hazards = active_phrases(text, HIGH_SIGNALS)
    if hazards:
        return PrioritySuggestion(Priority.HIGH, "Reported safety signals: " + ", ".join(hazards) + ".")
    places = active_phrases(text, VULNERABLE_PLACES)
    if places and category in {Category.POTHOLE, Category.DRAIN}:
        return PrioritySuggestion(Priority.HIGH, "Road/drain issue mentions a sensitive location: " + ", ".join(places) + ".")
    minor = active_phrases(text, MINOR_SIGNALS)
    if minor and category in {Category.LIGHT, Category.OTHER}:
        return PrioritySuggestion(Priority.LOW, "Minor issue reported: " + ", ".join(minor) + ".")
    return PrioritySuggestion(Priority.MEDIUM, "Standard review priority; no supported high-risk or minor-issue phrase matched.")
