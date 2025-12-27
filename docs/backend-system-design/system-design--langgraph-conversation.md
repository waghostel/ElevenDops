# LangGraph Conversation System Design

## System Overview

The Conversation System uses [LangGraph](https://langchain-ai.github.io/langgraph/) to orchestrate complex LLM workflows. It supports both synchronous execution and real-time streaming of generated content using Google's Gemini models.

## Script Generation Workflow

The script generation process is modeled as a state graph, allowing for structured processing, validation, and error handling.

```mermaid
stateDiagram-v2
    [*] --> PrepareContext

    state PrepareContext {
        [*] --> ValidateInput
        ValidateInput --> FormatPrompt
    }

    PrepareContext --> GenerateScript

    state GenerateScript {
        [*] --> InitLLM
        InitLLM --> InvokeGemini
        InvokeGemini --> HandleErrors: Error
        InvokeGemini --> ReturnContent: Success
    }

    GenerateScript --> PostProcess

    state PostProcess {
        [*] --> CleanMarkdown
        CleanMarkdown --> TrimWhitespace
    }

    PostProcess --> [*]
```

### LangGraph Implementation

The workflow is defined in `langgraph_workflow.py` with the following nodes:

1.  **`prepare_context`**: Validates inputs and performs any necessary text preprocessing.
2.  **`generate_script`**: Invokes the `ChatGoogleGenerativeAI` model. Handles API keys and timeouts.
3.  **`post_process`**: Cleans up the raw LLM output (e.g., removing Markdown code blocks).

## Streaming Architecture

To support long responses without timeouts, the system implements a streaming generator pattern.

```mermaid
sequenceDiagram
    participant Client
    participant API as /api/conversations
    participant Stream as generate_script_stream()
    participant LLM as Google Gemini

    Client->>API: Generate Script Request
    API->>Stream: invoke()

    Stream->>LLM: astream(messages)

    loop Token Stream
        LLM-->>Stream: Chunk (Token)
        Stream-->>Client: Yield {"type": "token", "content": "..."}
    end

    LLM-->>Stream: Complete
    Stream->>Stream: post_process_script()
    Stream-->>Client: Yield {"type": "complete", "script": "..."}
```

## Tracing and Observability

The system includes a custom tracing layer (`WorkflowTrace`) to monitor workflow execution.

- **Trace Granularity**: Tracks individual node execution time (ms), input/output state, and errors.
- **LangSmith Integration**: Compatible with LangSmith for deep debugging when configured.
- **Error Handling**: Captures full stack traces for failed nodes without crashing the entire workflow.

### Data Flow for Tracing

```mermaid
graph LR
    Node["Workflow Node"] --> Wrapper["@trace_node Decorator"]
    Wrapper -->|Start| Timer["Start Timer"]
    Wrapper -->|Execute| Func["Function Body"]
    Func -->|Result/Error| Wrapper
    Wrapper -->|End| Step["Create TraceStep"]
    Step --> Collector["WorkflowTrace Collector"]
```
