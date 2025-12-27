# Kiro Hooks Guide

This guide explains how to create and use Kiro hooks for automated agent execution. It's designed for team members using different IDEs or LLM tools who need to understand or replicate this pattern.

## What Are Kiro Hooks?

Kiro hooks are automation triggers that execute agent actions when specific events occur in the IDE. They enable:
- Automatic code quality checks on file save
- Translation synchronization across language files
- Custom workflows triggered by user actions
- Agent reminders during conversations

**Configuration**: Via Kiro UI (Explorer view → Agent Hooks section)

## Hook Components

### 1. Trigger Events

| Event Type | Description | Use Case |
|------------|-------------|----------|
| `onFileSave` | When a code file is saved | Run tests, lint, format |
| `onAgentComplete` | When agent execution finishes | Post-processing, notifications |
| `onSessionCreate` | When a new chat session starts | Initialize context, reminders |
| `onMessageSend` | When user sends a message | Add context, modify prompts |
| `onManualTrigger` | When user clicks hook button | On-demand workflows |

### 2. Action Types

| Action | Description | Example |
|--------|-------------|---------|
| `sendMessage` | Send a message to the agent | Remind agent of coding standards |
| `executeCommand` | Run a shell command | Execute test suite, build project |

## Step-by-Step Creation Process

### Step 1: Access Hook Configuration

**Option A: Explorer View**
1. Open Kiro Explorer panel
2. Find "Agent Hooks" section
3. Click "+" to create new hook

**Option B: Command Palette**
1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Search for "Open Kiro Hook UI"
3. Select to open hook configuration

### Step 2: Define Trigger

Choose when the hook should activate:

```yaml
# Example: Trigger on Python file save
trigger:
  event: onFileSave
  filePattern: "**/*.py"
```

### Step 3: Define Action

Specify what happens when triggered:

```yaml
# Example: Send message to agent
action:
  type: sendMessage
  message: "Please run tests for the modified file and report any failures."

# Example: Execute shell command
action:
  type: executeCommand
  command: "pytest tests/ -v --tb=short"
```

### Step 4: Configure Options

Set additional options:

```yaml
options:
  enabled: true
  description: "Run tests on Python file save"
  autoApprove: false  # Require user confirmation
```

## Common Hook Patterns

### Pattern 1: Auto-Test on Save

Automatically run tests when saving test files:

```yaml
name: "Auto Test Runner"
trigger:
  event: onFileSave
  filePattern: "**/test_*.py"
action:
  type: executeCommand
  command: "pytest ${filePath} -v"
options:
  description: "Run tests for saved test file"
```

### Pattern 2: Translation Sync

Update translation files when source changes:

```yaml
name: "Translation Sync"
trigger:
  event: onFileSave
  filePattern: "**/locales/en/*.json"
action:
  type: sendMessage
  message: |
    The English translation file was updated. Please:
    1. Review the changes
    2. Update corresponding files in zh-TW and ja folders
    3. Maintain consistent key structure
options:
  description: "Sync translations across languages"
```

### Pattern 3: Code Review Reminder

Add context when agent completes code generation:

```yaml
name: "Code Review Checklist"
trigger:
  event: onAgentComplete
action:
  type: sendMessage
  message: |
    Before finalizing, please verify:
    - [ ] Code follows project coding standards
    - [ ] Error handling is implemented
    - [ ] No hardcoded secrets or credentials
options:
  description: "Remind agent of review checklist"
```

### Pattern 4: Manual Spell Check

User-triggered documentation review:

```yaml
name: "Spell Check README"
trigger:
  event: onManualTrigger
action:
  type: sendMessage
  message: |
    Please review README.md for:
    - Grammar and spelling errors
    - Broken links
    - Outdated information
    Fix any issues found.
options:
  description: "Manual spell check for documentation"
```

### Pattern 5: Session Context Initialization

Set up context when starting new conversation:

```yaml
name: "Project Context"
trigger:
  event: onSessionCreate
action:
  type: sendMessage
  message: |
    This is the ElevenDops project. Key context:
    - Backend: FastAPI in backend/
    - Frontend: Streamlit in streamlit_app/
    - Tests: Property-based tests in tests/
    Please follow the coding standards in .kiro/steering/
options:
  description: "Initialize project context for new sessions"
```

## Hook Execution by LLM

### How LLMs Process Hooks

1. **Event Detection**: IDE detects trigger event (file save, message, etc.)
2. **Pattern Matching**: For file-based triggers, checks against `filePattern`
3. **Action Dispatch**: Executes configured action
4. **Context Injection**: For `sendMessage`, content is added to agent context
5. **Command Execution**: For `executeCommand`, runs in terminal

