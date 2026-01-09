# Knowledge base

## Overview

A well-curated knowledge base helps your agent go beyond its pre-trained data and deliver context-aware answers.
Here are a few examples where knowledge bases can be useful:

- Product catalogs: Store product specifications, pricing, and other essential details.
- HR or corporate policies: Provide quick answers about vacation policies, employee benefits, or onboarding procedures.
- Technical documentation: Equip your agent with in-depth guides or API references to assist developers.
- Customer FAQs: Answer common inquiries consistently.
  The agent on this page is configured with full knowledge of ElevenLabs’ documentation and sitemap. Go ahead and ask it about anything about ElevenLabs.

## Usage

### Build a knowledge base via the API

```python
# First create the document from text
knowledge_base_document_text = elevenlabs.conversational_ai.knowledge_base.documents.create_from_text(
 text="The airspeed velocity of an unladen swallow (European) is 24 miles per hour or roughly 11 meters per second.",
 name="Unladen Swallow facts",
)

# Alternatively, you can create a document from a URL
knowledge_base_document_url = elevenlabs.conversational_ai.knowledge_base.documents.create_from_url(
 url="https://en.wikipedia.org/wiki/Unladen_swallow",
 name="Unladen Swallow Wikipedia page",
)

# Or create a document from a file
knowledge_base_document_file = elevenlabs.conversational_ai.knowledge_base.documents.create_from_file(
 file=open("/path/to/unladen-swallow-facts.txt", "rb"),
 name="Unladen Swallow Facts",
)

# Then add the document to the agent
agent = elevenlabs.conversational_ai.agents.update(
 agent_id="agent-id",
 conversation_config={
 "agent": {
 "prompt": {
 "knowledge_base": [
 {
 "type": "text",
 "name": knowledge_base_document_text.name,
 "id": knowledge_base_document_text.id,
 },
 {
 "type": "url",
 "name": knowledge_base_document_url.name,
 "id": knowledge_base_document_url.id,
 },
 {
 "type": "file",
 "name": knowledge_base_document_file.name,
 "id": knowledge_base_document_file.id,
 }
 ]
 }
 }
 },
)

print("Agent updated:", agent)
```

## Best practices

### Content quality

Provide clear, well-structured information that’s relevant to your agent’s purpose.

### Size management

Break large documents into smaller, focused pieces for better processing.

### Regular updates

Regularly review and update the agent’s knowledge base to ensure the information remains current and accurate.

### Identify knowledge gaps

Review conversation transcripts to identify popular topics, queries and areas where users struggle to find information. Note any knowledge gaps and add the missing context to the knowledge base.

---

## Maintenance & Sync Quality

The system implements automated background synchronization and a manual reconciliation tool to ensure high data quality.

### 1. Automated Sync

When you create or edit documents in the app, the system automatically propagates those changes to ElevenLabs. If a document is in use by an agent, the system handles the replacement safely.

### 2. Manual Reconciliation

If you suspect data drift, use the CLI tool to audit and fix your Knowledge Base:

```powershell
.\.venv\Scripts\python.exe scripts/reconcile--elevenlabs-knowledge.py --audit
```

See the [Knowledge Architecture Guide](./guide--knowledge-architecture.md) for deeper technical details.

## Enterprise features

Need higher limits? [Contact our sales team](https://elevenlabs.io/contact-sales) to discuss enterprise plans with expanded knowledge base capabilities.

# Delete Document

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
client.conversational_ai.delete_knowledge_base_document(
    document_id="document_id"
)
```

## Response

Returns `200 OK` on success.
