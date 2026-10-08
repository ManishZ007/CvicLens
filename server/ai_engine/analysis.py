"""Combined local analysis entry point for later authenticated API integration."""

from dataclasses import replace

from .contracts import AnalysisRequest, AnalysisResult
from .model_classifier import classify_with_model
from .priority import suggest_priority


def analyze_text(request: AnalysisRequest) -> AnalysisResult:
    result = classify_with_model(request)
    suggestion = suggest_priority(request, result.category)
    return replace(result, priority=suggestion.priority,
                   priority_reason=suggestion.reason, priority_method=suggestion.method)