### LLM Interaction Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Trigger   │────▶│  Hook Engine │────▶│   Action    │
│   Event     │     │  (Pattern    │     │  Executor   │
│             │     │   Match)     │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                    ┌──────────────────────────┴──────────────────────────┐
                    │                                                      │
              ┌─────▼─────┐                                        ┌──────▼──────┐
              │  Send to  │                                        │   Execute   │
              │   Agent   │                                        │   Command   │
              │  Context  │                                        │  in Shell   │
              └───────────┘                                        └─────────────┘
```

### Variables Available in Hooks

| Variable | Description | Example |
|----------|-------------|---------|
| `${filePath}` | Full path of triggering file | `backend/services/audio.py` |
| `${fileName}` | Name of triggering file | `audio.py` |
| `${fileDir}` | Directory of triggering file | `backend/services` |
| `${workspaceRoot}` | Project root directory | `/home/user/project` |
| `${message}` | User's message (for message triggers) | "Fix the bug" |

## Adapting for Other IDEs

### For VS Code Extensions

Create a similar hook system using VS Code's event API:

```typescript
// Example: VS Code extension hook implementation
import * as vscode from 'vscode';

interface Hook {
  name: string;
  trigger: {
    event: 'onFileSave' | 'onManualTrigger';
    filePattern?: string;
  };
  action: {
    type: 'sendMessage' | 'executeCommand';
    content: string;
  };
}

function registerHook(hook: Hook) {
  if (hook.trigger.event === 'onFileSave') {
    vscode.workspace.onDidSaveTextDocument((doc) => {
      if (matchesPattern(doc.uri.fsPath, hook.trigger.filePattern)) {
        executeAction(hook.action);
      }
    });
  }
}
```

### For Cursor/Continue

1. Use the tool's native automation features
2. Create custom commands that mirror hook behavior
3. Configure file watchers for save-triggered actions

### For Direct LLM API Usage

Implement hooks programmatically:

```python
import os
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class HookHandler(FileSystemEventHandler):
    def __init__(self, hooks: list):
        self.hooks = hooks
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        for hook in self.hooks:
            if hook['trigger']['event'] == 'onFileSave':
                pattern = hook['trigger'].get('filePattern', '*')
                if fnmatch.fnmatch(event.src_path, pattern):
                    self.execute_hook(hook, event.src_path)
    
    def execute_hook(self, hook: dict, file_path: str):
        action = hook['action']
        
        if action['type'] == 'sendMessage':
            # Inject message into LLM context
            message = action['content'].replace('${filePath}', file_path)
            add_to_agent_context(message)
        
        elif action['type'] == 'executeCommand':
            # Run shell command
            command = action['content'].replace('${filePath}', file_path)
            os.system(command)
```

## Best Practices

### Do's ✅

1. **Keep hooks focused** - One purpose per hook
2. **Use specific file patterns** - Avoid overly broad triggers
3. **Test hooks manually first** - Verify behavior before enabling
4. **Document hook purpose** - Use clear descriptions
5. **Consider performance** - Avoid heavy operations on frequent triggers

### Don'ts ❌

1. **Don't create circular triggers** - Hook A triggers Hook B triggers Hook A
2. **Don't run long commands on save** - Use async or background execution
3. **Don't expose secrets in commands** - Use environment variables
4. **Don't over-automate** - Some tasks need human judgment
5. **Don't ignore errors** - Handle command failures gracefully

## Troubleshooting

### Hook Not Triggering

1. Verify hook is enabled in configuration
2. Check file pattern matches target files
3. Ensure trigger event is correct
4. Look for errors in Kiro output panel

### Command Execution Fails

1. Test command manually in terminal first
2. Check working directory is correct
3. Verify all required tools are installed
4. Check environment variables are set

### Message Not Appearing in Context

1. Verify `sendMessage` action is configured
2. Check message content is not empty
3. Ensure hook is not disabled
4. Review Kiro logs for errors

## Integration with Steering Documents

Hooks and steering documents work together:

```yaml
# Hook that references steering document
name: "Apply Coding Standards"
trigger:
  event: onFileSave
  filePattern: "backend/**/*.py"
action:
  type: sendMessage
  message: |
    File saved. Please verify it follows the coding standards
    defined in .kiro/steering/coding-standards.md
```

## Summary

Kiro hooks provide powerful automation for development workflows. By following this guide, team members can:

1. Create hooks for common automation needs
2. Choose appropriate triggers and actions
3. Use variables for dynamic behavior
4. Adapt the pattern for other tools
5. Troubleshoot common issues

For questions or improvements to this guide, please update this document or discuss with the team.
