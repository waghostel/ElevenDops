# Kiro Team Collaboration Guide

This guide explains best practices for sharing Kiro configurations across a team. It's designed for team members using different IDEs or LLM tools who need to understand or replicate collaboration patterns.

## What to Share

### Version Control Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHAT TO COMMIT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ COMMIT (share with team)                                    │
│  ├── .kiro/                                                     │
│  │   ├── steering/*.md          # Project rules                 │
│  │   ├── specs/**/*.md          # Feature specifications        │
│  │   └── settings/mcp.json      # Shared MCP servers            │
│  │                                                              │
│  ❌ DO NOT COMMIT (personal/sensitive)                          │
│  ├── ~/.kiro/                   # User-level config             │
│  ├── .env                       # API keys, secrets             │
│  └── .kiro/settings/mcp.json    # If contains personal servers  │
│      (with personal API keys)                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended .gitignore

```gitignore
# Kiro - DO NOT ignore these (share with team)
# .kiro/steering/
# .kiro/specs/

# Kiro - Ignore if contains secrets
# .kiro/settings/mcp.json  # Uncomment if MCP config has secrets

# Environment files (always ignore)
.env
.env.local
.env.*.local

# IDE-specific (personal preference)
.vscode/settings.json
.idea/
```

## Steering File Conventions

### Naming Convention

```
.kiro/steering/
├── project-overview.md       # Always: Project context
├── coding-standards.md       # Always: Code conventions
├── api-guidelines.md         # Always: API design rules
├── backend-patterns.md       # FileMatch: backend/**/*.py
├── frontend-patterns.md      # FileMatch: streamlit_app/**/*.py
├── testing-guidelines.md     # FileMatch: tests/**/*.py
└── onboarding.md             # Manual: New team member guide
```

### Standard Steering Files

Every project should have these core steering files:

**1. project-overview.md (Always)**
```markdown
---
inclusion: always
---

# Project Overview

## Purpose
[What the project does]

## Technology Stack
[List technologies]

## Architecture
[Key architectural decisions]

## Key References
- #[[file:docs/requirements.md]]
- #[[file:docs/api/index.md]]
```

**2. coding-standards.md (Always)**
```markdown
---
inclusion: always
---

# Coding Standards

## Project Structure
[Directory layout]

## Naming Conventions
[File, class, function naming]

## Code Style
[Formatting, documentation requirements]

## Testing Requirements
[Test patterns, coverage expectations]
```

**3. Domain-Specific (FileMatch)**
```markdown
---
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"
---

# Backend Development Guidelines

[Backend-specific rules]
```

### Team Review Process

```
┌─────────────────────────────────────────────────────────────────┐
│                STEERING FILE REVIEW PROCESS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Create/modify steering file                                 │
│         ↓                                                       │
│  2. Create PR with changes                                      │
│         ↓                                                       │
│  3. Team reviews for:                                           │
│     • Accuracy of rules                                         │
│     • Consistency with existing standards                       │
│     • Appropriate inclusion type                                │
│         ↓                                                       │
│  4. Merge after approval                                        │
│         ↓                                                       │
│  5. Team pulls latest steering files                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Spec Collaboration

### Spec Ownership

```markdown
## Spec Ownership Model

- **Creator**: Writes initial spec, owns until completion
- **Reviewers**: Approve each phase (requirements, design, tasks)
- **Implementers**: Execute tasks (can be creator or others)

## Handoff Process

1. Creator completes spec through tasks.md
2. Creator assigns to implementer
3. Implementer reads full spec before starting
4. Implementer executes tasks, updates status
5. Creator reviews completed implementation
```

### Spec Status Tracking

Add status header to specs:

```markdown
# Feature: Audio Upload

**Status**: In Progress
**Owner**: @developer-name
**Created**: 2024-01-15
**Phase**: Implementation (Task 3/7)

---

