# Migrating to Real Google Cloud Platform (GCP) Services

This guide provides a step-by-step plan to switch your local ElevenDops environment from using local emulators (Firestore, GCS) to using real Google Cloud Platform services, while still running the application locally on `localhost`.

## Prerequisites

- A [Google Cloud Platform](https://console.cloud.google.com/) account.
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`) installed and accessible in your terminal.
- A functional ElevenDops local environment.

---

## Step 1: GCP Project Setup

1.  **Create a New Project** (or use an existing one):

    - Go to the [GCP Console](https://console.cloud.google.com/).
    - Create a new project (e.g., `elevendops-dev`).
    - Note down your **Project ID** (e.g., `elevendops-dev-123456`).

2.  **Enable Billing**:

    - Ensure billing is enabled for your project (required for some APIs).

3.  **Enable APIs**:
    - Go to **APIs & Services > Library**.
    - Search for and enable the following APIs:
      - **Cloud Firestore API**
      - **Cloud Storage API**
      - **Identity and Access Management (IAM) API**

---

## Step 2: Configure GCP Services

### Firestore

1.  Go to the [Firestore Console](https://console.cloud.google.com/firestore).
2.  Click **Create Database**.
3.  Select **Native Mode** (Recommended for this project).
4.  Choose a **Location** (e.g., `asia-east1` or `us-central1`) that is close to you.
5.  **Security Rules**: For development, start with **Test mode** (open to internet for 30 days) to avoid immediate permission issues, but move to Production mode with proper rules later.

### Cloud Storage

1.  Go to the [Cloud Storage Console](https://console.cloud.google.com/storage).
2.  **Create a Bucket**:
    - Name: Must be globally unique (e.g., `elevendops-audio-dev-[your-name]`).
    - defaults are usually fine for development.
    - Note down the **Bucket Name**.

---

## Step 3: Local Authentication

Instead of downloading long-lived service account keys (which are a security risk), we will use **Application Default Credentials (ADC)** via the `gcloud` CLI. This effectively logs your local machine in as "you" against the GCP project.

1.  Open your terminal.
2.  Login to GCP:
    ```bash
    gcloud auth login
    ```
3.  Set your active project:
    ```bash
    gcloud config set project [YOUR_PROJECT_ID]
    ```
4.  Acquire Application Default Credentials:
    ```bash
    gcloud auth application-default login
    ```
    - A browser window will open. Sign in with your Google account and allow access.
    - This creates a JSON credential file in a well-known location that the Google Cloud client libraries (used in our backend) automatically detect.

---

## Step 4: Update Local Configuration

Update your `.env` file to tell the ElevenDops application to stop using emulators and start using the real services.

1.  Open `.env` in your project root.
2.  Update the following variables:

```dotenv
# ===========================================
# Firestore Configuration
# ===========================================
# Disable the emulator
USE_FIRESTORE_EMULATOR=false
# (Optional) Comment out host, it won't be used
# FIRESTORE_EMULATOR_HOST=localhost:8080

# Set your REAL Project ID
GOOGLE_CLOUD_PROJECT=[YOUR_PROJECT_ID]

# ===========================================
# GCS Configuration
# ===========================================
# Disable the emulator
USE_GCS_EMULATOR=false
# (Optional) Comment out host
# GCS_EMULATOR_HOST=http://localhost:4443

# Set your REAL Bucket Name
GCS_BUCKET_NAME=[YOUR_BUCKET_NAME]
```

---

## Step 5: Verification

1.  **Restart the Backend**:

    - If you are running via `docker-compose`, you might want to stop the emulators (`docker-compose down`) and run just the app, usually:
      ```bash
      # Run backend locally
      uv run fastapi dev backend/main.py
      ```
      or if you are using the full docker compose setup, ensure your `.env` is passed through, but note that `gcloud auth application-default login` creds (saved in your user home dir) might not be automatically mounted into Docker containers unless you map the volume.

    > **Recommendation**: For this hybrid "Local Code + Real Cloud" setup, it is often easiest to run the backend Python code **directly on your host machine** (using `uv run ...`) rather than inside Docker, so it automatically inherits your user's `gcloud` credentials.

2.  **Test the App**:
    - Start the frontend: `uv run streamlit run streamlit_app/Home.py`
    - Go to **Agent Setup** or **Education Audio**.
    - Perform an action (create an agent, upload a file).
    - Check the [GCP Console](https://console.cloud.google.com/) (Firestore Data or Storage Browser) to verify the data was actually created in the cloud.

---

## Troubleshooting

- **Permissions Error**: Ensure your Google Account (the one you logged in with) has `Editor` or `Owner` role on the GCP Project, or at least `Firestore Admin` and `Storage Admin`.
- **"Credentials not found" in Docker**: If running in Docker, you must mount the ADC credentials file.
  - Linux/Mac: `~/.config/gcloud/application_default_credentials.json`
  - Windows: `%APPDATA%/gcloud/application_default_credentials.json`
  - Map this to `/root/.config/gcloud/application_default_credentials.json` in the container and set `GOOGLE_APPLICATION_CREDENTIALS` env var to that path.
