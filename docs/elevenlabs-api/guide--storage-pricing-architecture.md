# ElevenLabs Storage, Pricing & SaaS Architecture

This guide covers storage limits, pricing implications, and architectural patterns for building SaaS applications on top of ElevenLabs.

---

## 1. Storage & Subscription Limits

In ElevenLabs, "knowledge" and storage usage are tied directly to your subscription tier.

### A. AI Agent Knowledge Base (RAG)

Limits on the documents (PDF, TXT, URL) used to ground your agent's answers.

| Tier               | Limit                   | Notes                                                 |
| :----------------- | :---------------------- | :---------------------------------------------------- |
| **Non-Enterprise** | **20MB** or ~300k chars | Hard limit shared across all agents on the account.   |
| **Enterprise**     | **Custom**              | Millions of words; supports advanced large-scale RAG. |

### B. Voice Storage (Voice Slots)

The number of custom cloned voices you can save.

| Plan         | Voice Slots | PVC (Pro Voice Cloning) |
| :----------- | :---------- | :---------------------- |
| **Free**     | 3           | N/A                     |
| **Starter**  | 10          | N/A                     |
| **Creator**  | 30          | 1 Slot                  |
| **Pro**      | 160         | 1 Slot                  |
| **Scale**    | 660         | 1 Slot                  |
| **Business** | 660         | 3 Slots                 |

> **Note:** PVC (Professional Voice Cloning) requires 30min - 3hrs of audio to create a high-fidelity digital twin.

### C. Studio Project Storage

For long-form content (audiobooks, articles).

- **Free:** 5 Projects
- **Starter:** 20 Projects
- **Creator:** 1,000 Projects
- **Pro:** 3,000 Projects
- **Scale/Business:** 20,000 Projects

**Internal Project Limits:** Max 500 chapters/project, 400 paragraphs/chapter (5k chars/paragraph).

---

## 2. SaaS Architecture: Managing User Knowledge

**Crucial Concept:** ElevenLabs has **no native concept of "Sub-Users"**. Even if you have 1,000 users in your SaaS, ElevenLabs sees them all as YOU (one API key).

### The Challenge

If User A uploads a document, you must prevent User B from accessing it. You (the developer) act as the **Orchestrator**.

### Implementation Strategy

#### 1. Knowledge Base Isolation

- **ElevenLabs Side:** Create documents via API. You get back a `document_id`.
- **Your Database:** Store a mapping table:
  ```json
  {
    "user_id": "user_123",
    "kb_document_id": "doc_xyz_from_elevenlabs",
    "agent_id": "agent_abc"
  }
  ```
- **Runtime:** When User A chats, your backend looks up _their_ specific `agent_id` or injects _their_ `document_ids` into the request.

#### 2. Quota Management (Metered Billing)

- **Risk:** One heavy user can consume your entire monthly character quota.
- **Solution:** You MUST build an internal ledger.
  - Track every generation request in your DB.
  - Deduct from an internal "User Credit Balance" before calling ElevenLabs.
  - Block the request if their personal quota is invalid, even if your ElevenLabs account has credits.

### Architecture Comparison

| Component     | Managed by ElevenLabs    | Managed by YOUR SaaS                        |
| :------------ | :----------------------- | :------------------------------------------ |
| **API Key**   | One master key           | **Hidden** (never exposed to frontend)      |
| **Isolation** | None (Flat list)         | **Crucial Logic** (User ID <-> Resource ID) |
| **Billing**   | Charges you (Repository) | You charge users (Stripe, etc.)             |
| **Storage**   | Physical files & Vectors | Ownership records & Permission checks       |

---

## 3. RAG Integration Methods

You can connect your own external data to ElevenLabs Agents in three ways:

### Method 1: Custom LLM (Recommended for Existing RAG)

Use this if you already have a mature RAG system (Pinecone, LangChain, etc.).

- **How:** Point ElevenLabs to your own API endpoint (OpenAI-compatible).
- **Flow:** Speech -> Text -> **Your Server** -> Your DB -> Your LLM -> Text -> Speech.
- **Pros:** Maximum control, data privacy, full ownership of vector search logic.

### Method 2: Server Tools (Webhooks)

Use this for specific data lookups without replacing the entire brain.

- **How:** Define a "Tool" (e.g., `lookup_order_status`) in ElevenLabs Dashboard.
- **Flow:** User asks question -> Agent decides to call Tool -> **Webhook to your API** -> JSON Result -> Agent speaks answer.
- **Pros:** Easy to add "skills" to the hosted agent.

### Method 3: Model Context Protocol (MCP)

Use this for standardized connections.

- **How:** Connect an MCP Client to an MCP Server.
- **Pros:** "Universal Plug" for data. Great if your data sources already support MCP (e.g., Google Drive, Slack connectors).

---

## 4. Model Selection

When using the ElevenLabs Agent out-of-the-box, you can choose the underlying "Brain".

### A. Hosted Models (Lowest Latency)

Co-located with the TTS engine for sub-second responses.

- **Qwen3-30B-A3B:** Optimized for extreme speed (<150ms).
- **GLM-4.5-Air:** Good balance of reasoning and speed.

### B. Proprietary Models (High Intelligence)

- **Google Gemini 2.5 Flash:** Massive context window, very fast.
- **GPT-4o / GPT-4o-mini:** Standard versatile reasoning.
- **Claude 5.1 Sonnet/Haiku:** More natural, "human" sounding prose.

### C. Default Defaults

- **English:** Usually defaults to **GPT-4o-mini** or **Eleven Flash v2**.
- **Multilingual:** Switches to **Gemini 2.5 Flash** or **Eleven Multilingual v2.5**.

**Recommendation:**

- **Speed/Real-time:** Qwen3 or Gemini Flash Lite.
- **Complex Tasks:** GPT-4o or Claude 3.5 Sonnet.
- **Empathy:** Claude 3 Haiku.
