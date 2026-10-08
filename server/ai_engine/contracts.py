"""Shared, dependency-free contracts. No prediction is simulated here."""

from dataclasses import asdict, dataclass
from enum import Enum
from math import isfinite


class Category(str, Enum):
    POTHOLE = "pothole"
    GARBAGE = "garbage"
    WATER = "water"
    LIGHT = "light"
    DRAIN = "drain"
    OTHER = "other"


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self):
        for name, value, limit in (
            ("latitude", self.latitude, 90),
            ("longitude", self.longitude, 180),
        ):
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not isfinite(value) or not -limit <= value <= limit):
                raise ValueError(f"{name} must be a finite number between {-limit} and {limit}.")


@dataclass(frozen=True)
class AnalysisRequest:
    text: str
    language: Language = Language.ENGLISH
    location: Coordinates | None = None
    selected_category: Category | None = None

    def __post_init__(self):
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("A non-empty text description is required.")
        if len(self.text) > 5000:
            raise ValueError("Description must be 5000 characters or fewer.")
        object.__setattr__(self, "text", self.text.strip())
        object.__setattr__(self, "language", Language(self.language))
        if self.selected_category is not None:
            object.__setattr__(self, "selected_category", Category(self.selected_category))
        if self.location is not None and not isinstance(self.location, Coordinates):
            raise ValueError("location must be Coordinates or None.")


@dataclass(frozen=True)
class AnalysisResult:
    original_text: str
    original_language: Language
    category: Category
    priority: Priority
    confidence: float | None
    reason: str
    method: str
    translated_text: str | None = None
    priority_reason: str | None = None
    priority_method: str = "not_assessed"

    def __post_init__(self):
        object.__setattr__(self, "original_language", Language(self.original_language))
        object.__setattr__(self, "category", Category(self.category))
        object.__setattr__(self, "priority", Priority(self.priority))
        if self.method not in {"rules", "model"}:
            raise ValueError("method must be rules or model.")
        if self.priority_method not in {"not_assessed", "rules", "model"}:
            raise ValueError("Invalid priority method.")
        if self.confidence is not None:
            value = self.confidence
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not isfinite(value) or not 0 <= value <= 1):
                raise ValueError("confidence must be null or a number between 0 and 1.")

    def to_dict(self):
        return asdict(self)
