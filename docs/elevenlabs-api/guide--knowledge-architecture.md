# Knowledge Base Architecture & Integration

This document details how the ElevenDops system integrates with ElevenLabs Knowledge Base, explaining the hybrid storage model, synchronization flows, and ownership boundaries.

## 1. Hybrid Storage Architecture

We utilize a **Hybrid Storage Model** where the data is split between our local database (Firestore) and the external AI service (ElevenLabs).

| Feature                  | Storage Location                      | Purpose                                                     | Source of Truth |
| :----------------------- | :------------------------------------ | :---------------------------------------------------------- | :-------------- |
| **Metadata & Ownership** | **Firestore** (`knowledge_documents`) | Managing permissions, UI display, edit history.             | ✅ Yes          |
| **Raw Content**          | **Firestore**                         | Backup, editing, regenerating stats.                        | ✅ Yes          |
| **Vector Embeddings**    | **ElevenLabs**                        | Semantic search (RAG) for the AI Agent during conversation. | ❌ No (derived) |
| **Agent Links**          | **Multiple**                          | Connecting docs to bots; tracked locally for sync safety.   | Firestore       |

### Why this split?

- **Performance:** The UI lists documents instantly from Firestore without querying the slower external API.
- **Resilience:** If ElevenLabs is down or a sync fails, we still possess the original data to retry.
- **Cost & Limits:** We avoid unnecessary API calls for simple management tasks (renaming, tagging).

---

## 2. Synchronization Lifecycle

The system treats Firestore as the "Master" and ElevenLabs as a "Replica". Changes propagate **one-way** from App -> ElevenLabs.

### Upload Flow (Create)

1.  **User Uploads File:** Content is saved to Firestore immediately with status `PENDING`.
2.  **Background Task:** System triggers an async job to call ElevenLabs API (`create_document`).
3.  **State Update:**
    - _Success:_ Firestore document updated to `COMPLETED`, ElevenLabs ID saved.
    - _Failure:_ Firestore document updated to `FAILED` with error message.

### Edit Flow (Update)

Editing a document's `raw_content` triggers a re-sync:

1. **Detection:** System checks if the document is currently linked to any ElevenLabs Agents.
2. **Safety Detach:** If linked, the document is temporarily detached from those agents (ElevenLabs prevents deleting "in-use" documents).
3. **Replacement:** The old document is deleted from ElevenLabs, and the new content is uploaded as a fresh document.
4. **Re-attach:** If it was previously linked, the new document ID is automatically re-attached to the original agents.

### Deletion Flow (Delete)

1.  **User Deletes File:** User requests deletion in UI.
2.  **Agent-aware Cleanup:**
    - The system checks for active agent links.
    - It detaches the document from all agents in ElevenLabs.
3.  **Dual Deletion:**
    - **ElevenLabs:** API call sent to remove the document from the Knowledge Base.
    - **Firestore:** Document record is permanently removed.

---

## 3. Maintenance & Reconciliation

To ensure the systems never drift apart (e.g., due to API timeouts or manual edits in the console), we provide a **Reconciliation Tool**.

### CLI Tool: `reconcile--elevenlabs-knowledge.py`

Located in the `scripts/` directory, this tool allows for manual audit and repair.

| Mode             | Usage                                                       | Description                                               |
| :--------------- | :---------------------------------------------------------- | :-------------------------------------------------------- |
| `--audit`        | `python scripts/reconcile--elevenlabs-knowledge.py --audit` | **Safe.** Prints a report of Orphans vs Unsynced docs.    |
| `--fix-orphans`  | `python scripts/reconcile... --fix-orphans`                 | Deletes ElevenLabs docs that don't exist in Firestore.    |
| `--fix-unsynced` | `python scripts/reconcile... --fix-unsynced`                | Re-uploads Firestore docs that are missing in ElevenLabs. |

> [!TIP]
> Run `--audit` periodically to check for "Ghost" documents that might be consuming your 20MB ElevenLabs storage quota.

---

## 4. Ownership & Usage

ElevenLabs itself works as a flat list of documents. We enforce logic and relationships layer on top via Firestore.

### A. Ownership (`doctor_id`)

- **ElevenLabs:** Knows nothing about "Users". All documents belong to the API Key owner.
- **Firestore:** Every `knowledge_document` has a `doctor_id` field.
- **Application Logic:** The API filters queries by `doctor_id` so User A cannot see or use User B's documents, even though they technically reside in the same ElevenLabs account.

### B. Agent Linking

- **ElevenLabs:** An Agent is linked to specific Document IDs.
- **App Logic:** We replicate this link in our `agents` collection (`knowledge_ids` array).
- **Usage Check:** To see if a document is "in use", we query our local `agents` collection, avoiding expensive API traversals.

---

## 4. Limits & Quotas

Since we are dependent on the ElevenLabs infrastructure, the following hard limits apply:

| Limit Type              | Constraint                  | Implication                                                                          |
| :---------------------- | :-------------------------- | :----------------------------------------------------------------------------------- |
| **Knowledge Base Size** | Max **20MB** or ~300k chars | (Std Account) Total size of all synced docs cannot exceed this.                      |
| **Document Size**       | Min **500 bytes**           | Very short texts may be rejected or not indexed for RAG.                             |
| **Retention**           | **Indefinite**              | Documents stay until explicitly deleted.                                             |
| **Sync Speed**          | **Async**                   | Documents are not instantly available for chat; usually takes 3-10 seconds to index. |

### Handling Limits

If the 20MB limit is reached, the `sync_status` in Firestore will transition to `FAILED` with a `Quota Exceeded` error message. The user must delete old documents to free up space.
