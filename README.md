# FSDCvicLens

## Project Structure

```
FSDCvicLens/
├── client/                     # Frontend — Next.js (React + TypeScript)
│   ├── public/                 # Static assets
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── src/
│   │   └── app/                # App Router
│   │       ├── favicon.ico
│   │       ├── globals.css
│   │       ├── layout.tsx
│   │       └── page.tsx
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── package.json
│   ├── postcss.config.mjs
│   └── tsconfig.json
│
├── server/                     # Backend — Django
│   ├── config/                 # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── venv/                   # Python virtual environment (git-ignored)
│   ├── manage.py
│   └── requirements.txt
│
├── .gitignore
└── README.md
```
