# Antigravity Context Management

This document explains how the Antigravity AI agent manages context and loads project knowledge.

## Overview

Antigravity uses a **two-tier context system** to balance immediate availability with context efficiency.

```mermaid
graph TB
    subgraph "Always in Context (System Prompt)"
        A[Global Rules<br/>MEMORY user_global]
        B[User Preferences]
        C[Workflow Definitions]
    end

    subgraph "On-Demand Loading"
        D[.agent/rules/*]
        E[.kiro/steering/*]
        F[docs/*]
        G[Source Code]
    end

    subgraph "Agent Context Window"
        H[System Prompt<br/>~10-15%]
        I[Conversation History<br/>~30-40%]
        J[Retrieved Knowledge<br/>~45-60%]
    end

    A --> H
    B --> H
    C --> H

    D -.->|grep/view| J
    E -.->|grep/view| J
    F -.->|grep/view| J
    G -.->|grep/view| J
```

## Tier 1: Global Constants (Always Loaded)

These are **always present** in the system prompt and occupy a fixed portion of the context window.

| Location              | Purpose                   | Example                                 |
| --------------------- | ------------------------- | --------------------------------------- |
| `MEMORY[user_global]` | Core tech stack rules     | Use `pnpm`, `uv`, TailwindCSS 4         |
| User Rules            | Coding style conventions  | Google docstrings, strict types         |
| Workflows             | Slash command definitions | `/kiro-spec-run`, `/uv-package-manager` |

### Characteristics

- ✅ **Immediate**: No lookup needed
- ✅ **Consistent**: Applied to every request
- ❌ **Fixed Cost**: Always uses context space (~10-15%)

### When to Use

- **Critical constraints** that must never be violated
- **Project-wide conventions** (tech stack, naming)
- **Frequently needed** information

---

## Tier 2: On-Demand Loading

These are **retrieved as needed** based on the current task.

| Location           | Purpose                | Loaded When                         |
| ------------------ | ---------------------- | ----------------------------------- |
| `.agent/rules/*`   | Domain-specific rules  | Agent searches for related patterns |
| `.kiro/steering/*` | Architecture docs      | Starting spec-driven work           |
| `.kiro/specs/*`    | Feature specifications | Implementing specific features      |
| `docs/*`           | Project documentation  | Researching project context         |

### Retrieval Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant FileSystem

    User->>Agent: "Fix the 307 error"
    Agent->>Agent: Parse intent
    Agent->>FileSystem: grep_search("307", backend/)
    FileSystem-->>Agent: Matching files
    Agent->>FileSystem: view_file(templates.py)
    FileSystem-->>Agent: File contents
    Agent->>FileSystem: list_dir(.agent/rules/)
    FileSystem-->>Agent: Available rules
    Agent->>Agent: Decide if rules are relevant
    Agent->>User: Solution + explanation
```

### Characteristics

- ✅ **Efficient**: Only loaded when relevant
- ✅ **Scalable**: Unlimited project docs
- ❌ **Latency**: Requires tool calls to retrieve
- ❌ **Ephemeral**: Pruned as conversation grows

---

## Context Window Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Fresh: New conversation
    Fresh --> Working: User request
    Working --> Growing: Tool results added
    Growing --> Pruning: Context limit approached
    Pruning --> Working: Older content removed
    Working --> [*]: Conversation ends

    note right of Pruning
        Older tool results and
        file contents are removed.
        Global rules are preserved.
    end note
```

### What Gets Pruned First

1. Old file contents (already acted upon)
2. Intermediate search results
3. Earlier conversation turns

### What's Preserved

1. System prompt (global rules)
2. Recent conversation context
3. Currently relevant file contents

---

## Best Practices

### For Global Rules (Tier 1)

```markdown
# Good: Concise, critical constraints

- Use **pnpm** instead of npm
- Use **uv** for Python dependencies
- All API endpoints MUST return StandardResponse
```

### For On-Demand Rules (Tier 2)

```markdown
# Good: Detailed, domain-specific guidance

## API Route Patterns

When defining collection endpoints...
[detailed examples and rationale]
```

### Rule Placement Decision Tree

```mermaid
flowchart TD
    A[New Rule] --> B{Critical constraint?}
    B -->|Yes| C{Frequently needed?}
    B -->|No| F[.agent/rules/]
    C -->|Yes| D[MEMORY user_global]
    C -->|No| E{Domain-specific?}
    E -->|Yes| F
    E -->|No| G[.kiro/steering/]
```

---

## Summary

| Aspect       | Tier 1 (Global)  | Tier 2 (On-Demand) |
| ------------ | ---------------- | ------------------ |
| Location     | System prompt    | File system        |
| Loading      | Always           | When searched      |
| Context cost | Fixed (~10-15%)  | Variable           |
| Persistence  | Permanent        | Session-based      |
| Best for     | Core constraints | Detailed guidance  |
