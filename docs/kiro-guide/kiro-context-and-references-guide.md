# Kiro Context and References Guide

This guide explains how to provide context to Kiro using context keys and file references. It's designed for team members using different IDEs or LLM tools who need to understand or replicate this pattern.

## What Are Context Keys?

Context keys are special prefixes (starting with `#`) that tell Kiro to include specific information in the conversation. They allow you to:
- Reference specific files or folders
- Include diagnostic information
- Share terminal output
- Show git changes
- Search the entire codebase

## Available Context Keys

| Key | Description | Use Case |
|-----|-------------|----------|
| `#File` | Reference a specific file | "Check #File:backend/main.py for errors" |
| `#Folder` | Reference a folder's contents | "Review #Folder:backend/services" |
| `#Codebase` | Search entire indexed codebase | "Find all API endpoints in #Codebase" |
| `#Problems` | Current file's diagnostics | "Fix the #Problems in this file" |
| `#Terminal` | Recent terminal output | "Explain the error in #Terminal" |
| `#Git Diff` | Current git changes | "Review my #Git Diff" |

## Using Context Keys

### #File - Reference Specific Files

**Syntax**: `#File:path/to/file.ext` or select from autocomplete

**Examples**:
```
Review #File:backend/main.py for security issues

Compare #File:backend/config.py with #File:backend/config.example.py

The function in #File:backend/services/audio.py needs optimization
```

**How it works**:
1. Type `#File` in chat
2. Autocomplete shows available files
3. Select file or type path manually
4. File content is included in context

### #Folder - Reference Directories

**Syntax**: `#Folder:path/to/folder` or select from autocomplete

**Examples**:
```
Explain the structure of #Folder:backend/api

Review all services in #Folder:backend/services

What tests exist in #Folder:tests
```

**How it works**:
1. Type `#Folder` in chat
2. Select folder from autocomplete
3. Folder structure and file contents are included

### #Codebase - Search Entire Project

**Syntax**: `#Codebase` followed by your query

**Examples**:
```
Find all ElevenLabs API calls in #Codebase

Where is authentication implemented in #Codebase

Show all Pydantic models in #Codebase
```

**How it works**:
1. Kiro indexes your workspace
2. Semantic search finds relevant code
3. Matching files/snippets are included in context

**Note**: Codebase search requires indexing to be complete.

### #Problems - Current File Diagnostics

**Syntax**: `#Problems`

**Examples**:
```
Fix the #Problems in this file

Explain what's causing the #Problems

Are the #Problems related to type errors?
```

**How it works**:
1. Kiro reads diagnostics from language server
2. Errors, warnings, and hints are included
3. Context includes line numbers and messages

### #Terminal - Terminal Output

**Syntax**: `#Terminal`

**Examples**:
```
Explain the error in #Terminal

Why did the test fail? See #Terminal

Parse the output in #Terminal and suggest fixes
```

**How it works**:
1. Recent terminal output is captured
2. Includes stdout and stderr
3. Useful for debugging command failures

### #Git Diff - Current Changes

**Syntax**: `#Git Diff`

**Examples**:
```
Review my #Git Diff before I commit

Are there any issues with the #Git Diff

Summarize what changed in #Git Diff
```

**How it works**:
1. Kiro reads current git diff
2. Shows staged and unstaged changes
3. Includes file paths and line changes

## File References in Documents

### Syntax

Use this syntax in steering files, specs, and documentation:

```markdown
#[[file:relative/path/to/file.md]]
```

### Examples

```markdown
# Project Overview

## Key Reference Documents
- **User Requirements**: #[[file:user-need/user-need-phase1.md]]
- **API Documentation**: #[[file:docs/elevenlabs-api/index.md]]
- **Coding Standards**: #[[file:.kiro/steering/coding-standards.md]]

## Related Specs
See the implementation details in #[[file:.kiro/specs/feature-name/design.md]]
```

### Where File References Work

