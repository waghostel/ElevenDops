# Skill Format Specification

Complete reference for skill file formats and structure.

## Table of Contents

1. [Folder Structure](#folder-structure)
2. [SKILL.md Specification](#skillmd-specification)
3. [Scripts Directory](#scripts-directory)
4. [References Directory](#references-directory)
5. [Assets Directory](#assets-directory)
6. [Validation Rules](#validation-rules)

---

## Folder Structure

### Minimal Skill

```
my-skill/
└── SKILL.md
```

### Full Skill

```
my-skill/
├── SKILL.md                    # Required: Entry point
├── LICENSE.txt                 # Optional: License terms
├── scripts/                    # Optional: Executable code
│   ├── process_data.py
│   └── validate.sh
├── references/                 # Optional: Documentation
│   ├── api-docs.md
│   └── schemas.md
└── assets/                     # Optional: Output resources
    ├── template.pptx
    └── logo.png
```

---

## SKILL.md Specification

### YAML Frontmatter

```yaml
---
# REQUIRED FIELDS
name: skill-name              # Hyphen-case identifier
description: |                # What it does + when to use
  Multi-line description
  explaining the skill.

# OPTIONAL FIELDS
license: Apache 2.0           # License name or file reference
allowed-tools:                # Pre-approved tools (client-specific)
  - bash
  - python
metadata:                     # Custom key-value pairs
  version: "1.0"
  author: "Team Name"
---
```

### Field Requirements

#### name (required)
- Format: hyphen-case (lowercase letters, digits, hyphens)
- Must match containing folder name exactly
- Max length: 64 characters
- No leading/trailing hyphens or consecutive hyphens

Valid: `pdf-processor`, `my-skill-v2`, `data-analyzer`
Invalid: `PDF_Processor`, `-my-skill`, `my--skill`

#### description (required)
- Max length: 1024 characters
- No angle brackets (`<` or `>`)
- Should include:
  - What the skill does
  - When to use it (triggers)
  - Supported file types or scenarios

Example:
```yaml
description: |
  PDF manipulation toolkit for extracting text, creating documents,
  and handling forms. Use when working with .pdf files for:
  (1) Text extraction, (2) Form filling, (3) Document merging,
  (4) Table extraction, or any PDF processing task.
```

### Markdown Body

The body contains instructions loaded after skill activation.

#### Structure Guidelines

```markdown
# Skill Title

## Overview
[1-2 sentences explaining capability]

## Quick Start
[Minimal example to get started]

## Workflows
[Step-by-step procedures]

## Reference Files
[Links to bundled resources]
```

#### Best Practices

- Keep under 500 lines (split into references if longer)
- Use imperative/infinitive form ("Extract text" not "Extracting text")
- Include code examples for technical skills
- Reference bundled files with relative paths: `[API Docs](references/api.md)`

---

## Scripts Directory

Executable code for deterministic, repeatable tasks.

### When to Include Scripts

- Same code rewritten repeatedly
- Deterministic reliability needed
- Complex operations that benefit from testing

### Script Guidelines

```python
#!/usr/bin/env python3
"""
Script description and usage.

Usage:
    python script.py <input> [options]

Example:
    python script.py data.json --format csv
"""

import sys

def main():
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

### Execution Modes

1. **Direct execution**: Agent runs script without reading
2. **Read then execute**: Agent reads for understanding, then runs
3. **Patch and execute**: Agent modifies for environment, then runs

---

## References Directory

Documentation loaded into context on-demand.

### When to Include References

- Detailed API documentation
- Database schemas
- Domain-specific knowledge
- Comprehensive workflow guides
- Information too lengthy for SKILL.md

### Reference Guidelines

```markdown
# Reference Title

## Table of Contents
[Include for files >100 lines]

## Section 1
[Content]

## Section 2
[Content]
```

### Organization Patterns

**By domain:**
```
references/
├── finance.md
├── sales.md
└── marketing.md
```

**By framework:**
```
references/
├── aws.md
├── gcp.md
└── azure.md
```

**By complexity:**
```
references/
├── quickstart.md
├── advanced.md
└── troubleshooting.md
```

---

## Assets Directory

Files used in output, not loaded into context.

### When to Include Assets

- Templates (PPTX, DOCX, HTML)
- Images (logos, icons)
- Fonts
- Boilerplate code directories
- Sample data files

### Asset Types

| Type | Examples | Use Case |
|------|----------|----------|
| Templates | `.pptx`, `.docx` | Document generation |
| Images | `.png`, `.svg`, `.jpg` | Brand assets |
| Fonts | `.ttf`, `.woff2` | Typography |
| Code | directories | Project scaffolding |
| Data | `.json`, `.csv` | Sample/test data |

---

## Validation Rules

### Automatic Checks

The `quick_validate.py` script verifies:

1. **SKILL.md exists** in skill folder
2. **Valid YAML frontmatter** with `---` delimiters
3. **Required fields present**: `name`, `description`
4. **Name format**: hyphen-case, no invalid characters
5. **Name length**: ≤64 characters
6. **Description format**: no angle brackets
7. **Description length**: ≤1024 characters
8. **No unexpected frontmatter keys**

### Allowed Frontmatter Keys

```
name, description, license, allowed-tools, metadata
```

### Running Validation

```bash
python scripts/quick_validate.py <skill-folder>
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "No YAML frontmatter" | Missing `---` delimiters | Add frontmatter block |
| "Missing 'name'" | No name field | Add `name: skill-name` |
| "Should be hyphen-case" | Invalid characters | Use lowercase + hyphens |
| "Cannot contain angle brackets" | `<` or `>` in description | Remove or escape |
