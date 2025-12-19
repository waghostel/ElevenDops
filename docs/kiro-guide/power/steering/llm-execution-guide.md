# LLM Execution Guide for Kiro Powers

This guide explains how AI agents (LLMs) should discover, activate, and execute Kiro Powers. Use this as a reference when implementing power support in your agent or IDE.

---

## Power Lifecycle Overview

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

---

## Step 1: Discovery (list action)

**Purpose**: See all available powers and their capabilities

**When to use**:
- Starting a new task to see available capabilities
- Finding the right power for a specific need
- Checking if a power is installed

**Returns**:
```json
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

---

## Step 2: Keyword-Based Activation

Powers define keywords that trigger proactive activation. When user message contains matching keywords, the LLM should activate the power.

**Example**: A power with keywords `["weather", "forecast", "temperature"]` should activate when user asks "What's the weather in Tokyo?"

**Keyword Matching Logic**:
```python
def should_activate_power(user_message: str, power_keywords: list) -> bool:
    """Check if user message matches power keywords."""
    message_lower = user_message.lower()
    return any(keyword.lower() in message_lower for keyword in power_keywords)
```

**CRITICAL**: When you see words in the user's message that match a power's keywords, **immediately and proactively activate that power**. Don't wait for explicit requests.

---

## Step 3: Activation (activate action)

**Purpose**: Get full documentation and tool schemas for a power

**Parameters**:
- `powerName` (required): Name of the power to activate

**Returns**:
```json
{
  "powerName": "power-name",
  "displayName": "Power Display Name",
  "keywords": ["keyword1", "keyword2"],
  "description": "Full description",
  "overview": "Complete POWER.md content",
  "powerMdFound": true,
  "toolsByServer": {
    "server-name": [
      {
        "name": "tool_name",
        "description": "What the tool does",
        "inputSchema": {
          "type": "object",
          "properties": {
            "param1": { "type": "string", "description": "..." }
          },
          "required": ["param1"]
        }
      }
    ]
  },
  "steeringFiles": ["getting-started.md", "advanced-usage.md"]
}
```

**CRITICAL**: Always activate before using a power's tools!

---

## Step 4: Execution (use action)

**Purpose**: Run a specific tool from an MCP server

**Parameters**:
- `powerName` (required): The power containing the tool
- `serverName` (required): MCP server name (from `toolsByServer` keys)
- `toolName` (required): Tool to execute (from `toolsByServer[serverName]`)
- `arguments` (required): Tool parameters matching `inputSchema`

**Returns**: Tool-specific execution result

**Example Flow**:
```
1. activate("weather-power")
   → toolsByServer = { "weather-api": [{ name: "get_forecast", ... }] }

2. use("weather-power", "weather-api", "get_forecast", { "location": "Tokyo" })
   → { "forecast": "Sunny, 25°C", ... }
```

---

## Step 5: Guidance (readSteering action)

**Purpose**: Load detailed instructions for specific workflows

**Parameters**:
- `powerName` (required): Name of the power
- `steeringFile` (required): File name from `steeringFiles` array (include `.md`)

**Returns**: Markdown content with step-by-step guidance

**When to use**:
- Learning how to use a power effectively
- Following complex multi-step workflows
- Troubleshooting issues

---

## Complete Usage Example

### Scenario: Using a Weather Power

```
User: "What's the weather forecast for Seattle?"

LLM Internal Process:
1. Recognize "weather" and "forecast" match power keywords
2. List powers to confirm weather-power is installed
3. Activate weather-power to get tool schemas
4. Use get_forecast tool with location="Seattle"
5. Return formatted result to user
```

**Step-by-Step Execution**:

```
Step 1: list
→ Found: weather-power (keywords: weather, forecast, temperature)

Step 2: activate(powerName="weather-power")
→ toolsByServer: {
    "weather-api": [
      { name: "get_forecast", inputSchema: { location: string, units?: string } },
      { name: "get_current", inputSchema: { location: string } }
    ]
  }
→ steeringFiles: ["getting-started.md"]

Step 3: use(
    powerName="weather-power",
    serverName="weather-api",
    toolName="get_forecast",
    arguments={ "location": "Seattle", "units": "imperial" }
  )
→ { "location": "Seattle", "forecast": "Partly cloudy, 58°F", ... }
```

---

## Three-Level Context Loading

Powers use progressive disclosure to minimize context usage:

```
Level 1: Metadata (Always loaded)
├── name + description (~100 tokens)
└── Used for: Skill selection

Level 2: POWER.md Body (On activation)
├── Instructions + workflows (~500-2000 tokens)
└── Used for: Task execution

Level 3: Steering Files (On demand)
├── Detailed workflow guides
└── Used for: Specific operations
```

---

## Implementation for IDE/Agent Developers

### Adding Power Support

#### Step 1: Power Installation

Copy power folders to a known location:
```
~/.kiro/powers/
├── weather-power/
├── pdf-processor/
└── data-analyzer/
```

#### Step 2: Generate Power Index

Parse all POWER.md files and extract metadata:

```python
import yaml
from pathlib import Path

def index_powers(powers_dir):
    powers = []
    for power_path in Path(powers_dir).iterdir():
        power_md = power_path / "POWER.md"
        if power_md.exists():
            content = power_md.read_text()
            frontmatter = extract_frontmatter(content)
            powers.append({
                "name": frontmatter["name"],
                "description": frontmatter["description"],
                "keywords": frontmatter.get("keywords", []),
                "location": str(power_md.absolute())
            })
    return powers
```

#### Step 3: Include in System Prompt

Format powers for agent context:

```python
def format_powers_prompt(powers):
    prompt = "**Currently Installed Powers:**\n\n"
    for power in powers:
        keywords_str = ", ".join(power.get('keywords', []))
        prompt += f"• **{power['name']}**\n"
        prompt += f"  {power['description']}\n"
        prompt += f"  Keywords: {keywords_str}\n\n"
    return prompt
```

#### Step 4: Handle Power Activation

When agent requests power content:

```python
def load_power(power_path):
    """Load full POWER.md content when agent activates power."""
    return Path(power_path).read_text()

def load_steering(power_path, steering_file):
    """Load steering file when agent requests it."""
    power_dir = Path(power_path).parent
    return (power_dir / "steering" / steering_file).read_text()
```

---

## Best Practices for LLM Execution

### Do's ✅

1. **Always activate before use** - Never guess tool names or parameters
2. **Match keywords proactively** - Activate powers when keywords match
3. **Read steering files** - Use them for complex workflows
4. **Follow POWER.md instructions** - They contain domain-specific guidance
5. **Handle errors gracefully** - Check for common issues in troubleshooting sections

### Don'ts ❌

1. **Don't skip activation** - You'll fail without proper tool schemas
2. **Don't guess server names** - Get them from `toolsByServer` keys
3. **Don't ignore keywords** - They're designed to trigger activation
4. **Don't hardcode parameters** - Always check `inputSchema`

---

## Troubleshooting

### Power Not Found

1. Verify power is installed (use `list` action)
2. Check power name spelling (case-sensitive)
3. Ensure power directory structure is correct

### Tool Execution Fails

1. Always `activate` before `use`
2. Verify `serverName` matches `toolsByServer` keys exactly
3. Check `arguments` match the tool's `inputSchema`
4. Verify MCP server is running and configured

### Keywords Not Triggering Activation

1. Check keywords are defined in power metadata
2. Verify keywords are specific enough
3. Test with exact keyword matches first
