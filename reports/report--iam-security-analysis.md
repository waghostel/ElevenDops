# IAM Security Analysis Report

**Project**: `elevendops-dev`  
**Date**: 2026-01-17  
**Service Account Analyzed**: `721904174352-compute@developer.gserviceaccount.com`

---

## Current IAM Bindings

### Project-Level Roles (Compute SA)

| Role                                   | Strictness          | Assessment                                                                                                  |
| :------------------------------------- | :------------------ | :---------------------------------------------------------------------------------------------------------- |
| `roles/editor`                         | ⚠️ **OVERLY BROAD** | Grants broad write access to most GCP services. Should be replaced with specific roles.                     |
| `roles/datastore.user`                 | ✅ Appropriate      | Required for Firestore read/write.                                                                          |
| `roles/storage.objectAdmin`            | ⚠️ Could be tighter | Grants full object control. Consider `storage.objectViewer` + `storage.objectCreator` if delete not needed. |
| `roles/secretmanager.secretAccessor`   | ✅ Appropriate      | Read-only access to secrets. Minimal required permission.                                                   |
| `roles/iam.serviceAccountTokenCreator` | ✅ Appropriate      | Required for signed URL generation.                                                                         |

### Service Account-Level Bindings

| Binding                                      | Assessment                   |
| :------------------------------------------- | :--------------------------- |
| Self-impersonation (Token Creator on itself) | ✅ Required for signBlob API |

---

## Security Findings

### 🔴 Critical: `roles/editor` is Too Broad

**Issue**: The default Compute Engine service account has `roles/editor`, which:

- Grants write access to nearly all GCP resources
- Allows creating/modifying Cloud Storage buckets, Compute instances, etc.
- Violates the principle of least privilege

**Risk**: If the Cloud Run service is compromised, an attacker could:

- Create new resources (cost impact)
- Modify other services in the project
- Access resources beyond what the app needs

**Recommendation**: Remove `roles/editor` and keep only the specific roles required.

```bash
# Remove overly broad editor role
gcloud projects remove-iam-policy-binding elevendops-dev `
    --member="serviceAccount:721904174352-compute@developer.gserviceaccount.com" `
    --role="roles/editor"
```

### 🟡 Moderate: `storage.objectAdmin` Could Be Tighter

**Current**: Full control over all objects in all buckets.

**Recommended Alternative**: If deletion is only needed for specific features, consider:

1. Keep `objectAdmin` only if audio deletion is a core feature
2. Otherwise, use `storage.objectCreator` + `storage.objectViewer`

**Bucket-Level Scoping**: For production, consider IAM at the **bucket level** instead of project level:

```bash
# Bucket-specific permission (more secure)
gsutil iam ch serviceAccount:721904174352-compute@developer.gserviceaccount.com:objectAdmin gs://elevendops-bucket
```

---

## Recommended Minimal Permissions

For a strict least-privilege Cloud Run deployment, use only these roles:

| Role                                   | Purpose                    |
| :------------------------------------- | :------------------------- |
| `roles/datastore.user`                 | Firestore read/write       |
| `roles/storage.objectAdmin`            | GCS read/write/delete      |
| `roles/secretmanager.secretAccessor`   | Read API keys              |
| `roles/iam.serviceAccountTokenCreator` | Sign URLs (project + self) |

**Optionally remove**:

- `roles/editor` - Not needed with specific roles above

---

## Action Items

1. **[Critical]** Remove `roles/editor` from the Compute SA
2. **[Optional]** Scope storage permissions to bucket level (instead of project level)
3. **[Optional]** Create a dedicated service account for Cloud Run instead of using the default Compute SA

---

## Verification Commands

```bash
# Check current roles for Compute SA
gcloud projects get-iam-policy elevendops-dev --flatten="bindings[].members" `
    --format="table(bindings.role)" `
    --filter="bindings.members:721904174352-compute@developer.gserviceaccount.com"

# Check self-impersonation binding
gcloud iam service-accounts get-iam-policy 721904174352-compute@developer.gserviceaccount.com `
    --project=elevendops-dev
```
