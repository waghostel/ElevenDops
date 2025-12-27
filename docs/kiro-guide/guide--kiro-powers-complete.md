# Kiro Powers Complete Guide

> **Note:** This document consolidates the former KIRO_POWERS_COMPREHENSIVE_GUIDE.md and power/POWER.md files.

Complete guide for using and building Kiro Powers with MCP integration.

---

## Table of Contents

1. [What are Kiro Powers?](#what-are-kiro-powers)
2. [Executing Powers](#executing-powers)
3. [Power Types](#power-types)
4. [Building Powers](#building-powers)
5. [POWER.md Frontmatter](#powermd-frontmatter)
6. [MCP Configuration](#mcp-configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## What are Kiro Powers?

Kiro Powers are modular capability packages that extend Kiro's functionality through:

- **Documentation** - POWER.md files with usage instructions
- **Workflow Guides** - Steering files for guided workflows
- **MCP Servers** - Model Context Protocol servers providing tools

Powers enable Kiro to interact with external services (Postman, databases, cloud providers) through a standardized interface.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Kiro IDE                             │
├─────────────────────────────────────────────────────────┤
│                   kiroPowers Tool                        │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌───────────┐ │
│  │  list   │  │ activate │  │   use   │  │readSteering│ │
│  └─────────┘  └──────────┘  └─────────┘  └───────────┘ │
├─────────────────────────────────────────────────────────┤
│                    MCP Protocol                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Postman    │  │   Weather   │  │  Custom Power   │ │
│  │  MCP Server │  │  MCP Server │  │   MCP Server    │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Executing Powers

### Step 1: List Available Powers

```
kiroPowers action="list"
```

Returns installed powers with `name`, `description`, `keywords`, `MCP servers`.

### Step 2: Activate a Power (REQUIRED)

**Always activate before using any power tools:**

```
kiroPowers action="activate" powerName="postman"
```

Returns `overview`, `toolsByServer`, `steeringFiles`, `powerMdFound`.

### Step 3: Use Power Tools

```
kiroPowers action="use"
  powerName="postman"
  serverName="postman"
  toolName="runCollection"
  arguments={"collectionId": "...", "environmentId": "..."}
```

### Step 4: Read Steering Files (Optional)

```
kiroPowers action="readSteering"
  powerName="postman"
  steeringFile="getting-started.md"
```

### Step 5: Configure Powers

```
kiroPowers action="configure"
```

Opens the Powers management panel for installing/managing powers.

---

## Power Types

### 1. Guided MCP Power 🎯

Powers that connect to MCP servers with comprehensive documentation.

**Structure:**

- `POWER.md` - Onboarding, workflows, troubleshooting
- `mcp.json` - MCP server configuration (required)
- Optional: `steering/` for workflow guides

**Examples:** Generate Release Notes, Supabase Local Dev, Supabase Remote Dev

### 2. Knowledge Base Power 📚

Pure documentation without MCP server connection.

**Structure:**

- `POWER.md` - Knowledge base content
- Optional: `steering/` for organized documentation
- **No mcp.json** file

**Examples:** Terraform CLI Guide, Best Practices Guide, Security Checklist

### Decision Matrix

| Question                | Guided MCP Power | Knowledge Base Power |
| ----------------------- | ---------------- | -------------------- |
| Connects to MCP server? | ✅ Yes           | ❌ No                |
| Has mcp.json?           | ✅ Yes           | ❌ No                |
| Documents CLI tool?     | ❌ No            | ✅ Often             |
| Pure documentation?     | ❌ No            | ✅ Yes               |

---

## Building Powers

### Power Structure Patterns

**Pattern A: Simple Power (Most Common)**

```
weather/
├── mcp.json    # MCP server config
└── POWER.md    # Everything: metadata + docs + steering
```

**Pattern B: Multiple Workflow Power**

```
playwright/
├── mcp.json
├── POWER.md
└── steering/
    ├── web-scraping.md
    ├── e2e-testing.md
    └── performance.md
```

**Pattern C: Knowledge Base Power (No MCP)**

```
testing-strategies/
├── POWER.md
└── steering/
    ├── unit-testing.md
    ├── integration-testing.md
    └── e2e-testing.md
```

### Required Components

**ALL powers MUST have:**

1. **POWER.md** (required) - With complete frontmatter metadata

**Guided MCP Powers ALSO need:** 2. **mcp.json** (required) - MCP server configuration

**Powers with multiple workflows MAY have:** 3. **steering/** directory (optional) - Additional dynamic content

---

## POWER.md Frontmatter

**Only these 5 fields exist:**

```yaml
---
name: "power-name"
displayName: "Human Readable Name"
description: "Clear description (max 3 sentences)"
keywords: ["keyword1", "keyword2", "keyword3"]
author: "Your Name"
---
```

**Required:** `name`, `displayName`, `description`  
**Optional:** `keywords`, `author`

**Recommended POWER.md Sections:**

- Overview
- Available Steering Files
- Available MCP Servers
- Tool Usage Examples
- Best Practices
- Troubleshooting
- Configuration

---

## MCP Configuration

### mcp.json Format

**Local (STDIO) MCP Server:**

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@org/mcp-server-package"],
      "env": { "API_KEY": "${API_KEY}" },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Remote (HTTP/SSE) MCP Server:**

```json
{
  "mcpServers": {
    "my-server": {
      "url": "https://mcp.example.com/endpoint",
      "headers": { "Authorization": "Bearer ${API_KEY}" }
    }
  }
}
```

### Configuration Locations

| Level     | Path                        | Precedence     |
| --------- | --------------------------- | -------------- |
| Workspace | `.kiro/settings/mcp.json`   | Highest        |
| User      | `~/.kiro/settings/mcp.json` | Lower          |
| Powers    | `~/.kiro/powers.mcp.json`   | Auto-generated |

---

## Best Practices

### Power Granularity

⭐ **A single power is perfectly fine for most cases.** Do NOT default to splitting powers.

**Only split when there's strong conviction that workflows are:**

- Completely independent and never used together
- In different environments (local vs remote)
- Require different setups or configurations

**Keep together (most cases):** terraform, git, docker, aws-cli, kubectl, postgresql

### Naming Conventions

| Type          | Format     | Examples                                            |
| ------------- | ---------- | --------------------------------------------------- |
| Power Names   | kebab-case | `generate-release-notes`, `track-competitor-prices` |
| Display Names | Title Case | "Generate Release Notes"                            |
| Keywords      | lowercase  | 5-7 relevant terms                                  |

### For Power Users (LLM Agents)

1. **Always activate first** - Get tool schemas before using
2. **Check keywords** - Match user intent to power capabilities
3. **Read steering files** - Follow guided workflows
4. **Handle errors** - Provide helpful feedback on failures
5. **Update configurations** - Keep project files current

### For Power Developers

1. **Start with POWER.md** - Documentation first
2. **Design clear tool interfaces** - Simple, consistent APIs
3. **Never hardcode API keys** - Use environment variables
4. **Provide examples** - Show common use cases
5. **Test thoroughly** - Cover error scenarios
6. **Document limitations** - Be clear about what doesn't work

### Tool Design Principles

- **Single Responsibility** - Each tool does one thing well
- **Consistent Naming** - Use verb_noun pattern (get_user, create_item)
- **Predictable Outputs** - Consistent response structures
- **Idempotency** - Safe to retry operations

---

## Troubleshooting

### Power Not Found

```
kiroPowers action="list"
kiroPowers action="configure"
```

### Tool Execution Fails

- Verify activation: `kiroPowers action="activate"`
- Check serverName matches toolsByServer keys
- Validate arguments against inputSchema

### Authentication Errors

- Verify API key is set in environment
- Check mcp.json configuration
- Ensure key has required permissions

### Rate Limiting

- Add delays between requests
- Reduce batch sizes
- Check power documentation for limits

---

## Knowledge Base Power Patterns

### CLI Tool Guide

```markdown
## Onboarding

### Installation

### Prerequisites

### Basic Configuration

## Common Workflows

### Workflow 1: Initialize Project

### Workflow 2: Deploy Application

## Troubleshooting

### Error: "Command not found"

### Error: "Permission denied"
```

### Best Practices Guide

```markdown
## Overview

## Core Principles

## Patterns

### Pattern: Input Validation
```

### Reference Documentation

```markdown
## Quick Reference

### Common Commands

### Configuration Options

## API Reference
```

---

**Document Version:** 2.0 (Merged)  
**Last Updated:** December 26, 2025  
**Keywords:** kiro, powers, mcp, model-context-protocol, tools, automation, power-builder
