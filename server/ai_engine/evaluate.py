"""Run with: python -m ai_engine.evaluate. Evaluation does not train the model."""

import json

from .classifier import classify_text
from .contracts import AnalysisRequest
from .model_classifier import classify_with_model
from .training_data import EVALUATION


def evaluate():
    results = {}
    for name, classify in (("rules", classify_text), ("model", classify_with_model)):
        rows = [
            {"text": text, "expected": category,
             "predicted": classify(AnalysisRequest(text)).category.value}
            for category, text in EVALUATION
        ]
        results[name] = {
            "correct": sum(row["expected"] == row["predicted"] for row in rows),
            "total": len(rows), "examples": rows,
        }
    return results


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
