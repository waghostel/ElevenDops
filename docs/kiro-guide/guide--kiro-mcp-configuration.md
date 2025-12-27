# Kiro MCP Configuration Guide

This guide explains how to configure and use Model Context Protocol (MCP) servers in Kiro. It's designed for team members using different IDEs or LLM tools who need to understand or replicate this pattern.

## What is MCP?

Model Context Protocol (MCP) is a standard for connecting LLMs to external tools and data sources. MCP servers provide:
- Additional tools the LLM can invoke
- Access to external APIs and services
- Custom capabilities beyond built-in features

**Configuration Location**: `.kiro/settings/mcp.json` (workspace) or `~/.kiro/settings/mcp.json` (user-level)

## Configuration Structure

### Basic Format

```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["package-name@latest"],
      "env": {
        "ENV_VAR": "value"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `command` | string | Executable to run (e.g., `uvx`, `npx`, `node`) |
| `args` | string[] | Command-line arguments |
| `env` | object | Environment variables for the server |
| `disabled` | boolean | Enable/disable the server |
| `autoApprove` | string[] | Tool names to auto-approve without confirmation |

## Configuration Precedence

MCP configs are merged with the following priority (later overrides earlier):

```
User Config (~/.kiro/settings/mcp.json)
    ↓ overridden by
Workspace Config (.kiro/settings/mcp.json)
    ↓ overridden by
Additional Workspace Folders (in multi-root)
```

## Step-by-Step Configuration

### Step 1: Choose Configuration Level

**Workspace-level** (recommended for project-specific servers):
```
.kiro/settings/mcp.json
```

**User-level** (for personal/global servers):
```
~/.kiro/settings/mcp.json
```

### Step 2: Create Configuration File

**For workspace-level**:
```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Step 3: Install Prerequisites

Most MCP servers use `uvx` (from the `uv` Python package manager):

**Installation options**:
```bash
# Using pip
pip install uv

# Using Homebrew (macOS)
brew install uv

# Using pipx
pipx install uv
```

For detailed installation: https://docs.astral.sh/uv/getting-started/installation/

**Note**: Once `uv` is installed, `uvx` will automatically download and run MCP servers—no server-specific installation required.

### Step 4: Verify Configuration

1. Open Kiro
2. Check MCP Server view in the Kiro feature panel
3. Servers reconnect automatically on config changes
4. Or use Command Palette → search "MCP" for relevant commands

## Common MCP Server Examples

### AWS Documentation Server

```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Fetch Server (HTTP Requests)

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch@latest"],
      "disabled": false,
      "autoApprove": ["fetch_html", "fetch_json"]
    }
  }
}
```

### Filesystem Server

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Custom Node.js Server

```json
{
  "mcpServers": {
    "custom-server": {
      "command": "node",
      "args": ["./scripts/my-mcp-server.js"],
      "env": {
        "API_KEY": "${env:MY_API_KEY}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Using MCP Tools in Kiro

### Discovery

1. Use Kiro Powers tool with `action="list"` to see installed powers
2. Use `action="activate"` to discover available tools from a power
3. Tools are grouped by MCP server in the response

### Execution Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  User Request   │────▶│  Kiro identifies │────▶│  MCP Server     │
│  (uses tool)    │     │  relevant tool   │     │  executes tool  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                        ┌──────────────────┐             │
                        │  Result returned │◀────────────┘
                        │  to conversation │
                        └──────────────────┘
```

### Auto-Approval

For frequently used tools, add them to `autoApprove` to skip confirmation:

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch@latest"],
      "autoApprove": ["fetch_html", "fetch_markdown", "fetch_json"]
    }
  }
}
```

## Creating Custom MCP Servers

### Basic Server Structure (Node.js)

```javascript
// my-mcp-server.js
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "my-custom-server",
  version: "1.0.0"
}, {
  capabilities: {
    tools: {}
  }
});

// Define tools
server.setRequestHandler("tools/list", async () => ({
  tools: [{
    name: "my_tool",
    description: "Does something useful",
    inputSchema: {
      type: "object",
      properties: {
        input: { type: "string", description: "Input value" }
      },
      required: ["input"]
    }
  }]
}));

// Handle tool calls
server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "my_tool") {
    const input = request.params.arguments.input;
    return {
      content: [{ type: "text", text: `Processed: ${input}` }]
    };
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Basic Server Structure (Python)

```python
# my_mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("my-custom-server")

@server.list_tools()
async def list_tools():
    return [{
        "name": "my_tool",
        "description": "Does something useful",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input value"}
            },
            "required": ["input"]
        }
    }]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "my_tool":
        return f"Processed: {arguments['input']}"

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Adapting for Other IDEs

### For VS Code with Other Extensions

Many AI extensions support MCP or similar protocols:

1. Check extension documentation for tool configuration
2. Adapt the JSON format to the extension's requirements
3. Server commands remain the same

### For Direct LLM API Usage

Implement MCP client programmatically:

```python
import subprocess
import json

class MCPClient:
    def __init__(self, command: str, args: list, env: dict = None):
        self.process = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            env=env
        )
    
    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        self.process.stdin.flush()
        response = self.process.stdout.readline()
        return json.loads(response)
```

## Troubleshooting

### Server Not Starting

1. Verify `uvx` or `npx` is installed and in PATH
2. Check command and args are correct
3. Look for errors in Kiro output panel
4. Test command manually in terminal:
   ```bash
   uvx package-name@latest --help
   ```

### Tools Not Appearing

1. Ensure `disabled: false` in config
2. Check server is running in MCP Server view
3. Verify tool names match exactly
4. Restart Kiro or reconnect server

### Permission Errors

1. Check environment variables are set correctly
2. Verify API keys are valid
3. Ensure file paths are accessible
4. Check firewall/network settings for external APIs

### Configuration Not Loading

1. Verify JSON syntax is valid
2. Check file is in correct location
3. For user-level config, use absolute path `~/.kiro/settings/mcp.json`
4. Restart Kiro after changes

## Best Practices

### Do's ✅

1. **Use workspace config for project-specific servers** - Keeps config with the project
2. **Use user config for personal tools** - Available across all projects
3. **Set appropriate log levels** - Use `ERROR` for production, `DEBUG` for troubleshooting
4. **Use autoApprove sparingly** - Only for trusted, frequently-used tools
5. **Version pin servers** - Use `@latest` or specific versions

### Don'ts ❌

1. **Don't commit API keys** - Use environment variables
2. **Don't enable unused servers** - Set `disabled: true`
3. **Don't auto-approve destructive tools** - Always confirm file deletions, etc.
4. **Don't ignore errors** - Check logs when tools fail

## Environment Variables

### Using System Environment Variables

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uvx",
      "args": ["my-server@latest"],
      "env": {
        "API_KEY": "${env:MY_API_KEY}"
      }
    }
  }
}
```

### Setting Variables in Config

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uvx",
      "args": ["my-server@latest"],
      "env": {
        "API_KEY": "your-api-key-here",
        "LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

## Summary

MCP configuration in Kiro enables:

1. **Extended capabilities** through external tools
2. **Flexible configuration** at workspace or user level
3. **Custom integrations** via custom MCP servers
4. **Controlled access** through auto-approve settings

For questions or improvements to this guide, please update this document or discuss with the team.
