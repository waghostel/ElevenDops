# Knowledge Base Architecture & Integration

This document details how the ElevenDops system integrates with ElevenLabs Knowledge Base, explaining the hybrid storage model, synchronization flows, and ownership boundaries.

## 1. Hybrid Storage Architecture

We utilize a **Hybrid Storage Model** where the data is split between our local database (Firestore) and the external AI service (ElevenLabs).

| Feature                  | Storage Location                      | Purpose                                                     | Source of Truth |
| :----------------------- | :------------------------------------ | :---------------------------------------------------------- | :-------------- |
| **Metadata & Ownership** | **Firestore** (`knowledge_documents`) | Managing permissions, UI display, edit history.             | ✅ Yes          |
| **Raw Content**          | **Firestore**                         | Backup, displaying content to user, regenerating stats.     | ✅ Yes          |
| **Vector Embeddings**    | **ElevenLabs**                        | Semantic search (RAG) for the AI Agent during conversation. | ❌ No (derived) |
| **Generated Audio**      | **GCS Bucket**                        | Storing final Text-to-Speech output files.                  | N/A             |

### Why this split?

- **Performance:** The UI lists documents instantly from Firestore without querying the slower external API.
- **Resilience:** If ElevenLabs is down or a sync fails, we still possess the original data to retry.
- **Cost & Limits:** We avoid unnecessary API calls for simple management tasks (renaming, tagging).

---

## 2. Synchronization Lifecycle

The system treats Firestore as the "Master" and ElevenLabs as a "Replica". Changes propagate **one-way** from App -> ElevenLabs.

### Upload Flow

1.  **User Uploads File:** Content is saved to Firestore immediately with status `PENDING`.
2.  **Background Task:** System triggers an async job to call ElevenLabs API (`create_document`).
3.  **State Update:**
    - _Success:_ Firestore document updated to `COMPLETED`, ElevenLabs ID saved.
    - _Failure:_ Firestore document updated to `FAILED` with error message.

### Deletion Flow

1.  **User Deletes File:** User requests deletion in UI.
2.  **Firestore Query:** System identifies the `elevenlabs_document_id`.
3.  **Dual Deletion:**
    - **ElevenLabs:** API call sent to remove the vector store entry. (Errors here are logged but swallowed to prevent blocking).
    - **Firestore:** Document record is permanently deleted.

---

## 3. Ownership & Usage

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
