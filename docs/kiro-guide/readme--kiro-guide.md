# Kiro Guide

Documentation for extending and customizing Kiro AI capabilities.

## Core Guides

| Guide                                                             | Description                                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------------- |
| [Steering Guide](guide--kiro-steering.md)                         | Configure agent behavior with steering files                  |
| [Spec-Driven Development](guide--kiro-spec-driven-development.md) | Build features with structured specs                          |
| [Hooks Guide](guide--kiro-hooks.md)                               | Automate agent execution with event-driven hooks              |
| [Context & References](guide--kiro-context-and-references.md)     | Use context keys (#File, #Codebase, etc.) and file references |
| [MCP Configuration](guide--kiro-mcp-configuration.md)             | Configure MCP servers for external tools                      |

## Workflow & Collaboration

| Guide                                                   | Description                                         |
| ------------------------------------------------------- | --------------------------------------------------- |
| [Workflow Patterns](guide--kiro-workflow-patterns.md)   | Common workflows combining Kiro features            |
| [Autonomy Modes](guide--kiro-autonomy-modes.md)         | Manage file changes with Autopilot/Supervised modes |
| [Team Collaboration](guide--kiro-team-collaboration.md) | Share configurations and work together              |
| [Troubleshooting](guide--kiro-troubleshooting.md)       | Diagnose and fix common issues                      |
| [Migration Guide](guide--kiro-migration.md)             | Transition from Cursor, Copilot, Continue, etc.     |

## Extension Systems

| System                                                       | Description                                   |
| ------------------------------------------------------------ | --------------------------------------------- |
| [Powers](power/README.md)                                    | Extend Kiro with MCP-based capabilities       |
| [Skills](skill/README.md)                                    | Create modular AI agent skills                |
| [.agent Document](dot-agent-document/guide--agent-system.md) | Configure .agent folder for non-Kiro AI tools |

## Additional Resources

| Resource                                                      | Description                             |
| ------------------------------------------------------------- | --------------------------------------- |
| [Powers Complete Guide](guide--kiro-powers-complete.md)       | Comprehensive guide for Kiro Powers     |
| [Agent Hooks Reference](guide--kiro-agent-hooks-reference.md) | Complete reference for Kiro agent hooks |
| [Diagnostic Tool Research](research--kiro-diagnostic-tool.md) | Research notes on Kiro diagnostic tools |
| [Shell Integration Test](test--kiro-shell-integration.md)     | Shell integration test documentation    |

## Quick Links

### Steering

- Inclusion types: `always`, `fileMatch`, `manual`
- Location: `.kiro/steering/*.md`
- File references: `#[[file:path/to/file.md]]`
- See: [Steering Guide](guide--kiro-steering.md)

### Context Keys

- `#File:path` - Reference specific files
- `#Folder:path` - Reference directories
- `#Codebase` - Search entire project
- `#Problems` - Current file diagnostics
- `#Terminal` - Recent terminal output
- `#Git Diff` - Current changes
- See: [Context & References Guide](guide--kiro-context-and-references.md)

### Spec-Driven Development

- Structured feature development with requirements → design → tasks
- Location: `.kiro/specs/`
- See: [Spec-Driven Development Guide](guide--kiro-spec-driven-development.md)

### MCP Configuration

- Workspace config: `.kiro/settings/mcp.json`
- User config: `~/.kiro/settings/mcp.json`
- See: [MCP Configuration Guide](guide--kiro-mcp-configuration.md)

### Powers

- Lifecycle: `list → activate → use → readSteering`
- Types: Guided MCP Power, Knowledge Base Power
- [Power README](power/README.md)
- [LLM Execution Guide](power/steering/llm-execution-guide.md)

### Skills

- Structure: `SKILL.md` + scripts + references + assets
- [Skill Format](skill/references/skill-format.md)
- [Design Patterns](skill/references/design-patterns.md)

### .agent Document

- For non-Kiro AI tools (Gemini CLI, Claude, Copilot, etc.)
- [Agent System Guide](dot-agent-document/guide--agent-system.md)
- [Agent Workflows](dot-agent-document/guide--agent-workflows.md)
- [Agent vs Skill Comparison](dot-agent-document/guide--agent-vs-skill-comparison.md)

### Hooks

- Triggers: `onFileSave`, `onAgentComplete`, `onSessionCreate`, `onManualTrigger`
- Actions: `sendMessage`, `executeCommand`
- Access: Explorer view → Agent Hooks, or Command Palette → "Open Kiro Hook UI"
- See: [Hooks Guide](guide--kiro-hooks.md)

### Autonomy Modes

- **Autopilot**: Files modified autonomously
- **Supervised**: Review changes before/after
- See: [Autonomy Modes Guide](guide--kiro-autonomy-modes.md)

### Team Collaboration

- Commit `.kiro/steering/` and `.kiro/specs/`
- Use environment variables for secrets
- See: [Team Collaboration Guide](guide--kiro-team-collaboration.md)
