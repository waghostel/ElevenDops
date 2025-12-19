---
name: skill-creator
description: Guide for creating effective skills that extend AI agent capabilities. Use when users want to create a new skill, update an existing skill, or understand skill architecture. Skills are modular packages containing instructions, scripts, and resources that agents discover and load dynamically.
license: Complete terms in LICENSE.txt
---

# Skill Creator

Create skills that extend AI agent capabilities with specialized knowledge, workflows, and tools.

## What Are Skills?

Skills are self-contained folders that transform general-purpose AI agents into specialized assistants. They provide:
- Procedural workflows for specific domains
- Tool integrations for file formats or APIs
- Domain expertise (schemas, business logic, policies)
- Bundled resources (scripts, references, assets)

## Skill Structure

```
skill-name/
├── SKILL.md              # Required: Entry point with metadata + instructions
├── scripts/              # Optional: Executable code (Python/Bash)
├── references/           # Optional: Documentation loaded on-demand
└── assets/               # Optional: Files used in output (templates, images)
```

## SKILL.md Format

Every skill requires a `SKILL.md` file with YAML frontmatter and Markdown body:

```yaml
---
name: my-skill-name          # Required: hyphen-case, matches folder name
description: What it does... # Required: Triggers skill activation
license: Apache 2.0          # Optional
allowed-tools: [...]         # Optional: Pre-approved tools
metadata: {...}              # Optional: Custom key-value pairs
---

# Skill Title

[Instructions for using the skill]
```

### Writing Effective Descriptions

The `description` field is the primary trigger mechanism. Include:
- What the skill does
- When to use it (specific scenarios, file types, tasks)
- Example: "PDF manipulation toolkit for extracting text, creating documents, and handling forms. Use when working with .pdf files for text extraction, form filling, or document generation."

## Creation Process

### Step 1: Understand with Examples

Gather concrete usage examples:
- "What should this skill support?"
- "How would users invoke it?"
- "What triggers should activate it?"

### Step 2: Plan Resources

For each example, identify:
- Scripts needed for repetitive/deterministic tasks
- References for domain knowledge
- Assets for output templates

### Step 3: Initialize

```bash
python scripts/init_skill.py <skill-name> --path <output-directory>
```

### Step 4: Implement

1. Create bundled resources (scripts, references, assets)
2. Write SKILL.md with clear instructions
3. Test scripts by running them

See [references/skill-format.md](references/skill-format.md) for detailed format specifications.
See [references/design-patterns.md](references/design-patterns.md) for proven patterns.
See [references/llm-execution-guide.md](references/llm-execution-guide.md) for LLM integration.

### Step 5: Package

```bash
python scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

### Step 6: Iterate

Test on real tasks, identify struggles, update resources.

## Core Principles

### Concise is Key
Only add context the agent doesn't already have. Challenge each piece: "Does this justify its token cost?"

### Progressive Disclosure
1. Metadata (name + description) - Always in context (~100 words)
2. SKILL.md body - When skill triggers (<5k words)
3. Bundled resources - As needed (unlimited)

### Appropriate Freedom
- High freedom: Text instructions for flexible tasks
- Medium freedom: Pseudocode for preferred patterns
- Low freedom: Specific scripts for fragile operations

## Reference Files

- [references/quick-start.md](references/quick-start.md) - Minimal steps to create a skill
- [references/skill-format.md](references/skill-format.md) - Complete format specification
- [references/design-patterns.md](references/design-patterns.md) - Workflow and output patterns
- [references/llm-execution-guide.md](references/llm-execution-guide.md) - How LLMs discover and execute skills
- [references/examples.md](references/examples.md) - Real skill examples with different patterns