| Location | Supported | Notes |
|----------|-----------|-------|
| Steering files (`.kiro/steering/*.md`) | ✅ | Auto-resolved when steering is loaded |
| Spec documents (`.kiro/specs/**/*.md`) | ✅ | Resolved during spec execution |
| Regular markdown files | ⚠️ | Only when explicitly referenced |
| Chat messages | ❌ | Use `#File:` syntax instead |

### Resolution Rules

1. Paths are relative to workspace root
2. File must exist at specified path
3. No spaces in syntax: `#[[file:path]]` not `#[[ file: path ]]`
4. Content is expanded inline when document is processed

## Combining Context Keys

You can use multiple context keys in a single message:

```
Compare #File:backend/services/audio.py with #File:backend/services/elevenlabs_service.py
and check if they follow the patterns in #Folder:backend/api

Also fix any #Problems in the current file.
```

## Context Key Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT RESOLUTION FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                               │
│  │ User Message │  "Fix #Problems in #File:backend/main.py"     │
│  └──────┬───────┘                                               │
│         ↓                                                       │
│  ┌──────────────────────────────────────────┐                   │
│  │ 1. PARSE CONTEXT KEYS                    │                   │
│  │    • Identify #Problems                  │                   │
│  │    • Identify #File:backend/main.py      │                   │
│  └──────┬───────────────────────────────────┘                   │
│         ↓                                                       │
│  ┌──────────────────────────────────────────┐                   │
│  │ 2. RESOLVE EACH KEY                      │                   │
│  │    • #Problems → Read diagnostics        │                   │
│  │    • #File → Read file content           │                   │
│  └──────┬───────────────────────────────────┘                   │
│         ↓                                                       │
│  ┌──────────────────────────────────────────┐                   │
│  │ 3. BUILD CONTEXT                         │                   │
│  │    • Combine resolved content            │                   │
│  │    • Add to LLM prompt                   │                   │
│  └──────┬───────────────────────────────────┘                   │
│         ↓                                                       │
│  ┌──────────────────────────────────────────┐                   │
│  │ 4. EXECUTE                               │                   │
│  │    • LLM processes with full context     │                   │
│  │    • Response addresses specific files   │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Creating Documents with File References

### Step 1: Identify Dependencies

List all files your document depends on:
- Configuration files
- Related documentation
- API specifications
- Schema definitions

### Step 2: Add References

```markdown
---
inclusion: always
---

# My Steering Document

## Overview
This document guides development of the audio feature.

## Key References
- **API Spec**: #[[file:docs/elevenlabs-api/audio-api.md]]
- **Data Models**: #[[file:backend/models/audio.py]]
- **Service Layer**: #[[file:backend/services/audio_service.py]]

## Guidelines
When implementing audio features, follow the patterns in 
#[[file:backend/services/elevenlabs_service.py]]
```

### Step 3: Verify References

Ensure all referenced files exist:
```bash
# Check if referenced files exist
ls docs/elevenlabs-api/audio-api.md
ls backend/models/audio.py
ls backend/services/audio_service.py
```

## Adapting for Other LLM Tools

### For Cursor

Cursor uses `@` symbol for context:
- `@file` - Reference files
- `@folder` - Reference folders
- `@codebase` - Search codebase
- `@docs` - Reference documentation

### For Continue

Continue uses similar patterns:
- `/file` - Reference files
- `/folder` - Reference folders
- Context providers for custom sources

### For Direct LLM API Usage

Implement context resolution programmatically:

