# Kiro Powers Guide

This folder contains comprehensive documentation for creating, testing, and executing Kiro Powers. It's designed for both human developers and LLM agents.

## What Are Kiro Powers?

Kiro Powers are modular capability packages that extend the LLM's abilities by bundling:
- **Documentation** (POWER.md) - Usage instructions and context
- **Steering Files** - Workflow guides for specific tasks
- **MCP Servers** (optional) - External tools via Model Context Protocol

Powers provide a structured way to add domain-specific capabilities while keeping the LLM's base context minimal.

## Power Types

| Type | Has mcp.json | Use Case |
|------|--------------|----------|
| **Guided MCP Power** | ✅ Yes | Connect to MCP servers with documentation |
| **Knowledge Base Power** | ❌ No | Pure documentation (CLI guides, best practices) |

## Power Structure

```
power-name/
├── POWER.md              # Required: metadata + documentation
├── mcp.json              # Optional: MCP server config (Guided MCP Powers only)
└── steering/             # Optional: workflow guides
    ├── getting-started.md
    └── advanced-usage.md
```

---

## Documentation Index

### Main Documentation
- [POWER.md](POWER.md) - Complete concepts, schemas, and best practices for power creation

### Steering Files (Workflow Guides)
| File | Purpose | Audience |
|------|---------|----------|
| [interactive.md](steering/interactive.md) | Step-by-step power creation workflow | Humans + LLMs creating powers |
| [testing.md](steering/testing.md) | Testing and validation procedures | Humans + LLMs testing powers |
| [llm-execution-guide.md](steering/llm-execution-guide.md) | Power execution patterns | LLMs using powers |
| [quick-reference.md](steering/quick-reference.md) | Condensed reference card | Quick lookups |
| [steering-files-guide.md](steering/steering-files-guide.md) | Creating steering documents | Humans + LLMs |

---

## Quick Start

### For Creating Powers

1. Read **[POWER.md](POWER.md)** to understand power concepts and structure
2. Follow **[steering/interactive.md](steering/interactive.md)** for guided creation
3. Use **[steering/testing.md](steering/testing.md)** to validate your power
4. Reference **[steering/quick-reference.md](steering/quick-reference.md)** for quick lookups

### For LLMs Executing Powers

1. Read **[steering/llm-execution-guide.md](steering/llm-execution-guide.md)** for execution patterns
2. Understand the power lifecycle: `list → activate → use → readSteering`
3. Follow keyword-based activation for proactive power usage

---

## Power Lifecycle (For LLM Usage)

```
┌─────────────────────────────────────────────────────────────────┐
│                     POWER LIFECYCLE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DISCOVERY (list)                                            │
│     └─> Scan installed powers                                   │
│     └─> Return: name, description, keywords, MCP servers        │
│                                                                  │
│  2. ACTIVATION (activate)                                       │
│     └─> Load POWER.md documentation                             │
│     └─> Load MCP tool schemas (if any)                          │
│     └─> Return: overview, toolsByServer, steeringFiles          │
│                                                                  │
│  3. EXECUTION (use)                                             │
│     └─> Route to correct MCP server                             │
│     └─> Execute tool with provided arguments                    │
│     └─> Return: tool execution result                           │
│                                                                  │
│  4. GUIDANCE (readSteering)                                     │
│     └─> Load specific steering file                             │
│     └─> Return: detailed workflow instructions                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Keyword-Based Activation

Powers define keywords that trigger proactive activation. When user message contains matching keywords, the LLM should activate the power immediately.

**Example**: A power with keywords `["weather", "forecast", "temperature"]` should activate when user asks "What's the weather in Tokyo?"

---

## Power Actions Reference

### 1. list - Discover Installed Powers
```json
// Returns
{
  "powers": [
    {
      "name": "power-name",
      "description": "What it does",
      "keywords": ["keyword1", "keyword2"],
      "mcpServers": ["server1", "server2"]
    }
  ]
}
```

### 2. activate - Load Power Context
```json
// Parameters: powerName (required)
// Returns
{
  "powerName": "power-name",
  "overview": "Complete POWER.md content",
  "toolsByServer": {
    "server-name": [
      { "name": "tool_name", "inputSchema": {...} }
    ]
  },
  "steeringFiles": ["getting-started.md"]
}
```

### 3. use - Execute Power Tools
```
// Parameters
- powerName (required): The power containing the tool
- serverName (required): MCP server name (from toolsByServer keys)
- toolName (required): Tool to execute
- arguments (required): Tool parameters matching inputSchema
```

### 4. readSteering - Get Workflow Guides
```
// Parameters
- powerName (required): Name of the power
- steeringFile (required): File name from steeringFiles array
```

### 5. configure - Open Management UI
Opens the Powers management panel for installation/configuration.

---

## Complete Usage Example

```
User: "What's the weather forecast for Seattle?"

LLM Process:
1. Recognize "weather" and "forecast" match power keywords
2. list → Found: weather-power
3. activate(powerName="weather-power")
   → toolsByServer: { "weather-api": [{ name: "get_forecast", ... }] }
4. use(powerName="weather-power", serverName="weather-api", 
       toolName="get_forecast", arguments={ "location": "Seattle" })
   → { "forecast": "Partly cloudy, 58°F" }
```

---

## Creating a Power

### Step 1: Define POWER.md with Frontmatter

```yaml
---
name: "my-power"              # Required: kebab-case
displayName: "My Power"       # Required: human-readable
description: "What it does"   # Required: max 3 sentences
keywords: ["key1", "key2"]    # Optional: 5-7 terms
author: "Your Name"           # Optional
---

# My Power

## Overview
[What this power does and when to use it]

## Available Tools
[Document each tool if MCP power]

## Best Practices
[Guidelines for effective usage]
```

### Step 2: Add mcp.json (For Guided MCP Powers)

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": { "API_KEY": "${ENV_VAR}" }
    }
  }
}
```

### Step 3: Add Steering Files (Optional)

Create workflow guides in `steering/` directory for complex use cases.

---

## Best Practices

### For Power Creation
- Keep powers focused on a single domain
- Write comprehensive POWER.md documentation
- Choose specific, relevant keywords (5-7 terms)
- Document all tool parameters with types
- Default to single power (only split with strong conviction)

### For LLM Execution
- **Always activate before use** - Never guess tool names or parameters
- **Match keywords proactively** - Activate powers when keywords match
- **Read steering files** - Use them for complex workflows
- **Follow POWER.md instructions** - They contain domain-specific guidance

---

## Implementing Powers in Other Systems

### Power Registry Pattern

```python
class PowerRegistry:
    def discover_powers(self) -> list:
        """Scan and register all installed powers."""
        pass
    
    def activate(self, power_name: str) -> dict:
        """Load full power context."""
        pass
    
    def execute_tool(self, power_name, server_name, tool_name, args) -> dict:
        """Execute an MCP tool."""
        pass
```

### Keyword Matching

```python
def should_activate_power(user_message: str, power_keywords: list) -> bool:
    message_lower = user_message.lower()
    return any(keyword.lower() in message_lower for keyword in power_keywords)
```

---

## Related Resources

- [Kiro Steering Guide](../kiro-steering-guide.md) - Configure agent behavior with steering files
- [Kiro Spec-Driven Development Guide](../kiro-spec-driven-development-guide.md) - Build features with structured specs
- [Kiro MCP Documentation](https://kiro.dev/docs/mcp/)
- [Kiro Powers Documentation](https://kiro.dev/docs/powers/)
