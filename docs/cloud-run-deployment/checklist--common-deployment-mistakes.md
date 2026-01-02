# Common Cloud Deployment Mistakes Checklist

This document catalogs common mistakes made when deploying applications to serverless and cloud platforms. Use this as a pre-deployment audit checklist.

---

## 1. Debug & Development Endpoints

| ID        | Mistake                             | Risk                                                                                     | Verification Strategy                                                                        |
| --------- | ----------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `SEC-001` | Debug routes enabled in production  | **High**. Exposes internal trace data, execution logs, and can trigger costly LLM calls. | Grep for `/debug`, `/test`, `/mock` routes. Wrap with `if settings.app_env != 'production'`. |
| `SEC-002` | FastAPI `docs` or `redoc` exposed   | **Medium**. Reveals full API schema to attackers.                                        | Check for `openapi_url=None` or `docs_url=None` in `FastAPI()` constructor in production.    |
| `SEC-003` | Verbose error messages in responses | **Medium**. Stack traces leak internal paths and library versions.                       | Ensure global exception handlers return generic messages; log details server-side only.      |

---

## 2. API Keys & Secrets

| ID        | Mistake                                  | Risk                                                     | Verification Strategy                                                               |
| --------- | ---------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------- |
| `SEC-010` | Hardcoded API keys in source code        | **Critical**. Keys committed to Git are publicly leaked. | `grep -rE 'sk-                                                                      | AIza | AKIA' .`in codebase. Use Secret Manager or`.env` files (gitignored). |
| `SEC-011` | Secrets in client-side code (JS bundles) | **Critical**. Frontend code is publicly visible.         | Ensure all API calls requiring secrets are proxied via backend.                     |
| `SEC-012` | `.env` file committed to Git             | **Critical**. All secrets exposed in repo history.       | Check `.gitignore` includes `.env*`. Audit history with `git log -p -- .env`.       |
| `SEC-013` | Secrets logged in plaintext              | **High**. Secrets appear in Cloud Logging/CloudWatch.    | Search logs for key patterns `sk-`, `AKIA`, `Bearer`. Redact in logging middleware. |
| `SEC-014` | Default or weak secrets in staging       | **Medium**. Staging environments can be attacked.        | Rotate all keys for prod/staging separately.                                        |

---

## 3. Database Connectivity & Configuration

### Firestore / Firebase

| ID       | Mistake                                                                   | Risk                                                             | Verification Strategy                                                                             |
| -------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `DB-001` | Firestore rules set to `allow read, write: if true;`                      | **Critical**. Anyone can read/write all data.                    | Review `firestore.rules` before deploy. Use Firebase Emulator tests.                              |
| `DB-002` | Missing composite indexes                                                 | **Medium**. Queries fail silently or throw errors in production. | Test all queries against emulator; deploy indexes via `firebase deploy --only firestore:indexes`. |
| `DB-003` | Using Firestore in Datastore mode when Native mode needed (or vice-versa) | **High**. Application crashes or wrong query semantics.          | Check project mode in GCP Console → Firestore. Cannot be changed after creation.                  |

### MongoDB / Atlas

| ID       | Mistake                                             | Risk                                          | Verification Strategy                                                                |
| -------- | --------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------ |
| `DB-010` | Connection string includes `0.0.0.0/0` IP whitelist | **High**. Database open to the internet.      | Restrict IP access to Cloud Run egress IPs or use VPC peering.                       |
| `DB-011` | Missing indexes on frequently queried fields        | **Medium**. Slow queries and high read costs. | Use `explain()` on queries; create indexes for fields used in `find()` and `sort()`. |

### PostgreSQL / Cloud SQL

| ID       | Mistake                          | Risk                                             | Verification Strategy                                                                            |
| -------- | -------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `DB-020` | Public IP enabled without SSL    | **Critical**. Traffic can be intercepted.        | Enforce SSL via `sslmode=require` in connection string. Use Cloud SQL Proxy for internal access. |
| `DB-021` | Connection pool exhaustion       | **High**. App becomes unresponsive under load.   | Use connection pooler (PgBouncer) or limit connections in ORM (e.g., SQLAlchemy `pool_size`).    |
| `DB-022` | Migrations not run before deploy | **High**. Schema mismatch causes runtime errors. | Add migration step to CI/CD pipeline (`alembic upgrade head`).                                   |

