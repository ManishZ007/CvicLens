"""Dependency-free multinomial Naive Bayes adapter for the Day 3 prototype."""

from collections import Counter
from functools import lru_cache
from math import log
import re

from .contracts import AnalysisRequest, AnalysisResult, Category, Language, Priority
from .training_data import TRAINING


STOP_WORDS = set("a an the is are was were of in on at to from with and for near my has have not".split())


def tokenize(text):
    return [word for word in re.findall(r"[a-z]+", text.casefold())
            if word not in STOP_WORDS]


class NaiveBayesClassifier:
    def __init__(self, training):
        if set(training) != {category.value for category in Category}:
            raise ValueError("Training must include every supported category.")
        self.counts = {}
        self.documents = {}
        for category, examples in training.items():
            if not examples or any(not tokenize(text) for text in examples):
                raise ValueError("Each category needs non-empty training examples.")
            self.counts[category] = Counter(
                token for text in examples for token in tokenize(text)
            )
            self.documents[category] = len(examples)
        self.vocabulary = set().union(*(set(counts) for counts in self.counts.values()))
        self.totals = {key: sum(value.values()) for key, value in self.counts.items()}

    def classify(self, request: AnalysisRequest) -> AnalysisResult:
        if request.language != Language.ENGLISH:
            raise NotImplementedError("The Day 3 model supports English only.")
        tokens = Counter(word for word in tokenize(request.text) if word in self.vocabulary)
        category = Category.OTHER
        reason = "No known vocabulary; manual review required."
        if tokens:
            documents = sum(self.documents.values())
            scores = {
                key: log(self.documents[key] / documents) + sum(
                    count * log((words[token] + 1) / (self.totals[key] + len(self.vocabulary)))
                    for token, count in tokens.items()
                )
                for key, words in self.counts.items()
            }
            ranked = sorted(scores, key=scores.get, reverse=True)
            if abs(scores[ranked[0]] - scores[ranked[1]]) < 1e-9:
                reason = "Equal model scores; manual review required."
            else:
                category = Category(ranked[0])
                reason = "Prototype Naive Bayes suggestion from a small hand-authored dataset."
        return AnalysisResult(
            original_text=request.text, original_language=request.language,
            category=category, priority=Priority.MEDIUM, confidence=None,
            reason=reason + " Priority is not assessed; medium is a placeholder.",
            method="model",
        )


@lru_cache(maxsize=1)
def get_classifier():
    return NaiveBayesClassifier(TRAINING)


def classify_with_model(request: AnalysisRequest) -> AnalysisResult:
    return get_classifier().classify(request)
