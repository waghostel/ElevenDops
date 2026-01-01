---
description: How to run integration tests using the local Firestore/GCS emulator
---

To run integration tests that require a stateful Firestore (resolving "MagicMock" persistence errors), follow these steps:

1. **Start the Emulator Services**
   This starts local Firestore (port 8080) and Fake GCS (port 4443).

   ```powershell
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Wait for Services**
   Ensure they are running (typically takes a few seconds). You can check with:

   ```powershell
   docker ps
   ```

3. **Run Tests with Emulator Flag**
   Set `TEST_AGAINST_EMULATOR=true` to disable the mocks and use the emulator.

   ```powershell
   $env:TEST_AGAINST_EMULATOR="true"
   uv run pytest -v tests/test_integration_workflow.py tests/test_education_audio_integration.py
   ```

4. **Stop the Emulator Services**
   When finished, clean up resources.
   ```powershell
   docker-compose -f docker-compose.dev.yml down
   ```
