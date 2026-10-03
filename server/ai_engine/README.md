# Day 1: AI contract

Owner: Manish. This package defines contracts only; it does not provide an HTTP
endpoint or claim to run an AI model. No dependency or Django configuration change
is needed. Naman owns API wiring and authentication.

## Shared identifiers

- Categories: `pothole`, `garbage`, `water`, `light`, `drain`, `other`.
- Languages: `en`, `hi`, `mr`.
- Priorities: `low`, `medium`, `high` (UI may display medium as `med`).
- Coordinates: `latitude`, `longitude`, numeric decimal degrees.

## Proposed text analysis endpoint (not implemented yet)

`POST /api/ai/classify/`, authenticated session and CSRF-protected.

```json
{
  "text": "Large pothole near school",
  "language": "en",
  "location": {"latitude": 18.52, "longitude": 73.85},
  "selected_category": null
}
```

Location and selected_category are optional. Text must be non-empty, at most
5000 characters. The supplied language is a preference until detection is added.
Future image/audio inputs will use validated uploads, not arbitrary remote URLs.

Response shape: original_text, original_language, translated_text (nullable),
category, priority, confidence (0..1 or null), reason, method (rules or model).
Never invent a confidence score for keyword rules. Preserve original-language
text. AI recommendations remain editable by the citizen/officer.

Errors should follow the existing API convention:
`{"errors": {"text": ["A non-empty text description is required."]}}`.
Use 400 for invalid input, 401 for unauthenticated access, 503 for an unavailable
analysis service. These are agreed implementation targets, not live routes.

## Verify

From server: `python -m unittest ai_engine.tests -v`.

## Day 2: English keyword baseline

`classify_text(AnalysisRequest(...))` in `classifier.py` suggests a category from
whole-word/phrase matches. No dependencies or HTTP routes are added.

```python
from ai_engine.classifier import classify_text
from ai_engine.contracts import AnalysisRequest

result = classify_text(AnalysisRequest("Large pothole near the school"))
print(result.to_dict())
```

The method is explicitly `rules`, confidence is null, and medium priority is an
unassessed placeholder until Day 4. Multiple matching categories or no matches
produce `other` for manual review. Hindi/Marathi raise NotImplementedError until
translation is implemented. This baseline does not understand negation, context,
or synonyms beyond its keyword list; it is not a trained AI model. Caller-supplied
language is not automatic detection. Original text is preserved after the request
contract's whitespace trimming. A citizen selection never becomes model evidence.
