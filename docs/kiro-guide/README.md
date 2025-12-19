# Kiro Guide

Documentation for extending and customizing Kiro AI capabilities.

## Core Guides

| Guide | Description |
|-------|-------------|
| [Steering Guide](kiro-steering-guide.md) | Configure agent behavior with steering files |
| [Spec-Driven Development](kiro-spec-driven-development-guide.md) | Build features with structured specs |
| [Hooks Guide](kiro-hooks-guide.md) | Automate agent execution with event-driven hooks |
| [Context & References](kiro-context-and-references-guide.md) | Use context keys (#File, #Codebase, etc.) and file references |
| [MCP Configuration](kiro-mcp-configuration-guide.md) | Configure MCP servers for external tools |

## Workflow & Collaboration

| Guide | Description |
|-------|-------------|
| [Workflow Patterns](kiro-workflow-patterns-guide.md) | Common workflows combining Kiro features |
| [Autonomy Modes](kiro-autonomy-modes-guide.md) | Manage file changes with Autopilot/Supervised modes |
| [Team Collaboration](kiro-team-collaboration-guide.md) | Share configurations and work together |
| [Troubleshooting](kiro-troubleshooting-guide.md) | Diagnose and fix common issues |
| [Migration Guide](kiro-migration-guide.md) | Transition from Cursor, Copilot, Continue, etc. |

## Extension Systems

| System | Description |
|--------|-------------|
| [Powers](power/README.md) | Extend Kiro with MCP-based capabilities |
| [Skills](skill/README.md) | Create modular AI agent skills |

## Quick Links

### Steering
- Inclusion types: `always`, `fileMatch`, `manual`
- Location: `.kiro/steering/*.md`
- File references: `#[[file:path/to/file.md]]`
- See: [Steering Guide](kiro-steering-guide.md)

### Context Keys
- `#File:path` - Reference specific files
- `#Folder:path` - Reference directories
- `#Codebase` - Search entire project
- `#Problems` - Current file diagnostics
- `#Terminal` - Recent terminal output
- `#Git Diff` - Current changes
- See: [Context & References Guide](kiro-context-and-references-guide.md)

### Spec-Driven Development
- Structured feature development with requirements → design → tasks
- Location: `.kiro/specs/`
- See: [Spec-Driven Development Guide](kiro-spec-driven-development-guide.md)

### MCP Configuration
- Workspace config: `.kiro/settings/mcp.json`
- User config: `~/.kiro/settings/mcp.json`
- See: [MCP Configuration Guide](kiro-mcp-configuration-guide.md)

### Powers
- Lifecycle: `list → activate → use → readSteering`
- Types: Guided MCP Power, Knowledge Base Power
- [Power Creation Guide](power/POWER.md)
- [LLM Execution Guide](power/steering/llm-execution-guide.md)

### Skills
- Structure: `SKILL.md` + scripts + references + assets
- [Skill Format](skill/references/skill-format.md)
- [Design Patterns](skill/references/design-patterns.md)

### Hooks
- Triggers: `onFileSave`, `onAgentComplete`, `onSessionCreate`, `onManualTrigger`
- Actions: `sendMessage`, `executeCommand`
- Access: Explorer view → Agent Hooks, or Command Palette → "Open Kiro Hook UI"
- See: [Hooks Guide](kiro-hooks-guide.md)

### Autonomy Modes
- **Autopilot**: Files modified autonomously
- **Supervised**: Review changes before/after
- See: [Autonomy Modes Guide](kiro-autonomy-modes-guide.md)

### Team Collaboration
- Commit `.kiro/steering/` and `.kiro/specs/`
- Use environment variables for secrets
- See: [Team Collaboration Guide](kiro-team-collaboration-guide.md)
