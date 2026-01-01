# Security Risk Analysis Report: Cloud Run Deployment

**Date:** 2026-01-01
**Target Environment:** Google Cloud Run (Production)
**Assessment Status:** 🔴 CRITICAL RISKS IDENTIFIED

## Executive Summary

The current configuration deploys the ElevenDops application as a **publicly accessible service** without authentication. While the backend API is correctly isolated from the internet (internal-only), the Streamlit frontend exposes all functionality and data to anyone with the Cloud Run URL.

**Deployment is NOT RECOMMENDED for production use with real patient data until authentication is implemented.**

---

## 🚨 Critical Risks (Must Fix)

### 1. Unauthenticated Public Access to Patient Data

- **Severity:** Critical
- **Vulnerability:** The Streamlit application (`app.py`) has no login mechanism.
- **Impact:** The **Conversation Logs** page (`6_Conversation_Logs.py`) allows anyone to search for and view full patient transcripts, audio recordings, and medical analysis.
- **Compliance Violation:** This is a direct violation of HIPAA, GDPR, and other medical data privacy regulations.

### 2. Unrestricted Access to Paid APIs

- **Severity:** High
- **Vulnerability:** "Education Audio" and "Agent Setup" pages trigger calls to ElevenLabs and Google Gemini APIs.
- **Impact:** Malicious users could automate requests to these endpoints, rapidly depleting your API quotas and incurring significant financial costs (Denial of Wallet attack).

### 3. Open Knowledge Base Management

- **Severity:** High
- **Vulnerability:** The "Upload Knowledge" page allows any visitor to upload, index, and potentially delete medical documents.
- **Impact:** Unauthorized users can pollute the knowledge base with false information, which the AI agents would then provide to patients.

---

## ⚠️ Moderate Risks

### 1. Cross-Site Scripting (Reflected)

- **Severity:** Medium
- **Vulnerability:** Streamlit apps can sometimes be vulnerable to reflected XSS if user input is rendered unsanitized. While Streamlit handles most of this, custom HTML components (used in chat bubbles) need careful review.
- **Location:** `6_Conversation_Logs.py` renders HTML for chat bubbles using `unsafe_allow_html=True`.

### 2. Lack of Audit Trail

- **Severity:** Medium
- **Vulnerability:** Without user identities (User ID/Email), it is impossible to track _who_ accessed a patient record or _who_ generated an audio file.
- **Impact:** Inability to investigate security incidents or data breaches.

---

## ✅ Secured Components (Good Practices Identified)

The following security controls are correctly implemented:

1.  **Container Security**:

    - Runs as non-root user (`appuser`).
    - Uses minimal base image (`python:3.11-slim`).
    - Emulators disabled in production.

2.  **Network Architecture**:

    - **Backend API** listens on `localhost` only, inaccessible from the public internet.
    - **HTTPS** is enforced by Cloud Run default.
    - **Secrets** are managed via Secret Manager, not hardcoded.

3.  **Authentication (Infrastructure)**:
    - Service Account has least-privilege roles (`datastore.user`, `storage.objectAdmin`).

---

## Recommendations & Remediation Plan

### Immediate Actions (Before Production Launch)

1.  **Enable Cloud Run Authentication:**

    - **Action:** Remove `--allow-unauthenticated` from `service.yaml` and `cloudbuild.yaml`.
    - **Effect:** Only users with GCP IAM permissions (e.g., your organization's Google Accounts) can access the URL. This is the fastest fix for internal tools.

2.  **Implement Application-Level Authentication:**

    - **Action:** Integrate `streamlit-authenticator` or a custom OAuth2 wrapper (e.g., Google Sign-In) within `app.py`.
    - **Effect:** Provides proper login screen for doctors/admins.

3.  **Sanitize Chat Rendering:**
    - **Action:** Ensure content in `6_Conversation_Logs.py` is HTML-escaped before being inserted into `unsafe_allow_html` blocks.

### Long-Term Improvements

1.  **Role-Based Access Control (RBAC):**

    - Differentiate between "Admin" (can upload knowledge) and "Viewer" (can only read logs).

2.  **WAF Implementation:**
    - Deploy Cloud Load Balancing with Cloud Armor in front of Cloud Run to prevent bot attacks and rate-limit IP addresses.
