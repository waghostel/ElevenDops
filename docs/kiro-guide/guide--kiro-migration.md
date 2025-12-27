# Kiro Migration Guide

This guide helps developers transition from other AI coding assistants to Kiro. It maps familiar concepts and workflows to Kiro's features.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FEATURE MAPPING                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Other Tools              →        Kiro                         │
│  ─────────────────────────────────────────────────────          │
│  Rules/Instructions       →        Steering Files               │
│  Context/@ mentions       →        Context Keys (#)             │
│  Custom Commands          →        Hooks                        │
│  Project Context          →        Codebase Index               │
│  Tool Integration         →        MCP Servers                  │
│  Workflows/Agents         →        Specs                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## From GitHub Copilot

### Feature Mapping

| Copilot Feature | Kiro Equivalent | Notes |
|-----------------|-----------------|-------|
| Inline suggestions | Chat-based interaction | Kiro focuses on conversation |
| Copilot Chat | Kiro Chat | Similar experience |
| @workspace | #Codebase | Search entire project |
| @file | #File: | Reference specific files |
| .github/copilot-instructions.md | .kiro/steering/*.md | Project rules |

### Migration Steps

**1. Move Instructions to Steering**

Copilot instructions:
```markdown
<!-- .github/copilot-instructions.md -->
Use TypeScript for all new files.
Follow the existing code style.
Add JSDoc comments to functions.
```

Kiro steering:
```markdown
<!-- .kiro/steering/coding-standards.md -->
---
inclusion: always
---

# Coding Standards

## Language
- Use TypeScript for all new files

## Style
- Follow existing code patterns
- Add JSDoc comments to all functions
```

**2. Adapt Context Usage**

Copilot:
```
@workspace find all API endpoints
```

Kiro:
```
Find all API endpoints in #Codebase
```

**3. Leverage Additional Features**

Kiro offers features Copilot doesn't have:
- **Specs**: Structured feature development
- **Hooks**: Automated workflows
- **MCP**: External tool integration

---

## From Cursor

### Feature Mapping

| Cursor Feature | Kiro Equivalent | Notes |
|----------------|-----------------|-------|
| @file | #File: | Reference files |
| @folder | #Folder: | Reference folders |
| @codebase | #Codebase | Search project |
| @docs | MCP servers | External documentation |
| .cursorrules | .kiro/steering/*.md | Project rules |
| Composer | Specs | Multi-file changes |
| Cmd+K | Chat | Inline editing |

### Migration Steps

**1. Convert .cursorrules to Steering**

Cursor rules:
```
<!-- .cursorrules -->
You are an expert in Python and FastAPI.
Always use type hints.
Follow PEP 8 style guide.
Use pytest for testing.
```

Kiro steering:
```markdown
<!-- .kiro/steering/coding-standards.md -->
---
inclusion: always
---

# Coding Standards

## Expertise Context
This is a Python/FastAPI project.

## Code Style
- Always use type hints
- Follow PEP 8 style guide
- Use pytest for testing
```

**2. Adapt @ Mentions to # Context Keys**

Cursor:
```
@file:backend/main.py explain this code
@folder:backend/services review the structure
@codebase find authentication logic
```

Kiro:
```
Explain #File:backend/main.py
Review the structure of #Folder:backend/services
Find authentication logic in #Codebase
```

**3. Replace Composer with Specs**

Cursor Composer is ad-hoc multi-file editing.
Kiro Specs provide structured planning:

```
# Instead of ad-hoc Composer session:
"Add user authentication to the app"

# Use Kiro Specs:
"Create a spec for user authentication feature"
# → requirements.md (what to build)
# → design.md (how to build)
# → tasks.md (step-by-step plan)
# → Execute tasks one at a time
```

**4. Convert Custom Docs to MCP**

Cursor @docs:
```
@docs:react explain useEffect
```

Kiro MCP:
```json
// .kiro/settings/mcp.json
{
  "mcpServers": {
    "react-docs": {
      "command": "uvx",
      "args": ["react-docs-server@latest"]
    }
  }
}
```

Then use the MCP tools through Kiro Powers.

---

## From Continue

### Feature Mapping

| Continue Feature | Kiro Equivalent | Notes |
|------------------|-----------------|-------|
| /file | #File: | Reference files |
| /folder | #Folder: | Reference folders |
| /codebase | #Codebase | Search project |
| config.json | .kiro/settings/mcp.json | Configuration |
| Context Providers | MCP Servers | External data |
| Slash Commands | Hooks | Custom actions |
| .continuerules | .kiro/steering/*.md | Project rules |

### Migration Steps

**1. Convert Rules**

Continue rules:
```json
// .continuerules
{
  "rules": [
    "Use functional components in React",
    "Prefer async/await over promises"
  ]
}
```

Kiro steering:
```markdown
<!-- .kiro/steering/coding-standards.md -->
---
inclusion: always
---

# Coding Standards

## React
- Use functional components

## Async Code
- Prefer async/await over raw promises
```

**2. Migrate Context Providers to MCP**

Continue context provider:
```json
{
  "contextProviders": [
    {
      "name": "docs",
      "params": { "site": "https://docs.example.com" }
    }
  ]
}
```

Kiro MCP:
```json
{
  "mcpServers": {
    "docs": {
      "command": "uvx",
      "args": ["mcp-server-fetch@latest"],
      "env": {
        "BASE_URL": "https://docs.example.com"
      }
    }
  }
}
```

**3. Convert Slash Commands to Hooks**

Continue slash command:
```json
{
  "slashCommands": [
    {
      "name": "test",
      "description": "Run tests",
      "command": "npm test"
    }
  ]
}
```

Kiro hook:
```yaml
name: "Run Tests"
trigger:
  event: onManualTrigger
action:
  type: executeCommand
  command: "npm test"
```

---

## From Codeium/Windsurf

### Feature Mapping

| Codeium Feature | Kiro Equivalent | Notes |
|-----------------|-----------------|-------|
| Chat | Kiro Chat | Similar |
| @mention files | #File: | Reference files |
| Cascade | Specs | Multi-step workflows |
| Supercomplete | Chat-based | Different approach |

### Migration Steps

**1. Adapt Cascade to Specs**

Codeium Cascade handles multi-step tasks automatically.
Kiro Specs provide more control:

```
# Cascade approach (automatic)
"Build a REST API for users"

# Kiro Spec approach (controlled)
"Create a spec for user REST API"
# Review requirements → approve
# Review design → approve
# Review tasks → approve
# Execute tasks one at a time
```

**2. Use Steering for Context**

Instead of relying on automatic context:
```markdown
---
inclusion: always
---

# Project Context

## Architecture
- Backend: FastAPI
- Database: PostgreSQL
- Auth: JWT tokens

## Patterns
- Repository pattern for data access
- Service layer for business logic
```

---

## From ChatGPT/Claude Direct

### Feature Mapping

| Direct LLM | Kiro Equivalent | Notes |
|------------|-----------------|-------|
| System prompt | Steering files | Persistent rules |
| Copy-paste code | #File: references | Direct file access |
| Manual context | #Codebase search | Automatic discovery |
| Chat history | Session context | Maintained automatically |

### Migration Steps

**1. Convert System Prompts to Steering**

ChatGPT system prompt:
```
You are a senior Python developer. 
Always write type hints.
Use docstrings for all functions.
Follow clean code principles.
```

Kiro steering:
```markdown
---
inclusion: always
---

# Development Standards

## Code Quality
- Always include type hints
- Write docstrings for all functions
- Follow clean code principles

## Context
Senior Python development standards apply.
```

**2. Stop Copy-Pasting**

Instead of:
```
Here's my code:
[paste 200 lines]
What's wrong with it?
```

Use:
```
What's wrong with #File:backend/services/audio.py?
Check the #Problems in the current file.
```

**3. Use Codebase Search**

Instead of:
```
I have a function somewhere that handles authentication...
[paste multiple files trying to find it]
```

Use:
```
Find the authentication handler in #Codebase
```

---

## Common Migration Patterns

### Pattern 1: Project Setup

**Before (any tool)**:
- Manually explain project structure each session
- Copy-paste relevant code for context
- Repeat instructions frequently

**After (Kiro)**:
```markdown
<!-- .kiro/steering/project-overview.md -->
---
inclusion: always
---

# Project Overview
[Automatically included in every conversation]

## Structure
- backend/ - FastAPI
- frontend/ - React
- tests/ - pytest

## Key Files
- #[[file:backend/main.py]]
- #[[file:backend/config.py]]
```

### Pattern 2: Code Standards

**Before**:
- Remind AI of coding standards each time
- Fix style issues after generation
- Inconsistent output

**After**:
```markdown
<!-- .kiro/steering/coding-standards.md -->
---
inclusion: always
---

# Coding Standards
[Always applied to all code generation]

## Style
- 4 spaces indentation
- Max line length: 88
- Type hints required
```

### Pattern 3: Feature Development

**Before**:
- Ad-hoc requests
- Lost context between sessions
- No structured planning

**After**:
```
# Structured spec-driven development
.kiro/specs/feature-name/
├── requirements.md  # What to build
├── design.md        # How to build
└── tasks.md         # Step-by-step plan
```

### Pattern 4: Automation

**Before**:
- Manual test runs
- Remember to check things
- Inconsistent workflows

**After**:
```yaml
# Automated hooks
name: "Auto Test"
trigger:
  event: onFileSave
  filePattern: "**/*.py"
action:
  type: executeCommand
  command: "pytest tests/ -v"
```

---

## Migration Checklist

### Phase 1: Basic Setup
- [ ] Install Kiro
- [ ] Create `.kiro/steering/` directory
- [ ] Migrate existing rules to steering files
- [ ] Test basic chat functionality

### Phase 2: Context Migration
- [ ] Learn context key syntax (#File:, #Folder:, etc.)
- [ ] Set up codebase indexing
- [ ] Create project-overview.md steering
- [ ] Create coding-standards.md steering

### Phase 3: Advanced Features
- [ ] Configure MCP servers (if needed)
- [ ] Set up hooks for automation
- [ ] Create first spec for a feature
- [ ] Train team on new workflows

### Phase 4: Optimization
- [ ] Refine steering based on experience
- [ ] Add domain-specific steering (fileMatch)
- [ ] Document team conventions
- [ ] Share configurations with team

---

## Quick Reference: Syntax Comparison

### File References

| Tool | Syntax |
|------|--------|
| Cursor | `@file:path/to/file.py` |
| Continue | `/file path/to/file.py` |
| Copilot | `@file:path/to/file.py` |
| **Kiro** | `#File:path/to/file.py` |

### Folder References

| Tool | Syntax |
|------|--------|
| Cursor | `@folder:path/to/folder` |
| Continue | `/folder path/to/folder` |
| **Kiro** | `#Folder:path/to/folder` |

### Codebase Search

| Tool | Syntax |
|------|--------|
| Cursor | `@codebase query` |
| Continue | `/codebase query` |
| Copilot | `@workspace query` |
| **Kiro** | `#Codebase query` |

### Rules/Instructions

| Tool | Location |
|------|----------|
| Cursor | `.cursorrules` |
| Continue | `.continuerules` |
| Copilot | `.github/copilot-instructions.md` |
| **Kiro** | `.kiro/steering/*.md` |

---

## Kiro-Specific Advantages

### 1. Structured Development (Specs)
No other tool has built-in spec-driven development:
- Requirements → Design → Tasks → Implementation
- Approval gates at each phase
- Traceable implementation

### 2. Flexible Steering
More powerful than simple rules files:
- Multiple inclusion types (always, fileMatch, manual)
- File references for dynamic content
- Organized by concern

### 3. MCP Integration
Standard protocol for tool integration:
- Growing ecosystem of servers
- Custom server development
- Consistent interface

### 4. Automation (Hooks)
Built-in automation without external tools:
- Event-driven triggers
- Message and command actions
- IDE-integrated

---

## Getting Help

### Learning Resources
- Read other guides in `docs/kiro-guide/`
- Experiment with small projects first
- Ask Kiro to explain its features

### Common Questions

**Q: Can I use Kiro alongside other tools?**
A: Yes, but steering files are Kiro-specific. You can maintain both configurations.

**Q: Will my existing workflows break?**
A: No, Kiro is additive. Your code and git history remain unchanged.

**Q: How long does migration take?**
A: Basic setup: 30 minutes. Full adoption: 1-2 weeks of gradual transition.

## Summary

Migrating to Kiro involves:

1. **Converting rules** → Steering files
2. **Adapting syntax** → # context keys
3. **Learning new features** → Specs, Hooks, MCP
4. **Gradual adoption** → Start simple, add complexity

The investment pays off with:
- More consistent AI assistance
- Structured development workflows
- Better team collaboration
- Automated quality checks

For questions or improvements to this guide, please update this document or discuss with the team.
