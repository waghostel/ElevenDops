# Skill Design Patterns

Proven patterns for effective skill design.

## Table of Contents

1. [Structural Patterns](#structural-patterns)
2. [Workflow Patterns](#workflow-patterns)
3. [Output Patterns](#output-patterns)
4. [Progressive Disclosure Patterns](#progressive-disclosure-patterns)
5. [Freedom Level Patterns](#freedom-level-patterns)

---

## Structural Patterns

### Pattern 1: Workflow-Based

Best for sequential processes with clear steps.

```markdown
# Document Processor

## Overview
Process documents through validation, transformation, and export.

## Workflow Decision Tree
- Creating new? → Section "Creating"
- Editing existing? → Section "Editing"
- Analyzing? → Section "Analysis"

## Creating Documents
1. Initialize template
2. Add content
3. Export

## Editing Documents
1. Load document
2. Apply changes
3. Save
```

**Use when:** Clear step-by-step procedures exist.

### Pattern 2: Task-Based

Best for tool collections with independent operations.

```markdown
# PDF Toolkit

## Quick Start
[Minimal example]

## Extract Text
[Instructions + code]

## Merge Documents
[Instructions + code]

## Fill Forms
[Instructions + code]
```

**Use when:** Skill offers multiple independent capabilities.

### Pattern 3: Reference/Guidelines

Best for standards, specifications, or policies.

```markdown
# Brand Guidelines

## Overview
Maintain brand consistency across all outputs.

## Colors
- Primary: #1a73e8
- Secondary: #34a853

## Typography
- Headings: Roboto Bold
- Body: Open Sans

## Logo Usage
[Rules and examples]
```

**Use when:** Enforcing standards or specifications.

### Pattern 4: Capabilities-Based

Best for integrated systems with related features.

```markdown
# API Integration

## Core Capabilities

### 1. Authentication
[OAuth flow, token management]

### 2. Data Retrieval
[Query patterns, pagination]

### 3. Data Mutation
[Create, update, delete operations]

### 4. Error Handling
[Common errors, recovery strategies]
```

**Use when:** Features are interrelated and build on each other.

---

## Workflow Patterns

### Sequential Workflow

For multi-step processes:

```markdown
## PDF Form Filling Process

1. **Analyze form** - Run `scripts/analyze_form.py`
2. **Create mapping** - Edit `fields.json`
3. **Validate** - Run `scripts/validate_fields.py`
4. **Fill form** - Run `scripts/fill_form.py`
5. **Verify** - Run `scripts/verify_output.py`
```

### Conditional Workflow

For branching logic:

```markdown
## Document Processing

1. Determine document type:
   - **New document?** → Follow "Creation Workflow"
   - **Existing document?** → Follow "Editing Workflow"

### Creation Workflow
1. Select template
2. Add content
3. Export

### Editing Workflow
1. Load document
2. Identify changes
3. Apply modifications
4. Save
```

### Iterative Workflow

For refinement processes:

```markdown
## Code Review Process

1. **Initial analysis** - Identify issues
2. **Categorize** - Group by severity
3. **Address critical** - Fix blocking issues
4. **Address warnings** - Fix non-blocking issues
5. **Verify** - Run tests
6. **Repeat** if issues remain
```

---

## Output Patterns

### Template Pattern (Strict)

For consistent, required formats:

```markdown
## Report Structure

ALWAYS use this exact template:

# [Analysis Title]

## Executive Summary
[One-paragraph overview]

## Key Findings
- Finding 1 with data
- Finding 2 with data

## Recommendations
1. Actionable recommendation
2. Actionable recommendation
```

### Template Pattern (Flexible)

For adaptable formats:

```markdown
## Report Structure

Sensible default format (adapt as needed):

# [Title]

## Summary
[Overview - adjust length to content]

## Findings
[Organize by relevance]

## Next Steps
[Tailor to context]
```

### Examples Pattern

For quality-dependent outputs:

```markdown
## Commit Message Format

**Example 1:**
Input: Added user authentication with JWT
Output:
```
feat(auth): implement JWT authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed date display bug in reports
Output:
```
fix(reports): correct date formatting

Use UTC timestamps consistently
```
```

---

## Progressive Disclosure Patterns

### Pattern 1: High-Level Guide with References

Keep SKILL.md lean, link to details:

```markdown
# PDF Processing

## Quick Start
[Basic example]

## Advanced Features
- **Form filling**: See [forms.md](references/forms.md)
- **API reference**: See [reference.md](references/reference.md)
- **Examples**: See [examples.md](references/examples.md)
```

### Pattern 2: Domain-Specific Organization

Organize by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview + navigation)
└── references/
    ├── finance.md
    ├── sales.md
    └── marketing.md
```

SKILL.md:
```markdown
## Domain References

Load the relevant reference for your query:
- **Finance queries**: [references/finance.md](references/finance.md)
- **Sales queries**: [references/sales.md](references/sales.md)
- **Marketing queries**: [references/marketing.md](references/marketing.md)
```

### Pattern 3: Framework-Specific Organization

For multi-framework skills:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

SKILL.md:
```markdown
## Provider Selection

1. Identify target cloud provider
2. Load relevant reference:
   - AWS: [references/aws.md](references/aws.md)
   - GCP: [references/gcp.md](references/gcp.md)
   - Azure: [references/azure.md](references/azure.md)
```

### Pattern 4: Conditional Details

Show basic content, link to advanced:

```markdown
# Document Processing

## Basic Editing
Modify XML directly for simple changes.

## Advanced Features
- **Tracked changes**: See [redlining.md](references/redlining.md)
- **OOXML details**: See [ooxml.md](references/ooxml.md)
```

---

## Freedom Level Patterns

### High Freedom (Text Instructions)

For flexible, context-dependent tasks:

```markdown
## Writing Style

Adapt tone to audience:
- Technical users: Be precise, use jargon
- Business users: Focus on outcomes
- General users: Keep it simple

Consider the document purpose and adjust formality accordingly.
```

**Use when:** Multiple valid approaches, decisions depend on context.

### Medium Freedom (Pseudocode/Parameters)

For preferred patterns with variation:

```markdown
## Data Processing

```pseudocode
1. Load data from {source}
2. Validate against {schema}
3. Transform using {rules}
4. Output to {destination}
```

Parameters:
- source: file path or API endpoint
- schema: JSON schema or validation rules
- rules: transformation logic
- destination: output location
```

**Use when:** Preferred pattern exists, some variation acceptable.

### Low Freedom (Specific Scripts)

For fragile, error-prone operations:

```markdown
## PDF Form Filling

ALWAYS use the provided script:

```bash
python scripts/fill_form.py input.pdf data.json output.pdf
```

Do NOT attempt to fill forms manually or with alternative methods.
The script handles edge cases that are easy to miss.
```

**Use when:** Operations are fragile, consistency critical, specific sequence required.

---

## Anti-Patterns to Avoid

### ❌ Deeply Nested References

Bad:
```
SKILL.md → reference1.md → reference2.md → reference3.md
```

Good:
```
SKILL.md → reference1.md
         → reference2.md
         → reference3.md
```

### ❌ Duplicated Information

Bad: Same content in SKILL.md AND references/guide.md

Good: Core workflow in SKILL.md, details in references/

### ❌ Verbose Explanations

Bad: "In order to extract text from a PDF document, you will need to..."

Good: "Extract text: `page.extract_text()`"

### ❌ Unnecessary Files

Bad: README.md, CHANGELOG.md, INSTALLATION.md in skill folder

Good: Only SKILL.md + essential resources