```python
import re
from pathlib import Path

def resolve_context_keys(message: str, workspace_root: str) -> str:
    """Resolve context keys in a message."""
    context_parts = []
    
    # Resolve #File:path references
    file_pattern = r'#File:([^\s]+)'
    for match in re.finditer(file_pattern, message):
        file_path = Path(workspace_root) / match.group(1)
        if file_path.exists():
            content = file_path.read_text()
            context_parts.append(f"=== {match.group(1)} ===\n{content}")
    
    # Resolve #[[file:path]] references
    ref_pattern = r'#\[\[file:([^\]]+)\]\]'
    for match in re.finditer(ref_pattern, message):
        file_path = Path(workspace_root) / match.group(1)
        if file_path.exists():
            content = file_path.read_text()
            context_parts.append(f"=== {match.group(1)} ===\n{content}")
    
    # Build final context
    if context_parts:
        context = "\n\n".join(context_parts)
        return f"{context}\n\n---\n\nUser message: {message}"
    
    return message

def resolve_problems(file_path: str) -> list:
    """Get diagnostics for a file (requires language server)."""
    # Implementation depends on your language server setup
    # Return list of {line, column, message, severity}
    pass

def resolve_git_diff() -> str:
    """Get current git diff."""
    import subprocess
    result = subprocess.run(
        ['git', 'diff', 'HEAD'],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### Implementing File Reference Resolution

```python
import re
from pathlib import Path

def expand_file_references(content: str, workspace_root: str) -> str:
    """Expand #[[file:path]] references in document content."""
    
    pattern = r'#\[\[file:([^\]]+)\]\]'
    
    def replace_reference(match):
        relative_path = match.group(1)
        file_path = Path(workspace_root) / relative_path
        
        if file_path.exists():
            file_content = file_path.read_text()
            return f"\n\n--- Begin {relative_path} ---\n{file_content}\n--- End {relative_path} ---\n\n"
        else:
            return f"[File not found: {relative_path}]"
    
    return re.sub(pattern, replace_reference, content)
```

## Best Practices

### Do's ✅

1. **Use specific file references** - `#File:backend/main.py` not just "the main file"
2. **Combine context keys** - Provide all relevant context in one message
3. **Keep references up to date** - Update when files move or rename
4. **Use relative paths** - Always relative to workspace root
5. **Reference relevant files** - Only include what's needed for the task

### Don'ts ❌

1. **Don't reference too many files** - Context has limits
2. **Don't use absolute paths** - They won't work for other team members
3. **Don't reference non-existent files** - Verify paths before using
4. **Don't forget to update references** - When refactoring, update docs too
5. **Don't include sensitive files** - No credentials or secrets

## Common Patterns

### Pattern 1: Bug Fix with Context

```
I'm seeing an error in #Terminal when running the tests.

The relevant code is in #File:backend/services/audio.py

Please fix the #Problems and explain what was wrong.
```

### Pattern 2: Code Review

```
Review my #Git Diff for the audio feature.

Make sure it follows the patterns in #Folder:backend/services

Check for any issues with the API design in #File:backend/api/audio.py
```

### Pattern 3: Feature Implementation

```
Implement the new endpoint following the spec in 
#File:.kiro/specs/audio-upload/design.md

Use the existing patterns from #Folder:backend/api

Reference the models in #File:backend/models/audio.py
```

### Pattern 4: Documentation with References

```markdown
---
inclusion: always
---

# Audio Service Guidelines

## API Reference
Follow the ElevenLabs API patterns: #[[file:docs/elevenlabs-api/index.md]]

## Implementation
Service implementation: #[[file:backend/services/audio_service.py]]
Data models: #[[file:backend/models/audio.py]]

## Testing
Test patterns: #[[file:tests/test_audio_service_props.py]]
```

## Troubleshooting

### File Not Found

1. Check path is relative to workspace root
2. Verify file exists at specified location
3. Check for typos in path
4. Ensure correct case (case-sensitive on Linux/Mac)

### Context Not Loading

1. Verify syntax is correct (`#File:` not `#file:`)
2. Check file is within workspace
3. Ensure file is not in `.gitignore` (for codebase search)
4. Try refreshing the index for `#Codebase`

### Reference Not Expanding

1. Check syntax: `#[[file:path]]` with no spaces
2. Verify file exists
3. Ensure document is being processed (steering files, specs)
4. Check for nested references (not supported)

## Summary

Context keys and file references enable:

1. **Precise context** - Reference exactly what's needed
2. **Dynamic documentation** - Keep docs in sync with code
3. **Efficient communication** - Less copy-pasting, more productivity
4. **Cross-file awareness** - LLM understands relationships

For questions or improvements to this guide, please update this document or discuss with the team.
