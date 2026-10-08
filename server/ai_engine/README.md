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

## Day 3: trained local prototype

`model_classifier.classify_with_model(request)` implements multinomial Naive Bayes
with Laplace smoothing. It learns word counts from 36 hand-authored English
examples in `training_data.py`, cached in memory on first use. It is a small local
model adapter, not an external LLM or a production-trained municipal model.
No dependency, HTTP route, model download, or API credential is required.

Run `python -m ai_engine.evaluate` to compare the model with the Day 2 rules on
12 separate hand-authored examples: rules 8/12, model 12/12. This small synthetic
holdout is illustrative and does not establish real-world accuracy. The model
does not understand negation, mixed issues, or out-of-domain input reliably.
Unknown vocabulary and tied scores return `other`; human review is still needed.
Confidence remains null because scores are not calibrated. Priority remains an
explicit unassessed medium placeholder, and Hindi/Marathi are not supported yet.

Run `python manage.py test users ai_engine` for all current backend tests.

## Day 4: priority suggestions

Use `analysis.analyze_text(AnalysisRequest(text=...))` to combine the trained
category model with explicit English priority rules. Results add `priority_reason`
and `priority_method`; category `method` remains `model`, priority method is
`rules`, and confidence remains null. No HTTP route or database writes are added.

Direct category-only classification still returns an unassessed medium placeholder,
now identified by `priority_method=not_assessed`. Use the combined entry point when
an assessed recommendation is required.

Safety phrases or road/drain issues mentioning schools/hospitals/playgrounds suggest
high; explicitly minor lighting/cosmetic complaints suggest low; others get medium.
Simple nearby negation is handled, but sarcasm, complex negation, resolved historical
hazards and mixed issues can be misread. Suggestions require citizen/officer review.
These rules do not verify location, severity, or actual proximity to facilities.

## Day 5: location and department routing

`location.route_complaint(category, latitude, longitude)` returns a RoutingResult
with department_code/name, ward_code/name, mode and reason. Call `.to_dict()` for
JSON-ready output. Coordinates must be numeric, finite and globally valid, or
both omitted. Unknown categories and partial/invalid coordinates raise ValueError.

Two SYNTHETIC rectangular demo zones are supplied, not official Pune boundaries:
DEMO-A: latitude [18.50,18.55), longitude [73.80,73.85).
DEMO-B: latitude [18.50,18.55), longitude [73.85,73.90).
Outside points return no ward (`outside_demo`); absent location returns `pending`.
Keep the demo label visible. The service does not call external APIs or PostGIS.
Naman owns persistence/API integration and should map the returned codes to seeded
Department/Ward records, leaving unresolved wards null rather than guessing.

Example: `route_complaint("pothole", 18.52, 73.82).to_dict()` routes to Roads and
Demo zone A. Shared edges belong to one zone only. Verified official polygons are
required before claiming municipal ward accuracy.
