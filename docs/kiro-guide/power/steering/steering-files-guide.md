# Kiro Steering Files Guide

This guide explains how to create and use Kiro steering documents for LLM-assisted development. Steering files provide contextual guidance to LLMs during code generation.

---

## What Are Steering Documents?

Steering documents are markdown files that provide contextual guidance to LLMs. They act as "always-on" or "conditional" instructions that help the AI understand project conventions, architecture decisions, and coding standards.

**Location**: `.kiro/steering/*.md`

---

## Document Structure

### Front Matter (Required)

Every steering document starts with YAML front matter that controls when the document is included:

```yaml
---
inclusion: always | fileMatch | manual
fileMatchPattern: "pattern/**/*.ext"  # Only for fileMatch
---
```

### Inclusion Types

| Type | Description | Use Case |
|------|-------------|----------|
| `always` | Included in every LLM interaction | Project overview, coding standards |
| `fileMatch` | Included when working on matching files | Backend-specific, frontend-specific rules |
| `manual` | Only when explicitly referenced by user | Specialized workflows, optional guides |

---

## Step-by-Step Creation Process

### Step 1: Identify the Need

Determine what guidance the LLM needs:
- **Global rules**: Apply to all code (use `inclusion: always`)
- **Context-specific**: Apply to certain file types (use `inclusion: fileMatch`)
- **On-demand**: Specialized guidance (use `inclusion: manual`)

### Step 2: Create the File

Create a new `.md` file in `.kiro/steering/`:

```bash
# Example: Create a new steering file
touch .kiro/steering/my-guidelines.md
```

### Step 3: Add Front Matter

Choose the appropriate inclusion type:

```yaml
# For always-included documents
---
inclusion: always
---

# For file-pattern matching
---
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"
---

# For manual inclusion
---
inclusion: manual
---
```

### Step 4: Write Content

Structure your content with clear sections:

```markdown
---
inclusion: always
---

# Document Title

## Section 1: Overview
Brief description of what this document covers.

## Section 2: Guidelines
- Guideline 1
- Guideline 2

## Section 3: Code Examples
```python
# Example code here
```

## Reference Documents
- **Related Doc**: #[[file:path/to/related.md]]
```

---

## File Reference Syntax

Link to other project files using this syntax:

```markdown
#[[file:relative/path/to/file.md]]
```

**Examples**:
```markdown
- **User Requirements**: #[[file:user-need/user-need-phase1.md]]
- **API Docs**: #[[file:docs/elevenlabs-api/index.md]]
```

This tells the LLM to consider the referenced file's content when generating code.

---

## Common Patterns

### Pattern 1: Project Overview (Always Included)

```markdown
---
inclusion: always
---

# Project Overview

## Purpose
[What the project does]

## Technology Stack
- Frontend: [tech]
- Backend: [tech]
- Database: [tech]

## Architecture Principles
1. [Principle 1]
2. [Principle 2]

## Key Reference Documents
- **Requirements**: #[[file:docs/requirements.md]]
```

### Pattern 2: Coding Standards (Always Included)

```markdown
---
inclusion: always
---

# Coding Standards

## Project Structure
```
src/
  components/
  services/
  utils/
```

## Naming Conventions
- Files: kebab-case
- Classes: PascalCase
- Functions: camelCase

## Testing Requirements
- Use [framework] for testing
- Test files: `*.test.ts`
```

### Pattern 3: Backend-Specific Rules (File Match)

```markdown
---
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"
---

# Backend Development Guidelines

## API Design
- RESTful conventions
- Consistent error handling

## Service Layer
[Service-specific guidance]
```

### Pattern 4: Frontend-Specific Rules (File Match)

```markdown
---
inclusion: fileMatch
fileMatchPattern: "frontend/**/*.tsx"
---

# Frontend Development Guidelines

## Component Structure
[Component patterns]

## State Management
[State management rules]
```

---

## How Steering Documents Are Processed

### Processing Order

1. **Discovery**: LLM scans `.kiro/steering/` directory
2. **Front Matter Parsing**: Reads YAML to determine inclusion rules
3. **Pattern Matching**: For `fileMatch`, checks current file against pattern
4. **Content Injection**: Matching documents are added to LLM context
5. **Reference Resolution**: `#[[file:...]]` references are expanded

### Context Priority

When multiple steering documents apply:
- All matching documents are included
- More specific patterns don't override general ones
- Documents are additive, not exclusive

---

## File Match Pattern Examples

| Pattern | Matches |
|---------|---------|
| `**/*.py` | All Python files |
| `backend/**/*.py` | Python files in backend/ |
| `**/test_*.py` | Test files anywhere |
| `src/components/**/*.tsx` | React components |
| `**/*service*` | Files with "service" in name |

---

## Best Practices

### Do's ✅

1. **Keep documents focused** - One topic per file
2. **Use clear headings** - Easy to scan and reference
3. **Include code examples** - Show, don't just tell
4. **Reference related docs** - Use `#[[file:...]]` syntax
5. **Update regularly** - Keep in sync with project evolution

### Don'ts ❌

1. **Don't duplicate content** - Reference instead of copy
2. **Don't be too verbose** - LLMs have context limits
3. **Don't include secrets** - No API keys or credentials
4. **Don't use absolute paths** - Always use relative paths
5. **Don't over-constrain** - Leave room for LLM judgment

---

## Troubleshooting

### Document Not Being Applied

1. Check front matter syntax (must be valid YAML)
2. Verify file is in `.kiro/steering/` directory
3. For `fileMatch`, test pattern against current file path
4. Ensure no syntax errors in markdown

### File References Not Working

1. Use relative paths from project root
2. Check file exists at specified path
3. Verify syntax: `#[[file:path]]` (no spaces)

---

## Adapting for Other LLM Tools

If using a different IDE or LLM tool, you can replicate this pattern:

### For Cursor/Continue/Other AI IDEs

1. Create a similar directory structure (e.g., `.ai/context/`)
2. Use the tool's native context inclusion mechanism
3. Adapt front matter to tool's format if needed

### For Direct LLM API Usage

1. Read steering files programmatically
2. Parse front matter to determine inclusion
3. Prepend matching content to your prompts
4. Resolve file references before sending

### Example: Manual Context Injection

```python
import os
import yaml
import re
from pathlib import Path

def load_steering_docs(current_file: str = None) -> str:
    """Load applicable steering documents."""
    steering_dir = Path(".kiro/steering")
    context = []
    
    for doc_path in steering_dir.glob("*.md"):
        content = doc_path.read_text()
        
        # Parse front matter
        if content.startswith("---"):
            _, front_matter, body = content.split("---", 2)
            config = yaml.safe_load(front_matter)
            
            inclusion = config.get("inclusion", "always")
            
            if inclusion == "always":
                context.append(body)
            elif inclusion == "fileMatch" and current_file:
                pattern = config.get("fileMatchPattern", "")
                if matches_pattern(current_file, pattern):
                    context.append(body)
    
    return "\n\n".join(context)
```

---

## Summary

Steering documents provide a structured way to give LLMs project-specific context:

1. **Location**: `.kiro/steering/*.md`
2. **Inclusion types**: `always`, `fileMatch`, `manual`
3. **File references**: `#[[file:path/to/file.md]]`
4. **Best practice**: Keep focused, use examples, reference related docs
