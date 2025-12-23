# Kiro Powers - Comprehensive Guide

> **Purpose:** This document explains how Kiro Powers work, how to execute them, how to create new powers, and key considerations for power development.

## What are Kiro Powers?

Kiro Powers are modular capability packages that extend Kiro's functionality through:
- **Documentation** - POWER.md files with usage instructions
- **Workflow Guides** - Steering files for guided workflows
- **MCP Servers** - Model Context Protocol servers providing tools

Powers enable Kiro to interact with external services (Postman, databases, cloud providers) through a standardized interface.

## How Kiro Powers Work

### Architecture Overview

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

### Power Components

1. **POWER.md** - Main documentation file
2. **Steering Files** - Workflow guides (*.md in steering folder)
3. **MCP Server** - Backend service providing tools
4. **Configuration** - mcp.json settings

## Executing Kiro Powers

### Step 1: List Available Powers

```
kiroPowers action="list"
```

Returns installed powers with:
- `name` - Power identifier
- `description` - What the power does
- `keywords` - Search terms for matching
- `MCP servers` - Backend servers providing tools

### Step 2: Activate a Power (REQUIRED)

**Always activate before using any power tools:**

```
kiroPowers action="activate" powerName="postman"
```

Returns:
- `overview` - Complete POWER.md content
- `toolsByServer` - All available tools grouped by server
- `steeringFiles` - Available workflow guides
- `powerMdFound` - Whether documentation exists

### Step 3: Use Power Tools

```
kiroPowers action="use" 
  powerName="postman" 
  serverName="postman" 
  toolName="runCollection"
  arguments={"collectionId": "...", "environmentId": "..."}
```

**Required Parameters:**
- `powerName` - The power to use
- `serverName` - MCP server within the power (from activate response)
- `toolName` - Specific tool to execute (from activate response)
- `arguments` - Tool parameters matching inputSchema

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

## Power Execution Flow

```
┌──────────────────┐
│   User Request   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Keyword Match?  │──Yes──▶ Activate Power
└────────┬─────────┘
         │ No
         ▼
┌──────────────────┐
│   List Powers    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Activate Power   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Review Tools    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Use Tool(s)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Process Results  │
└──────────────────┘
```

## Creating a New Kiro Power

### Prerequisites

1. Install the "power-builder" power if available
2. Understand MCP (Model Context Protocol)
3. Have a clear use case for the power

### Power Structure

```
my-power/
├── POWER.md              # Main documentation (required)
├── steering/             # Workflow guides (optional)
│   ├── getting-started.md
│   └── advanced-usage.md
└── mcp-config.json       # MCP server configuration
```

### Step 1: Create POWER.md

```markdown
# My Power Name

Brief description of what this power does.

## Overview

Detailed explanation of capabilities.

## Available MCP Servers

### server-name
**Package:** `@org/mcp-server-package`
**Connection:** SSE or stdio
**Authentication:** Required credentials

**Available Tools:**
- `toolName` - Description of what it does
  - Parameters: param1 (type), param2 (type)

## Usage Examples

\`\`\`javascript
// Example tool call
mcp_server_toolName({
  "param1": "value1",
  "param2": "value2"
})
\`\`\`

## Configuration

\`\`\`json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["@org/mcp-server-package"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
\`\`\`
```

### Step 2: Create MCP Server Configuration

**For SSE-based servers (remote):**
```json
{
  "mcpServers": {
    "my-server": {
      "url": "https://mcp.example.com/endpoint",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

**For stdio-based servers (local):**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["@org/mcp-server-package"],
      "env": {
        "API_KEY": "${API_KEY}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Step 3: Create Steering Files (Optional)

```markdown
---
inclusion: manual
---

# Getting Started with My Power

## Prerequisites
- Required setup steps
- API keys needed

## Quick Start
1. Step one
2. Step two
3. Step three

## Common Workflows
...
```

### Step 4: Define Tool Schemas

Each tool should have:
- Clear name and description
- Input schema with required/optional parameters
- Expected output format
- Error handling

```typescript
interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: {
      [key: string]: {
        type: string;
        description: string;
        required?: boolean;
      };
    };
    required: string[];
  };
}
```

## Key Considerations for Power Development

### 1. Authentication & Security

- **Never hardcode API keys** - Use environment variables
- **Support multiple auth methods** - Bearer tokens, API keys, OAuth
- **Document required permissions** - What access levels are needed
- **Handle credential errors gracefully** - Clear error messages

### 2. Error Handling

```javascript
// Good error handling
try {
  const result = await mcpTool(params);
  return result;
} catch (error) {
  if (error.code === 401) {
    return { error: "Authentication failed. Check API key." };
  }
  if (error.code === 404) {
    return { error: "Resource not found. Verify ID." };
  }
  return { error: `Unexpected error: ${error.message}` };
}
```

### 3. Rate Limiting

- Implement backoff strategies
- Document rate limits in POWER.md
- Provide guidance on batch operations

### 4. Documentation Quality

**Essential Documentation:**
- Clear tool descriptions
- Parameter explanations with examples
- Common use cases
- Troubleshooting section
- Configuration examples

### 5. Tool Design Principles

- **Single Responsibility** - Each tool does one thing well
- **Consistent Naming** - Use verb_noun pattern (get_user, create_item)
- **Predictable Outputs** - Consistent response structures
- **Idempotency** - Safe to retry operations

### 6. Testing Considerations

- Test with mock data first
- Verify error scenarios
- Check rate limit handling
- Validate authentication flows

### 7. User Experience

- Provide sensible defaults
- Make common operations simple
- Support both simple and advanced use cases
- Include examples in documentation

## MCP Configuration Locations

### User Level (Global)
```
~/.kiro/settings/mcp.json
```

### Workspace Level
```
.kiro/settings/mcp.json
```

**Precedence:** Workspace config overrides user config

## Example: Postman Power Structure

```
postman-power/
├── POWER.md
│   ├── Overview
│   ├── Available Tools (40 in minimal mode)
│   ├── Usage Examples
│   ├── Workflows
│   └── Configuration
├── steering/
│   └── steering.md
└── MCP Server: postman
    ├── URL: https://mcp.postman.com/minimal
    └── Auth: Bearer ${POSTMAN_API_KEY}
```

## Best Practices Summary

### For Power Users (LLM Agents)

1. **Always activate first** - Get tool schemas before using
2. **Check keywords** - Match user intent to power capabilities
3. **Read steering files** - Follow guided workflows
4. **Handle errors** - Provide helpful feedback on failures
5. **Update configurations** - Keep project files current

### For Power Developers

1. **Start with POWER.md** - Documentation first
2. **Design clear tool interfaces** - Simple, consistent APIs
3. **Handle authentication properly** - Environment variables
4. **Provide examples** - Show common use cases
5. **Test thoroughly** - Cover error scenarios
6. **Document limitations** - Be clear about what doesn't work

## Troubleshooting Common Issues

### Power Not Found
- Check power is installed: `kiroPowers action="list"`
- Install via: `kiroPowers action="configure"`

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

**Document Version:** 1.0  
**Last Updated:** December 23, 2025  
**Keywords:** kiro, powers, mcp, model-context-protocol, tools, automation