### DynamoDB

| ID       | Mistake                                         | Risk                                                  | Verification Strategy                                           |
| -------- | ----------------------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------- |
| `DB-030` | Incorrect partition key design (hot partitions) | **High**. Throttling and latency spikes.              | Distribute writes across partitions; avoid timestamp-only keys. |
| `DB-031` | Scan operations on large tables                 | **High**. Expensive, slow, and consumes all capacity. | Use Query with indexes; avoid `scan()` in application code.     |

---

## 4. Authentication & Authorization

### Firebase Auth / Cognito

| ID         | Mistake                                     | Risk                                                | Verification Strategy                                                              |
| ---------- | ------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `AUTH-001` | Missing token verification on backend       | **Critical**. Anyone can forge requests.            | Verify ID tokens using Firebase Admin SDK or Cognito SDK on every protected route. |
| `AUTH-002` | Storing JWT in LocalStorage                 | **Medium**. XSS can steal tokens.                   | Use HttpOnly cookies for tokens where possible.                                    |
| `AUTH-003` | Not validating email before granting access | **Medium**. Unverified users access sensitive data. | Check `email_verified` claim in token before granting access.                      |
| `AUTH-004` | Overly permissive OAuth scopes              | **Medium**. Requesting more data than needed.       | Request only necessary scopes (e.g., `profile email` not `*`).                     |

### AWS AppSync / GraphQL

| ID         | Mistake                             | Risk                                                      | Verification Strategy                                               |
| ---------- | ----------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------- |
| `AUTH-010` | No authorization on resolvers       | **Critical**. All data exposed to any authenticated user. | Use `@auth` directive or VTL authorization logic in every resolver. |
| `AUTH-011` | Introspection enabled in production | **Medium**. Schema is exposed.                            | Disable introspection for production stage.                         |

---

## 5. Serverless Compute (Lambda, Cloud Functions, Cloud Run)

| ID         | Mistake                                     | Risk                                                     | Verification Strategy                                                                        |
| ---------- | ------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `COMP-001` | Cold start performance issues               | **Medium**. First request latency is high.               | Use Provisioned Concurrency (Lambda) or `min-instances=1` (Cloud Run). Profile startup time. |
| `COMP-002` | Missing health check endpoint               | **High**. Platform cannot determine container health.    | Implement `/health` or `/api/health` endpoint that returns 200 OK quickly.                   |
| `COMP-003` | Using ephemeral storage for persistent data | **Critical**. Data lost on container restart.            | Store files in GCS/S3; use Firestore/DynamoDB for state.                                     |
| `COMP-004` | Timeout too short for long operations       | **High**. Audio generation or file processing times out. | Increase timeout (Cloud Run: up to 3600s, Lambda: up to 900s).                               |
| `COMP-005` | Memory too low for application              | **High**. OOMKilled errors.                              | Monitor memory usage; increase allocation (Lambda/Cloud Run memory setting).                 |

### AWS Fargate / App Runner

| ID         | Mistake                          | Risk                                                       | Verification Strategy                                                               |
| ---------- | -------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `COMP-010` | Exposing container on wrong port | **High**. Service unreachable.                             | Ensure `PORT` env var matches `EXPOSE` in Dockerfile and App Runner/Fargate config. |
| `COMP-011` | No graceful shutdown handling    | **Medium**. In-flight requests dropped during deployments. | Handle `SIGTERM` in application; allow 10s for cleanup.                             |

---

## 6. Storage (GCS, S3)

| ID         | Mistake                            | Risk                                         | Verification Strategy                                                |
| ---------- | ---------------------------------- | -------------------------------------------- | -------------------------------------------------------------------- |
| `STOR-001` | Bucket set to public               | **Critical**. All files publicly accessible. | Check IAM policy; remove `allUsers` or `allAuthenticatedUsers`.      |
| `STOR-002` | No lifecycle policy for temp files | **Medium**. Storage costs grow unbounded.    | Configure auto-delete policy for objects older than N days.          |
| `STOR-003` | Signed URLs with excessive expiry  | **Medium**. Links remain valid too long.     | Set expiry to minimum needed (e.g., 15 minutes for downloads).       |
| `STOR-004` | CORS misconfigured                 | **Medium**. Frontend cannot access files.    | Verify CORS allows your frontend origin; test with browser devtools. |