[Rest of spec content]
```

### Collaborative Spec Review

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC REVIEW WORKFLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Requirements Phase                                             │
│  ├── Creator drafts requirements.md                             │
│  ├── Share in PR or team channel                                │
│  ├── Team reviews for completeness                              │
│  └── Approve before proceeding to design                        │
│                                                                 │
│  Design Phase                                                   │
│  ├── Creator drafts design.md                                   │
│  ├── Technical review by senior dev                             │
│  ├── Check architecture alignment                               │
│  └── Approve before proceeding to tasks                         │
│                                                                 │
│  Tasks Phase                                                    │
│  ├── Creator drafts tasks.md                                    │
│  ├── Review task breakdown                                      │
│  ├── Estimate effort                                            │
│  └── Approve before implementation                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Configuration Sharing

### Shared vs Personal Servers

```json
// .kiro/settings/mcp.json (SHARED - commit this)
{
  "mcpServers": {
    "project-docs": {
      "command": "uvx",
      "args": ["docs-server@latest"],
      "env": {
        "DOCS_PATH": "./docs"
      },
      "disabled": false
    }
  }
}
```

```json
// ~/.kiro/settings/mcp.json (PERSONAL - don't commit)
{
  "mcpServers": {
    "my-private-server": {
      "command": "uvx",
      "args": ["private-server@latest"],
      "env": {
        "API_KEY": "my-personal-key"
      }
    }
  }
}
```

### Environment Variable Pattern

For servers requiring API keys:

```json
// .kiro/settings/mcp.json (safe to commit)
{
  "mcpServers": {
    "api-server": {
      "command": "uvx",
      "args": ["api-server@latest"],
      "env": {
        "API_KEY": "${env:SHARED_API_KEY}"
      }
    }
  }
}
```

Team members set `SHARED_API_KEY` in their local environment.

## Hook Sharing

### Shared Hooks

Hooks that benefit the whole team:

```yaml
# Auto-test on save (shared)
name: "Team Test Runner"
trigger:
  event: onFileSave
  filePattern: "**/*.py"
action:
  type: executeCommand
  command: "pytest tests/ -v --tb=short"
description: "Run tests on Python file save"
```

### Personal Hooks

Hooks for individual preferences:

```yaml
# Personal reminder (not shared)
name: "My Code Review Checklist"
trigger:
  event: onManualTrigger
action:
  type: sendMessage
  message: "My personal review checklist..."
```

### Hook Documentation

Document shared hooks in steering:

```markdown
---
inclusion: always
---

# Team Hooks

## Available Hooks

