# 🚀 ElevenDops: Multi-Service Migration Plan (MVP Optimized)

This document outlines the strategy for migrating ElevenDops to a modern, multi-service architecture designed for a **Quick Demonstration MVP**.

We will use a hybrid approach: **Python/Streamlit** for the internal Doctor tools and **React/Vite** for the patient-facing side.

## 1. Goal Architecture

- **Unified URL:** `https://elevendops-mvp.web.app` (via Firebase Hosting)
- **Routing Logic:**
  - `/api/*` → **FastAPI** (Cloud Run: `api-service`) - The "Brain" (Logics, ElevenLabs, Firestore)
  - `/doctor/*` → **Streamlit** (Cloud Run: `doctor-portal`) - The "Admin/Doctor Portal" (Document Upload & Testing)
  - `/*` → **React + Vite (TS)** (Firebase Hosting) - The "Patient Experience" (Chat, Voice AI, & Audio Education)

---

## 2. Why React/Vite for the Patient Frontend?

For a quick, high-impact demonstration, React (Vite/TS) is preferred over Next.js because:

- **Static Hosting:** The entire frontend builds into simple files that host for **free** on Firebase Hosting. No server maintenance.
- **Persistent Experience:** Being a Single Page Application (SPA), patients can listen to Education Audio in the background while navigating to a chat tab without the audio stopping.
- **Rapid Iteration:** Vite provides near-instant feedback during development.
- **Interactive Features:** Fully supports high-performance features like:
  - AI Agent Voice Interaction (via WebSockets/Microphone)
  - Real-time chat interfaces
  - Custom Audio Players for educational scripts

---

## 3. Structural Changes

Transform the current repository to support independent deployment cycles.

```text
ElevenDops/
├── backend/
│   └── Dockerfile             # Specialized for FastAPI (Uvicorn)
├── streamlit_app/
│   └── Dockerfile             # Specialized for Streamlit
├── patient_frontend/          # <-- NEW Vite + React + TypeScript Project
│   ├── src/
│   └── public/                # Static assets
├── firebase.json              # The "Traffic Controller" (Routing)
└── scripts/
    └── deploy_all.ps1         # One-click deployment script
```

---

## 4. Implementation Details

### Step 1: Decentralize Dockerfiles (Cloud Run)

Each container should do exactly one thing.

**`backend/Dockerfile`:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**`streamlit_app/Dockerfile`:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
```

### Step 2: The "Traffic Controller" (Firebase Hosting)

Create a `firebase.json` in the project root to link all services.

```json
{
  "hosting": {
    "public": "patient_frontend/dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "/api/**",
        "run": { "serviceId": "api-service", "region": "us-central1" }
      },
      {
        "source": "/doctor/**",
        "run": { "serviceId": "doctor-portal", "region": "us-central1" }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

### Step 3: Local Development with Cloud Resources

To test locally while controlling cloud resources:

1.  **GCP Service Account:** Export a JSON key for Firestore access.
2.  **Environment Variables:** Set `GOOGLE_APPLICATION_CREDENTIALS` and `ELEVENLABS_API_KEY` in your local `.env`.
3.  **Cross-Origin (CORS):** Ensure the FastAPI backend has CORS enabled to allow requests from `localhost:5173` (Vite's default port).

---

## 5. Future-Proofing

While we start with **Vite** for speed, the code structure (React/TS) allows for an easy transition to **Next.js** later if SEO or Server-Side Rendering becomes a priority. The UI components and API service logic can be copy-pasted with minimal changes.
