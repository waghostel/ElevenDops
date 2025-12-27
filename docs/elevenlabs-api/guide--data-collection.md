# Data Collection: Information Extraction

Extract structured information (names, emails, business data) from conversations using LLM.

## Configuration (Dashboard)

Located in **Analysis** tab > **Data collection**.

1. Click **Add item**.
2. **Identifier**: Unique name (e.g. `patient_symptom`, `appointment_time`).
3. **Data Type**: `string`, `boolean`, `integer`, `number`.
4. **Description**: Specific instructions for extraction (e.g. "The main symptom described by the patient").

## API / Integration

Extracted data is available in:

1. **Conversation History** (Get Conversation Details API).
2. **Post-call Webhooks**: The payload will include the extracted data fields.

## Limits

- Trial/Enterprise: 40 items per agent.
- Other plans: 25 items per agent.
