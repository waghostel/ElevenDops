# The `.agent` Directory System

This document explains how the `.agent` directory works with AI coding assistants like Antigravity. It serves as a structured workspace for defining reusable workflows, rules, and instructions that guide the AI's behavior within a project.

---

## Overview

The `.agent` directory is a **project-level configuration space** that allows developers to customize how an AI assistant interacts with their codebase. Unlike a single monolithic instruction file, it promotes a modular, lazy-loaded approach for efficiency.

```
.agent/
├── workflows/          # Standard operating procedures
│   ├── build.md
│   ├── deploy.md
│   └── test.md
├── rules/              # Project-wide coding constraints (optional)
│   └── naming-conventions.md
└── instructions.md     # Global agent instructions (optional)
```

---

## Core Concepts

### 1. Lazy Loading (On-Demand Context)

Files in `.agent/` are **not pre-loaded** into the AI's context window at the start of every conversation. Instead:

1.  The AI maintains an **index** of available files (low overhead).
2.  Files are loaded **only when relevant** (e.g., when a user invokes a command or the AI detects a related task).
3.  This preserves context window capacity for code, errors, and conversation history.

### 2. Slash Command Invocation

Workflow files can be triggered via **slash commands** based on their filename:

| File Path                            | Slash Command     |
| :----------------------------------- | :---------------- |
| `.agent/workflows/build.md`          | `/build`          |
| `.agent/workflows/deploy-staging.md` | `/deploy-staging` |

---

## Workflows (`workflows/`)

Workflows are the primary feature of the `.agent` system. They define step-by-step procedures for common tasks.

### File Format

Each workflow file uses YAML frontmatter followed by Markdown content:

````markdown
---
description: How to run the test suite
---

# Test Workflow

## Prerequisites

Ensure the virtual environment is active.

## Steps

1. Install dependencies
   // turbo

```powershell
uv sync
```
````

2. Run pytest
   // turbo

```powershell
uv run pytest tests/ -v
```

3. Check coverage report

```powershell
uv run pytest --cov=backend tests/
```

````

### Turbo Annotations

Special annotations control automatic execution:

| Annotation      | Scope        | Effect                                       |
| :-------------- | :----------- | :------------------------------------------- |
| `// turbo`      | Single step  | Auto-runs the immediately following command. |
| `// turbo-all`  | Entire file  | Auto-runs every command in the workflow.     |

> [!CAUTION]
> Use `// turbo` only for safe, non-destructive commands (e.g., `uv sync`, `pnpm install`). Avoid using it for commands that delete files or modify production data.

---

## Rules (`rules/`) (Optional)

The `rules/` subdirectory can hold files that define **constraints and conventions** the AI should follow when generating code.

### Example: `rules/api-design.md`

```markdown
---
description: API design guidelines for this project
---

# API Design Rules

1.  All endpoints MUST return JSON with a consistent envelope:
    ```json
    { "data": ..., "error": null }
    ```
2.  Use `snake_case` for all JSON keys.
3.  Pagination MUST use `offset` and `limit` query parameters.
````

When the AI is working on API-related code, it can reference this file to ensure compliance.

---

## Global Instructions (`instructions.md`) (Optional)

A single `instructions.md` file at the root of `.agent/` can provide high-level guidance that applies across all tasks.

### Example: `.agent/instructions.md`

```markdown
# Project Instructions

- This is a medical device documentation platform.
- Prioritize code clarity over brevity.
- Always include docstrings for public functions.
- When unsure, ask for clarification before proceeding.
```

---

## Benefits of the `.agent` System

| Benefit                | Description                                                                  |
| :--------------------- | :--------------------------------------------------------------------------- |
| **Modularity**         | Separate files for separate concerns; easy to add, update, or remove.        |
| **Context Efficiency** | Lazy loading prevents wasted context window space.                           |
| **Team Consistency**   | Standardized workflows ensure all team members (and AI) follow the same SOP. |
| **Version Controlled** | Lives in Git alongside the codebase; changes are tracked and reviewable.     |

---

## Quick Start

1.  **Create the directory structure:**

    ```powershell
    mkdir .agent\workflows
    ```

2.  **Add your first workflow:**
    Create `.agent/workflows/dev-setup.md`:

    ````markdown
    ---
    description: Set up the development environment
    ---

    # Dev Setup

    // turbo-all

    1. Install Python dependencies

    ```powershell
    uv sync
    ```
    ````

    2. Copy environment file

    ```powershell
    Copy-Item .env.example .env
    ```

    ```

    ```

3.  **Invoke it:**
    In your AI chat, type `/dev-setup` and the AI will follow the steps.

---

> [!TIP]
> Start small! Add one or two workflows for your most repetitive tasks (e.g., running tests, starting the dev server) and expand as needed.
