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
Translation requires configured credentials; transcription accuracy depends on language/audio quality.
Full offline synchronization, duplicate linking/upvotes, full UI translation and production
deployment remain future work. Only describe features actually verified in the current checkout.