| Hook | Trigger | Action | Purpose |
|------|---------|--------|---------|
| Test Runner | onFileSave (*.py) | Run pytest | Auto-test |
| Lint Check | onFileSave (*.py) | Run ruff | Code quality |
| Doc Sync | onFileSave (docs/*) | Notify | Keep docs current |

## Creating New Hooks

1. Discuss with team before adding shared hooks
2. Document in this file
3. Test thoroughly before enabling for all
```

## Onboarding New Team Members

### Onboarding Checklist

```markdown
# New Team Member Onboarding

## Day 1: Setup
- [ ] Clone repository
- [ ] Install dependencies (poetry install)
- [ ] Copy .env.example to .env
- [ ] Configure personal MCP servers (if any)
- [ ] Verify Kiro is working

## Day 2: Learn the System
- [ ] Read project-overview.md steering file
- [ ] Read coding-standards.md steering file
- [ ] Review existing specs in .kiro/specs/
- [ ] Understand hook configurations

## Day 3: First Task
- [ ] Pick a small task from existing spec
- [ ] Use supervised mode initially
- [ ] Ask questions in team channel
- [ ] Get code review on first PR
```

### Onboarding Steering File

Create `.kiro/steering/onboarding.md`:

```markdown
---
inclusion: manual
---

# Onboarding Guide

## Quick Start

1. **Setup Environment**
   ```bash
   git clone [repo-url]
   cd project
   poetry install
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Verify Setup**
   ```bash
   poetry run pytest tests/ -v
   poetry run uvicorn backend.main:app --reload
   ```

3. **Understand the Project**
   - Read #[[file:.kiro/steering/project-overview.md]]
   - Read #[[file:.kiro/steering/coding-standards.md]]
   - Browse #[[file:docs/README.md]]

## Key Concepts

### Kiro Features We Use
- **Steering**: Project rules in .kiro/steering/
- **Specs**: Feature planning in .kiro/specs/
- **Hooks**: Automation for testing

### Development Workflow
1. Create spec for new features
2. Get approval at each phase
3. Execute tasks one at a time
4. Run tests before committing

## Getting Help
- Team channel: #dev-help
- Documentation: docs/
- Ask Kiro: "Explain how [feature] works"
```

## Communication Patterns

### Sharing Context

When asking for help, share relevant context:

```markdown
## Good Help Request

"I'm working on the audio upload feature.

Spec: .kiro/specs/audio-upload/
Current task: Task 3 (implement validation)
Issue: Getting type error on line 45

Relevant files:
- backend/services/audio_service.py
- backend/models/audio.py

Error: [paste error]"
```

### Documenting Decisions

Record important decisions in steering or specs:

```markdown
## Decision Log

### 2024-01-15: Audio Format Support
**Decision**: Support MP3 and WAV only
**Reason**: ElevenLabs API limitation
**Impact**: Reject other formats at upload
**Decided by**: Team consensus

### 2024-01-10: Database Choice
**Decision**: Use Firestore
**Reason**: Serverless, scales automatically
**Impact**: NoSQL data modeling required
**Decided by**: Architecture review
```

## Conflict Resolution

### Steering Conflicts

When team members disagree on rules:

```
┌─────────────────────────────────────────────────────────────────┐
│                STEERING CONFLICT RESOLUTION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Document both perspectives                                  │
│         ↓                                                       │
│  2. Discuss in team meeting                                     │
│         ↓                                                       │
│  3. Try both approaches on small scale                          │
│         ↓                                                       │
│  4. Decide based on evidence                                    │
│         ↓                                                       │
│  5. Update steering with decision + rationale                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Spec Conflicts

When implementation differs from spec:

1. **Stop implementation**
2. **Document the conflict**
3. **Discuss with spec owner**
4. **Update spec OR adjust implementation**
5. **Never silently deviate from spec**

## Best Practices

### Do's ✅

1. **Commit steering files** - Share project knowledge
2. **Review spec changes** - Ensure team alignment
3. **Document decisions** - Future reference
4. **Use consistent naming** - Easy to find files
5. **Keep steering current** - Update when practices change

### Don'ts ❌

1. **Don't commit secrets** - Use environment variables
2. **Don't skip reviews** - Steering affects everyone
3. **Don't create personal steering** - Use manual inclusion instead
4. **Don't ignore conflicts** - Resolve promptly
5. **Don't duplicate content** - Reference instead

## Adapting for Non-Kiro Users

### For Team Members Without Kiro

Share the knowledge even if they use different tools:

1. **Steering files are readable markdown** - Anyone can read them
2. **Specs are standard documents** - Follow the same process manually
3. **Patterns are transferable** - Apply concepts in any tool

### Creating Tool-Agnostic Documentation

```markdown
# Project Standards (Tool-Agnostic)

## For Kiro Users
- Steering files in .kiro/steering/
- Use #File: context keys
- Execute specs with Kiro

## For Other AI Tools
- Read .kiro/steering/*.md for context
- Copy relevant sections to your tool's context
- Follow the same patterns manually

## For Manual Development
- Reference .kiro/steering/ for standards
- Follow spec structure for planning
- Use checklists from hooks as reminders
```

## Summary

Effective team collaboration with Kiro requires:

1. **Shared steering** - Consistent rules for everyone
2. **Spec reviews** - Team alignment on features
3. **Clear ownership** - Know who's responsible
4. **Good communication** - Share context effectively
5. **Documentation** - Record decisions and patterns

For questions or improvements to this guide, please update this document or discuss with the team.
