# Kiro Guide

Documentation for extending and customizing Kiro AI capabilities.

## Core Guides

| Guide | Description |
|-------|-------------|
| [Steering Guide](kiro-steering-guide.md) | Configure agent behavior with steering files |
| [Spec-Driven Development](kiro-spec-driven-development-guide.md) | Build features with structured specs |
| [Hooks Guide](kiro-hooks-guide.md) | Automate agent execution with event-driven hooks |

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

### Spec-Driven Development
- Structured feature development with requirements → design → tasks
- Location: `.kiro/specs/`

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
