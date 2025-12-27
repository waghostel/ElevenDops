# Kiro Agent Hooks Reference Guide

> A comprehensive reference for creating, using, and understanding Kiro agent hooks.
> Designed for developers and LLMs collaborating with Kiro.

## Table of Contents

1. [Overview](#overview)
2. [How to Create a Kiro Agent Hook](#how-to-create-a-kiro-agent-hook)
3. [How to Use Kiro Agent Hooks](#how-to-use-kiro-agent-hooks)
4. [When Kiro Agent Hooks Are Triggered](#when-kiro-agent-hooks-are-triggered)
5. [Hook Configuration Schema](#hook-configuration-schema)
6. [Examples](#examples)

---

## Overview

Kiro Agent Hooks are automation mechanisms that allow agent executions to start automatically when specific events occur in the IDE. They bridge user actions with agent capabilities, enabling automated workflows without manual intervention.

### Key Concepts

| Term | Definition |
|------|------------|
| **Hook** | An automation rule that connects a trigger event to an action |
| **Trigger** | The event that activates the hook |
| **Action** | What happens when the hook is triggered |
| **File Pattern** | A glob pattern to filter which files activate the hook |

---

## How to Create a Kiro Agent Hook

### Method 1: Using the Explorer View (Recommended)

**Step 1**: Open the Kiro Explorer panel in your IDE sidebar.

**Step 2**: Locate the "Agent Hooks" section in the explorer.

**Step 3**: Click the "+" (plus) button to create a new hook.

**Step 4**: Fill in the hook configuration form:
- **Name**: A descriptive name for the hook
- **Trigger Event**: Select when the hook should activate
- **File Pattern** (optional): Specify which files trigger the hook
- **Action Type**: Choose `sendMessage` or `executeCommand`
- **Action Content**: The message or command to execute

**Step 5**: Save the hook configuration.

### Method 2: Using the Command Palette

**Step 1**: Open the Command Palette:
- Windows/Linux: `Ctrl+Shift+P`
- macOS: `Cmd+Shift+P`

**Step 2**: Type "Open Kiro Hook UI" and select it.

**Step 3**: The Hook UI panel opens where you can create and manage hooks.

**Step 4**: Click "Create New Hook" and configure as described above.

### Method 3: Direct Configuration File (Advanced)

Hooks are stored in `.kiro/hooks/` directory. You can create hook files directly:

```
.kiro/
└── hooks/
    └── my-hook.json
```

**Hook File Structure**:

```json
{
  "name": "My Custom Hook",
  "description": "Description of what this hook does",
  "enabled": true,
  "trigger": {
    "event": "onFileSave",
    "filePattern": "**/*.py"
  },
  "action": {
    "type": "sendMessage",
    "message": "The file ${filePath} was saved. Please review for issues."
  }
}
```

---

## How to Use Kiro Agent Hooks

### Using Automatic Hooks

Once configured, automatic hooks work without user intervention:

1. **File Save Hooks**: Simply save a file that matches the pattern
2. **Session Hooks**: Start a new chat session
3. **Agent Complete Hooks**: Wait for agent to finish execution
4. **Message Hooks**: Send a message to the agent

### Using Manual Trigger Hooks

For `onManualTrigger` hooks:

1. Open the Kiro Explorer panel
2. Find the "Agent Hooks" section
3. Locate your manual hook
4. Click the "Run" button next to the hook name

### Managing Hooks

| Action | How To |
|--------|--------|
| **Enable/Disable** | Toggle the switch in Agent Hooks section |
| **Edit** | Click the hook name to open configuration |
| **Delete** | Click the trash icon next to the hook |
| **View Logs** | Check Kiro output panel for execution logs |

### Using Variables in Hooks

Hooks support dynamic variables that are replaced at runtime:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `${filePath}` | Full path of the triggering file | `backend/api/routes.py` |
| `${fileName}` | Name of the file only | `routes.py` |
| `${fileDir}` | Directory containing the file | `backend/api` |
| `${workspaceRoot}` | Root directory of the workspace | `/home/user/project` |
| `${message}` | User's message (message triggers only) | `"Fix the bug"` |

**Example Usage**:

```json
{
  "action": {
    "type": "executeCommand",
    "command": "pytest ${fileDir}/test_${fileName} -v"
  }
}
```

---

## When Kiro Agent Hooks Are Triggered

### Trigger Event Reference

#### 1. `onFileSave` - File Save Event

**When Triggered**: Immediately after a user saves a code file in the IDE.

**Conditions**:
- File must be saved (not just modified)
- File path must match `filePattern` if specified
- Hook must be enabled

**Use Cases**:
- Run linters or formatters
- Execute tests for modified files
- Update related documentation
- Sync translation files

**Configuration Example**:
```json
{
  "trigger": {
    "event": "onFileSave",
    "filePattern": "**/*.py"
  }
}
```

**Pattern Matching**:
| Pattern | Matches |
|---------|---------|
| `**/*.py` | All Python files in any directory |
| `backend/**/*.py` | Python files only in backend folder |
| `**/test_*.py` | Test files starting with `test_` |
| `*.md` | Markdown files in root only |

---

#### 2. `onAgentComplete` - Agent Execution Complete

**When Triggered**: After the Kiro agent finishes executing a task or responding to a query.

**Conditions**:
- Agent must complete its execution (success or failure)
- Hook must be enabled

**Use Cases**:
- Post-processing after code generation
- Verification checklists
- Notification triggers
- Cleanup operations

**Configuration Example**:
```json
{
  "trigger": {
    "event": "onAgentComplete"
  }
}
```

---

#### 3. `onSessionCreate` - New Session Start

**When Triggered**: When a user starts a new chat session with Kiro (on first message send).

**Conditions**:
- New session must be created
- First message is sent in the session
- Hook must be enabled

**Use Cases**:
- Initialize project context
- Set up coding standards reminders
- Load relevant documentation references
- Configure session-specific settings

**Configuration Example**:
```json
{
  "trigger": {
    "event": "onSessionCreate"
  }
}
```

---

#### 4. `onMessageSend` - User Message Event

**When Triggered**: Every time a user sends a message to the agent.

**Conditions**:
- User sends a message in chat
- Hook must be enabled

**Use Cases**:
- Add context to every request
- Inject coding standards
- Modify or enhance prompts
- Log user interactions

**Configuration Example**:
```json
{
  "trigger": {
    "event": "onMessageSend"
  }
}
```

**Note**: Use sparingly as this triggers on every message.

---

#### 5. `onManualTrigger` - User-Initiated Event

**When Triggered**: Only when the user explicitly clicks the hook's run button.

**Conditions**:
- User must manually click the trigger button
- Hook must be enabled

**Use Cases**:
- On-demand spell checking
- Manual code review requests
- Documentation generation
- One-time cleanup tasks

**Configuration Example**:
```json
{
  "trigger": {
    "event": "onManualTrigger"
  }
}
```

---

### Trigger Execution Flow

```
┌─────────────────┐
│  Event Occurs   │
│  (save, message,│
│   etc.)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Hook Engine    │
│  Checks All     │
│  Enabled Hooks  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     No
│  Event Type     │────────────▶ Skip Hook
│  Matches?       │
└────────┬────────┘
         │ Yes
         ▼
┌─────────────────┐     No
│  File Pattern   │────────────▶ Skip Hook
│  Matches?       │
│  (if applicable)│
└────────┬────────┘
         │ Yes
         ▼
┌─────────────────┐
│  Execute Action │
│  - sendMessage  │
│  - executeCmd   │
└─────────────────┘
```

---

## Hook Configuration Schema

### Complete Schema Reference

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "enabled": "boolean (default: true)",
  "trigger": {
    "event": "onFileSave | onAgentComplete | onSessionCreate | onMessageSend | onManualTrigger (required)",
    "filePattern": "string (optional, glob pattern)"
  },
  "action": {
    "type": "sendMessage | executeCommand (required)",
    "message": "string (required if type is sendMessage)",
    "command": "string (required if type is executeCommand)"
  }
}
```

### Action Types Explained

#### `sendMessage` Action

Sends a message to the agent context. The agent receives this as additional instruction or context.

```json
{
  "action": {
    "type": "sendMessage",
    "message": "Please ensure all code follows PEP 8 standards."
  }
}
```

**Behavior**:
- Message is injected into the agent's context
- Agent processes it as part of the current conversation
- Can include variables for dynamic content

#### `executeCommand` Action

Runs a shell command in the terminal.

```json
{
  "action": {
    "type": "executeCommand",
    "command": "pytest tests/ -v --tb=short"
  }
}
```

**Behavior**:
- Command runs in the workspace root directory
- Output is captured and can be viewed in terminal
- Variables are substituted before execution

---

## Examples

### Example 1: Python Test Runner

Automatically run tests when saving Python test files.

```json
{
  "name": "Python Test Runner",
  "description": "Run pytest when test files are saved",
  "enabled": true,
  "trigger": {
    "event": "onFileSave",
    "filePattern": "**/test_*.py"
  },
  "action": {
    "type": "executeCommand",
    "command": "pytest ${filePath} -v --tb=short"
  }
}
```

### Example 2: Code Review Checklist

Remind agent of review checklist after code generation.

```json
{
  "name": "Code Review Checklist",
  "description": "Verify code quality after agent completes",
  "enabled": true,
  "trigger": {
    "event": "onAgentComplete"
  },
  "action": {
    "type": "sendMessage",
    "message": "Before finalizing, verify:\n- [ ] Error handling implemented\n- [ ] No hardcoded credentials\n- [ ] Code follows project standards"
  }
}
```

### Example 3: Project Context Initialization

Set up context when starting a new session.

```json
{
  "name": "Project Context",
  "description": "Initialize ElevenDops project context",
  "enabled": true,
  "trigger": {
    "event": "onSessionCreate"
  },
  "action": {
    "type": "sendMessage",
    "message": "This is the ElevenDops project:\n- Backend: FastAPI (backend/)\n- Frontend: Streamlit (streamlit_app/)\n- Tests: Property-based (tests/)\nFollow coding standards in .kiro/steering/"
  }
}
```

### Example 4: Manual Documentation Check

User-triggered documentation review.

```json
{
  "name": "Documentation Review",
  "description": "Manual trigger to review README",
  "enabled": true,
  "trigger": {
    "event": "onManualTrigger"
  },
  "action": {
    "type": "sendMessage",
    "message": "Please review README.md for:\n- Spelling and grammar errors\n- Broken links\n- Outdated information\nFix any issues found."
  }
}
```

### Example 5: Lint on Save

Run linter when saving backend Python files.

```json
{
  "name": "Backend Linter",
  "description": "Run ruff linter on backend files",
  "enabled": true,
  "trigger": {
    "event": "onFileSave",
    "filePattern": "backend/**/*.py"
  },
  "action": {
    "type": "executeCommand",
    "command": "ruff check ${filePath} --fix"
  }
}
```

---

## Quick Reference Card

### Creating a Hook
1. Explorer → Agent Hooks → "+"
2. Or: Command Palette → "Open Kiro Hook UI"

### Trigger Events
| Event | When |
|-------|------|
| `onFileSave` | File saved |
| `onAgentComplete` | Agent finishes |
| `onSessionCreate` | New session starts |
| `onMessageSend` | User sends message |
| `onManualTrigger` | User clicks button |

### Action Types
| Type | Purpose |
|------|---------|
| `sendMessage` | Add context to agent |
| `executeCommand` | Run shell command |

### Variables
| Variable | Value |
|----------|-------|
| `${filePath}` | Full file path |
| `${fileName}` | File name only |
| `${fileDir}` | Directory path |
| `${workspaceRoot}` | Project root |
| `${message}` | User message |

---

## Related Documentation

- [Kiro Steering Guide](./guide--kiro-steering.md) - Configure persistent agent instructions
- [Kiro Workflow Patterns](./guide--kiro-workflow-patterns.md) - Common automation patterns
- [Kiro Troubleshooting](./guide--kiro-troubleshooting.md) - Debug hook issues
