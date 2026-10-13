# Day 7: local speech transcription

Run from `server` in PowerShell (Python 3.10+):

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -c "from faster_whisper.utils import download_model; download_model('base', output_dir='models/whisper-base')"
.\venv\Scripts\python.exe manage.py runserver
```

The multilingual base model downloads once. Model files are ignored by Git.
Optionally set `CIVICLENS_WHISPER_MODEL` to an existing local model directory.
Runtime inference uses CPU/int8 and does not download models or send audio to a service.

Authenticated `POST /api/ai/transcribe/`: multipart `audio` and `language` (`en`, `hi`, `mr`).
Fetch `/api/complaints/csrf/` and pass `X-CSRFToken` with the session cookie.
Response: `text`, `language`, `duration_seconds`, `method`.
Limits: 10 MB, 60 decoded seconds; invalid audio is rejected by the decoder.
Statuses: 400 invalid input, 401 sign-in required, 403 CSRF, 413 oversized,
422 no speech, 503 unavailable model or busy inference.
Audio is not saved as complaint media. Users must review/edit the transcript before applying it.

Base-model accuracy varies, especially Hindi/Marathi and noisy recordings. Selected
language is an explicit decoding hint, not automatic language detection. Transcription
preserves the spoken language; translation still uses the separate Day 6 service.
Production deployments should also configure request-size limits and rate limiting.

Implementation follows https://github.com/SYSTRAN/faster-whisper .
