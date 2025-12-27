# Client Tools: Client-side Operations

Empower your assistant to trigger client-side operations (UI events, DOM manipulation, etc).

## Configuration (Dashboard)

1. Navigate to Agent Dashboard > Tools.
2. Click "Add Tool", set Tool Type to "Client".
3. Configure **Name**, **Description**, and **Parameters**.

Example: `logMessage` tool with `message` parameter.

## SDK Registration (Code)

Unlike server-tools, client tools must be registered in the client-side code.

```python
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ClientTools

def log_message(parameters):
    message = parameters.get("message")
    print(message)

client_tools = ClientTools()
client_tools.register("logMessage", log_message)

conversation = Conversation(
    client=ElevenLabs(api_key="your-api-key"),
    agent_id="your-agent-id",
    client_tools=client_tools,
    # ...
)

conversation.start_session()
```

## Returning Data to Agent

If the agent needs the result (e.g. `get_customer_details`), ensure "Wait for response" is checked in dashboard.

```python
def get_customer_details():
    return {"id": 123, "name": "Alice"}

client_tools.register("getCustomerDetails", get_customer_details)
```

The agent receives the returned JSON and appends it to context.
