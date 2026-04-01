# SyncMyProfile.ai Documentation

## Overview

SyncMyProfile.ai is a FastAPI web application that:

- analyzes an uploaded LinkedIn profile PDF against a target role or job description
- transforms an uploaded resume into LinkedIn-ready content
- generates a LinkedIn profile from structured user input

The application renders server-side HTML with Jinja templates and uses Google Gemini for AI-powered analysis and profile generation.

## Project Structure

```text
app/
  main.py
  helpers/
  static/
  templates/
data/
  sessions/
  uploads/
docs/
logs/
requirements.txt
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables.

Create a local `.env` file from `.env.example` and set:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

If `GEMINI_API_KEY` is missing, the server still starts, but AI generation routes return a readable configuration error until the key is set.

## Run Locally

Use Uvicorn with the FastAPI app target:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Key Backend Components

### `app/main.py`

- boots the FastAPI app
- mounts static assets and templates
- handles uploads and page routes
- stores suggestion/error state in filesystem-backed sessions
- parses AI output for the results page

### `app/helpers/genai_utils.py`

- calls Gemini with retry logic
- validates that generated output contains the expected sections
- returns readable error strings when the API is unavailable or unconfigured

### `app/helpers/pdf_utils.py`

- extracts text from uploaded PDFs using PyMuPDF

### `app/helpers/session_utils.py`

- persists per-session state under `data/sessions/`

### `app/helpers/logging_utils.py`

- configures runtime logging
- makes console output resilient on Windows terminals
- writes detailed analysis logs to `logs/`

## Main Routes

- `GET /` and `GET /landing`: landing page
- `GET /select-service`: choose LinkedIn optimize, resume-to-LinkedIn, or profile creation
- `GET /start`: LinkedIn profile upload flow
- `GET /resume-start`: resume upload flow
- `GET /create-profile`: guided profile creation flow
- `POST /analyze`: AJAX-style analysis endpoint returning a redirect target
- `GET /suggestion`: renders the latest stored result
- `POST /suggestion`: analyzes and renders the result directly
- `POST /generate-profile`: creates a LinkedIn profile from form input

## Notes

- Uploaded PDFs are stored under `data/uploads/`.
- Session state is stored under `data/sessions/`.
- Analysis logs are written to `logs/`.
- Frontend assets are loaded from the `app/static/` directory and external CDNs used by the templates.
