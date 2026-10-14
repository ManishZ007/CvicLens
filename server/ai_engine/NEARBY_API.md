# Nearby reports and duplicate suggestions

Both endpoints require a signed-in session. Responses use `Cache-Control: private, no-store`.

## Duplicate suggestions

`POST /api/ai/duplicates/` with JSON and `X-CSRFToken` from `/api/complaints/csrf/`:

```json
{"text":"Large pothole near school","category":"pothole","latitude":18.52,"longitude":73.82}
```

Returns `results`, `truncated`, `method`, `radius_metres`, `lookback_days`, and
`automatic_merge: false`. Each suggestion contains `id`, `category`, `status`,
`created_at`, rounded `distance_metres` and `similarity`.

The baseline checks open reports of the same category from the past 30 days, within
200 metres. Similarity is the intersection divided by the union of Unicode word sets,
with a 0.35 cutoff; it is **not a probability or semantic model score**. Up to five
suggestions are returned. Hindi/Marathi combining marks are preserved, but input is
not translated and reports in different languages may not match.

## Nearby list

`GET /api/ai/nearby/?latitude=18.52&longitude=73.82`

Returns up to 50 open report summaries within 2 km, from the past 30 days, sorted
by distance. Includes the same metadata without `similarity`.

Neither endpoint returns reporter information, descriptions, photos, or precise
coordinates. An ID is not authorization to read another citizen's complaint.
Do not link these IDs to private detail pages for other citizens.

Both scans are capped at 1000 recent latitude-band candidates. `truncated` warns
when this cap or the nearby-list result limit hides records. A negative duplicate
check does not prove that the issue is new. No complaints are created, merged or
linked by either endpoint. Users may still submit separate issues.

Errors: 400 invalid input; 401 unauthenticated; 403 missing/invalid CSRF on POST.
