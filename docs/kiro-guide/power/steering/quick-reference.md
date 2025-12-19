# Power Builder Quick Reference

A condensed reference for creating Kiro Powers. For detailed guidance, see POWER.md or use the interactive workflow.

---

## Power Types

| Type | Has mcp.json? | Use Case |
|------|---------------|----------|
| **Guided MCP Power** | ✅ Yes | Document MCP servers with tools |
| **Knowledge Base Power** | ❌ No | Pure documentation, CLI guides, best practices |

---

## Directory Structure

### Minimal Power
```
power-name/
├── POWER.md          # Required: metadata + documentation
└── mcp.json          # Required for Guided MCP Powers only
```

### Full Power
```
power-name/
├── POWER.md          # Required: metadata + documentation
├── mcp.json          # Optional: MCP server config
└── steering/         # Optional: workflow guides
    ├── workflow-1.md
    └── workflow-2.md
```

---

## POWER.md Template

```yaml
---
name: "power-name"              # Required: kebab-case
displayName: "Power Name"       # Required: human-readable
description: "What it does"     # Required: max 3 sentences
keywords: ["key1", "key2"]      # Optional: 5-7 terms
author: "Your Name"             # Optional
---

# Power Name

## Overview
[What this power does and why it's useful]

## Onboarding
[Prerequisites, installation, configuration]

## Common Workflows
[Step-by-step instructions with examples]

## Troubleshooting
[Common errors and solutions]

## Best Practices
[Key guidelines for using this power]
```

---

## mcp.json Template

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "API_KEY_ENV_VAR"
      }
    }
  }
}
```

### Remote MCP Server
```json
{
  "mcpServers": {
    "server-name": {
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  }
}
```

---

## Naming Conventions

| Element | Format | Example |
|---------|--------|---------|
| Power name | kebab-case | `pdf-processor` |
| Display name | Title Case | `PDF Processor` |
| Server name | kebab-case | `pdf-api` |

---

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Lowercase kebab-case identifier |
| `displayName` | ✅ | Human-readable title |
| `description` | ✅ | Clear description (max 3 sentences) |
| `keywords` | ❌ | Search keywords (5-7 recommended) |
| `author` | ❌ | Creator name or organization |

**Note**: Fields like `version`, `tags`, `repository`, `license` do NOT exist.

---

## When to Create Steering Files

✅ **Create steering/** when:
- POWER.md exceeds ~500 lines
- Power has independent workflows
- Progressive discovery improves usability

❌ **Don't create steering/** when:
- Power is simple (< 500 lines)
- All content is closely related
- Agents need all information upfront

---

## Keyword Selection Tips

✅ **Good keywords** (specific):
- `"elevenlabs"`, `"text-to-speech"`, `"voice-synthesis"`
- `"postgresql"`, `"database-migration"`
- `"terraform"`, `"infrastructure-as-code"`

❌ **Bad keywords** (too generic):
- `"help"`, `"create"`, `"get"`
- `"file"`, `"data"`, `"api"`
- `"test"`, `"debug"`

---

## Power Actions (for LLMs)

| Action | Purpose | When to Use |
|--------|---------|-------------|
| `list` | See installed powers | Starting a task |
| `activate` | Load power documentation | Before using tools |
| `use` | Execute MCP tool | After activation |
| `readSteering` | Get workflow guide | For complex tasks |
| `configure` | Open management UI | Installing powers |

---

## Testing Checklist

### Required
- [ ] POWER.md exists with valid frontmatter
- [ ] Directory name matches `name` field
- [ ] mcp.json uses `mcpServers` format (if applicable)
- [ ] Power installs successfully
- [ ] Agent activates for relevant queries

### Recommended
- [ ] Description is clear and concise
- [ ] 5-7 relevant keywords included
- [ ] Workflow examples included
- [ ] Troubleshooting section present

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Power not found | Missing POWER.md | Create POWER.md with frontmatter |
| Tool not found | Wrong tool name | Check `toolsByServer` from activate |
| Invalid arguments | Wrong parameters | Check tool's `inputSchema` |
| Power doesn't trigger | Vague keywords | Add specific, relevant keywords |

---

## File Locations

| Location | Purpose |
|----------|---------|
| `.kiro/settings/mcp.json` | Workspace MCP config |
| `~/.kiro/settings/mcp.json` | User-level MCP config |
| `~/.kiro/powers.mcp.json` | Auto-generated from powers |
| `.kiro/steering/` | Workspace steering files |
| `~/.kiro/steering/` | User-level steering files |

---

## Resources

- **Interactive Creation**: `readSteering` → `interactive.md`
- **Testing Guide**: `readSteering` → `testing.md`
- **LLM Execution**: `readSteering` → `llm-execution-guide.md`
- **Kiro MCP Docs**: https://kiro.dev/docs/mcp/
- **Kiro Powers Docs**: https://kiro.dev/docs/powers/