---

## 7. CI/CD & Deployment

| ID         | Mistake                       | Risk                                                    | Verification Strategy                                                                  |
| ---------- | ----------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `CICD-001` | Secrets printed in build logs | **High**. Secrets visible in CI output.                 | Use secret masking in GitHub Actions, Cloud Build substitutions, etc.                  |
| `CICD-002` | No rollback strategy          | **High**. Bad deploy leaves app broken.                 | Use Cloud Run traffic splitting, Lambda aliases, or App Runner revisions for rollback. |
| `CICD-003` | Deploying from local machine  | **Medium**. Inconsistent builds and credential leakage. | Always deploy via CI/CD pipeline, not local `gcloud run deploy`.                       |

---

## 8. CORS & Network Security

| ID        | Mistake                                  | Risk                                                           | Verification Strategy                                                       |
| --------- | ---------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `NET-001` | CORS set to `*`                          | **High**. Any website can call your API.                       | Restrict `Access-Control-Allow-Origin` to specific domains.                 |
| `NET-002` | `allow_credentials=True` with `*` origin | **Critical**. Browser blocks this, but indicates config error. | If credentials needed, list specific origins, not `*`.                      |
| `NET-003` | Missing rate limiting                    | **Medium**. API can be DDoS'd or abused.                       | Implement rate limiting via API Gateway, Cloud Armor, or in-app middleware. |

---

## 9. Logging & Monitoring

| ID        | Mistake                           | Risk                                              | Verification Strategy                                              |
| --------- | --------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------ |
| `LOG-001` | Logging sensitive data (PII, PHI) | **Critical**. Compliance violation (GDPR, HIPAA). | Audit log statements; use log redaction.                           |
| `LOG-002` | No alerting on errors             | **Medium**. Issues go unnoticed.                  | Set up Cloud Monitoring or CloudWatch alerts for 5xx errors.       |
| `LOG-003` | Logs not structured (plain text)  | **Low**. Harder to query and analyze.             | Use structured JSON logging for Cloud Logging/CloudWatch Insights. |

---

## 10. Platform-Specific Pitfalls

### Vercel

| ID        | Mistake                                    | Risk                            | Verification Strategy                                      |
| --------- | ------------------------------------------ | ------------------------------- | ---------------------------------------------------------- |
| `VER-001` | Serverless function timeout (10s on Hobby) | **High**. Long operations fail. | Use background jobs or upgrade to Pro for longer timeouts. |
| `VER-002` | Edge functions accessing unsupported APIs  | **Medium**. Runtime errors.     | Use Node.js runtime if full Node API needed.               |

### AWS Amplify

| ID        | Mistake                              | Risk                                              | Verification Strategy                         |
| --------- | ------------------------------------ | ------------------------------------------------- | --------------------------------------------- |
| `AMP-001` | Amplify CLI credentials overly broad | **Medium**. IAM role can access more than needed. | Custom IAM role with least privilege.         |
| `AMP-002` | Not using environment separation     | **Medium**. Prod and dev share resources.         | Use Amplify environments (`amplify env add`). |

---

## Quick Audit Commands

```bash
# Search for hardcoded secrets
grep -rE '(sk-|AIza|AKIA|password=|secret=)' --include='*.py' --include='*.js' --include='*.ts' .

# Check for debug routes
grep -rn '/debug' --include='*.py' .

# Check for overly permissive CORS
grep -rn "allow_origins=\['\*'\]" --include='*.py' .

# Check Firestore rules for open access
grep -n "allow read, write: if true" firestore.rules

# Verify .env is gitignored
git check-ignore .env && echo "OK: .env is ignored" || echo "WARN: .env is NOT ignored"
```

---

## References

- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices)
- [AWS Lambda Security Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)
- [Firebase Security Rules Guide](https://firebase.google.com/docs/rules)
- [OWASP Serverless Top 10](https://owasp.org/www-project-serverless-top-10/)
