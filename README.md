# CivicLens

A college prototype for reporting civic issues using text, voice, photos and location,
with officer assignment, evidence-based resolution, notifications and citizen feedback.

## Stack
Next.js/React/TypeScript, Django, SQLite, local faster-whisper speech transcription.
Text classification uses a small Naive Bayes model; priority uses explainable rules.

## Local setup (PowerShell)
1. Install Python 3.10+ and a Node version supported by the installed Next.js release.
2. In server: python -m venv venv
3. .\venv\Scripts\python.exe -m pip install -r requirements.txt
4. .\venv\Scripts\python.exe manage.py migrate
5. .\venv\Scripts\python.exe manage.py seed_routing
6. .\venv\Scripts\python.exe manage.py createsuperuser
7. .\venv\Scripts\python.exe manage.py runserver
8. In a second terminal, from client: npm install; npm run dev
9. Open http://localhost:3000. Create a citizen account. Use the staff account for /officer.

The client forwards /api to Django on 127.0.0.1:8000. Use localhost consistently.
Read server/ai_engine/SPEECH_SETUP.md for the one-time Whisper download and
server/ai_engine/TRANSLATION_SETUP.md for Azure Translator environment setup.
Do not commit credentials, models, SQLite databases or uploaded files.

## Demo
Report a pothole at latitude 18.52, longitude 73.82 using photo and reviewed voice/text.
Check AI/duplicate suggestions. Officer verifies, assigns a matching demo worker,
starts work, uploads evidence and resolves with a note. Citizen opens the notification,
views evidence, rates the result, and optionally reopens for reassignment.

## Verification
Server: .\venv\Scripts\python.exe manage.py showcase_check
Server: .\venv\Scripts\python.exe manage.py test
Server: .\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
Client: npm run lint
Client: npx tsc --noEmit
Client: npm run build

## Limits
This is a local demo, not a production deployment or municipal integration.
Ward bounds and the 72-hour overdue rule are demonstration data/policy.
Duplicate suggestions use word overlap and distance, not semantic cross-language AI.
Nearby issues are a privacy-limited list, not a map. Notifications are in-app, not push/SMS.
Images are stored evidence; no image-recognition model is implemented.
English translation requires configured credentials. When unavailable, Hindi/Marathi reports
get labelled local keyword suggestions without a fabricated translation. Speech accuracy depends on audio.
The installable app includes a public offline screen. Explicit account-scoped device drafts save
text/location, not photos/audio, and must be restored and submitted manually after reconnecting.
Authenticated pages and API responses are never cached by the service worker.
Full offline synchronization, duplicate linking/upvotes, full UI translation and production
deployment remain future work. Only describe features actually verified in the current checkout.

## Showcase checklist

1. Run `manage.py showcase_check` from the server environment before the presentation.
2. Keep both Django and Next.js running; an offline screen does not mean the backend is running.
3. Use separate browser profiles/private windows for citizen and officer accounts.
4. Demonstrate text/photo/GPS reporting, suggestions, assignment, evidence, resolution and feedback.
5. For locations outside demo zones, use **Set department and ward manually** before assigning.
6. Record a short microphone sample on the presenting laptop; browser permissions require localhost or HTTPS.
7. Demonstrate **Save draft**, refresh, and **Restore draft** if needed. Clear the saved draft afterward.
8. Installation availability depends on the browser. Load the app once online before showing the offline screen.
9. No Google font download is needed for the build. The speech model must be downloaded once separately.

Do not claim image recognition, official government routing, push/SMS delivery, or production hosting.
Uploaded images are evidence and nearby results are private-data-limited summaries.
