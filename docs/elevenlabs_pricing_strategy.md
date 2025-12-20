# ElevenLabs API Pricing & Implementation Recommendations

This document outlines the current pricing structure for ElevenLabs API (as of Dec 2025) and provides recommendations for the development and testing of the **ElevenDops** application.

## 1. Pricing Plans Summary

| Plan        | Cost (Monthly) | Character Credits | Key Features                                                               |
| :---------- | :------------- | :---------------- | :------------------------------------------------------------------------- |
| **Free**    | $0             | 10,000 / month    | API Access, TTS/STT, Conversational AI. **Requires attribution.**          |
| **Starter** | $5             | 30,000 / month    | Commercial License, **Instant Voice Cloning**, Higher rate limits.         |
| **Creator** | $22\*          | 100,000 / month   | Professional Voice Cloning, Higher quality (192kbps), Usage-based top-ups. |

_\*Often includes a 50% discount for the first month ($11)._

---

## 2. Minimal Plan Recommendation

### Option A: The Free Plan ($0) - "Prototyping"

- **Best for:** Technical integration testing and unit/integration tests.
- **Usage:** Validating the `ElevenLabsService` implementation, testing webhook triggers, and checking basic latency.
- **Constraint:** 10,000 characters is roughly **15-20 minutes** of total speech. Heavy testing of the "Conversational Agent" will consume this quickly.
- **Action:** Ensure all automated tests use mocks where possible to save these credits for manual testing.

### Option B: The Starter Plan ($5) - "Pilot / Demo"

- **Best for:** User testing and stakeholder demonstrations.
- **Why Upgrade?**
  1.  **Commercial License:** Removes the requirement for ElevenLabs branding/attribution in the UI.
  2.  **Instant Voice Cloning:** Critical for ElevenDops if you want to demonstrate how a specific doctor's voice can be cloned for patient interactions.
  3.  **Credit Headroom:** 30,000 characters (~1 hour of speech) provides more safety for live demos.

---

## 3. Implementation Tips for Credit Conservation

1.  **Strict Mocking:** In `pytest`, ensure the ElevenLabs API is always mocked unless running specific integration tests (`@pytest.mark.integration`).
2.  **Shortening Payloads:** During manual testing of the Patient Chat, use short response configurations in the Agent's system prompt to minimize character consumption.
3.  **Caching:** Consider caching generated audio for frequent static phrases (like greetings) in Firestore/GCS to avoid re-generating the same characters multiple times.

---

## 4. Useful Links

- [Official Pricing Page](https://elevenlabs.io/pricing/api)
- [ElevenLabs API Usage Dashboard](https://elevenlabs.io/app/usage)
