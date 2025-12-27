# React SDK: Frontend Integration

The `@elevenlabs/react` package provides the `useConversation` hook for managing WebSocket connections and audio handling for Agents.

## Installation

```bash
npm install @elevenlabs/react
```

## `useConversation` Hook

```javascript
import { useConversation } from "@elevenlabs/react";

export function AgentComponent() {
  const conversation = useConversation({
    onConnect: () => console.log("Connected"),
    onDisconnect: () => console.log("Disconnected"),
    onMessage: (message) => console.log("Message:", message),
    onError: (error) => console.error("Error:", error),
  });

  const start = async () => {
    await conversation.startSession({
      agentId: "YOUR_AGENT_ID", // OR signedUrl: '...'
    });
  };

  const stop = async () => {
    await conversation.endSession();
  };

  return (
    <div>
      <p>Status: {conversation.status}</p>
      <p>Is Speaking: {conversation.isSpeaking ? "Yes" : "No"}</p>
      <button onClick={start} disabled={conversation.status === "connected"}>
        Start Conversation
      </button>
      <button onClick={stop} disabled={conversation.status !== "connected"}>
        Stop Conversation
      </button>
    </div>
  );
}
```

## Methods

- **startSession({ agentId, signedUrl })**: Starts the conversation.
- **endSession()**: Ends the conversation.
- **setVolume({ mode, value })**: Sets input/output volume (0-1).
- **sendFeedback({ score })**: Sends session feedback.

## Properties

- **status**: 'connected' | 'connecting' | 'disconnected'
- **isSpeaking**: boolean
