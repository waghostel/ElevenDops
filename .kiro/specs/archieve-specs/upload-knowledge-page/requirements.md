# Requirements Document

## Introduction

This specification defines the Upload Knowledge feature for the ElevenDops medical assistant system. The feature enables doctors to upload medical education documents (Markdown or TXT format) that will be stored in Firestore and synchronized to ElevenLabs Knowledge Base for use by AI agents in patient consultations.

## Glossary

- **Knowledge Document**: A medical education document containing information about diseases, treatments, or care instructions
- **ElevenLabs Knowledge Base**: External service that stores document copies for AI agent retrieval
- **Sync Status**: The synchronization state between Firestore (primary) and ElevenLabs (secondary)
- **Document Type**: Classification of knowledge content (FAQ, Post-operative Care, Precautions)
- **Firestore**: Google Cloud NoSQL database serving as the primary data source
- **Backend API**: FastAPI service handling business logic and external integrations

## Requirements

### Requirement 1

**User Story:** As a doctor, I want to upload medical education documents, so that I can build a knowledge base for AI-assisted patient consultations.

#### Acceptance Criteria

1. WHEN a doctor uploads a file THEN the System SHALL accept only Markdown (.md) or plain text (.txt) file formats
2. WHEN a doctor uploads a file exceeding 300KB THEN the System SHALL reject the upload and display a size limit error message
3. WHEN a valid file is uploaded THEN the System SHALL display a preview of the file content before submission
4. WHEN a doctor submits a document without a disease name THEN the System SHALL prevent submission and indicate the required field

### Requirement 2

**User Story:** As a doctor, I want to categorize my uploaded documents by disease and type, so that I can organize my knowledge base effectively.

#### Acceptance Criteria

1. WHEN uploading a document THEN the System SHALL require a disease name input field
2. WHEN uploading a document THEN the System SHALL provide document type selection with options: FAQ, Post-operative Care, Precautions
3. WHEN a document is saved THEN the System SHALL store the disease name and document type as metadata

### Requirement 3

**User Story:** As a doctor, I want my documents to be synchronized to ElevenLabs Knowledge Base, so that AI agents can access the information during patient conversations.

#### Acceptance Criteria

1. WHEN a doctor clicks "Save & Sync" THEN the System SHALL first store the document in Firestore
2. WHEN Firestore storage succeeds THEN the System SHALL initiate synchronization to ElevenLabs Knowledge Base
3. WHEN synchronization completes successfully THEN the System SHALL update the sync status to "completed" and store the ElevenLabs document ID
4. IF synchronization fails THEN the System SHALL retain the Firestore document and set sync status to "failed"
5. WHEN sync status is "failed" THEN the System SHALL provide a manual retry synchronization option

### Requirement 4

**User Story:** As a doctor, I want to view all my uploaded documents, so that I can manage my knowledge base.

#### Acceptance Criteria

1. WHEN the Upload Knowledge page loads THEN the System SHALL display a list of all uploaded documents
2. WHEN displaying documents THEN the System SHALL show: disease name, document type, sync status, and creation date
3. WHEN a document has sync status "completed" THEN the System SHALL display a green status indicator
4. WHEN a document has sync status "failed" THEN the System SHALL display a red status indicator with retry option
5. WHEN a document has sync status "pending" or "syncing" THEN the System SHALL display a yellow/orange status indicator

### Requirement 5

**User Story:** As a doctor, I want to delete documents from my knowledge base, so that I can remove outdated or incorrect information.

#### Acceptance Criteria

1. WHEN a doctor clicks delete on a document THEN the System SHALL display a confirmation dialog
2. WHEN deletion is confirmed THEN the System SHALL remove the document from Firestore
3. WHEN a document with ElevenLabs sync is deleted THEN the System SHALL also remove the document from ElevenLabs Knowledge Base
4. IF ElevenLabs deletion fails THEN the System SHALL still complete Firestore deletion and log the error

### Requirement 6

**User Story:** As a system, I want to maintain data integrity between Firestore and ElevenLabs, so that the knowledge base remains consistent.

#### Acceptance Criteria

1. THE System SHALL use Firestore as the primary data source for all knowledge documents
2. THE System SHALL store the ElevenLabs document ID reference in Firestore after successful sync
3. WHEN creating a knowledge document THEN the System SHALL generate a unique knowledge_id
4. THE System SHALL store document metadata including: knowledge_id, doctor_id, disease_name, document_type, raw_content, sync_status, elevenlabs_document_id, created_at

### Requirement 7

**User Story:** As a developer, I want the backend API to follow RESTful conventions, so that future frontend frameworks can integrate seamlessly.

#### Acceptance Criteria

1. THE System SHALL expose POST /api/knowledge endpoint for creating documents
2. THE System SHALL expose GET /api/knowledge endpoint for listing documents
3. THE System SHALL expose GET /api/knowledge/{id} endpoint for retrieving a single document
4. THE System SHALL expose DELETE /api/knowledge/{id} endpoint for removing documents
5. THE System SHALL expose POST /api/knowledge/{id}/retry-sync endpoint for retrying failed synchronizations
