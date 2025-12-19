# Skill Examples

Real-world skill examples demonstrating different patterns and structures.

## Table of Contents

1. [Minimal Skill](#minimal-skill)
2. [Script-Heavy Skill](#script-heavy-skill)
3. [Reference-Heavy Skill](#reference-heavy-skill)
4. [Multi-Framework Skill](#multi-framework-skill)
5. [Guidelines Skill](#guidelines-skill)

---

## Minimal Skill

A simple skill with just SKILL.md.

### Structure
```
commit-helper/
└── SKILL.md
```

### SKILL.md
```yaml
---
name: commit-helper
description: Generate conventional commit messages. Use when writing git commits to ensure consistent, descriptive messages following the conventional commits specification.
---

# Commit Message Helper

Generate commit messages following conventional commits format.

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Types

| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation |
| style | Formatting |
| refactor | Code restructuring |
| test | Adding tests |
| chore | Maintenance |

## Examples

**Feature:**
```
feat(auth): add JWT token refresh

Implement automatic token refresh when access token expires.
Tokens refresh 5 minutes before expiration.

Closes #123
```

**Bug fix:**
```
fix(api): handle null response from external service

Add null check before processing API response.
Previously caused TypeError on empty responses.
```

**Documentation:**
```
docs(readme): update installation instructions

Add Docker setup steps and environment variables.
```
```

---

## Script-Heavy Skill

A skill with multiple executable scripts.

### Structure
```
pdf-processor/
├── SKILL.md
├── scripts/
│   ├── extract_text.py
│   ├── merge_pdfs.py
│   ├── fill_form.py
│   └── rotate_pages.py
└── references/
    └── forms.md
```

### SKILL.md
```yaml
---
name: pdf-processor
description: PDF manipulation toolkit for text extraction, merging, form filling, and page rotation. Use when working with .pdf files for any processing, analysis, or modification task.
---

# PDF Processor

Process PDF files using bundled Python scripts.

## Quick Reference

| Task | Script | Usage |
|------|--------|-------|
| Extract text | extract_text.py | `python scripts/extract_text.py input.pdf` |
| Merge PDFs | merge_pdfs.py | `python scripts/merge_pdfs.py file1.pdf file2.pdf -o merged.pdf` |
| Fill form | fill_form.py | `python scripts/fill_form.py form.pdf data.json -o filled.pdf` |
| Rotate pages | rotate_pages.py | `python scripts/rotate_pages.py input.pdf 90 -o rotated.pdf` |

## Text Extraction

```bash
python scripts/extract_text.py document.pdf
python scripts/extract_text.py document.pdf --output text.txt
python scripts/extract_text.py document.pdf --pages 1-5
```

## Merging PDFs

```bash
python scripts/merge_pdfs.py file1.pdf file2.pdf file3.pdf -o combined.pdf
```

## Form Filling

For form filling, see [references/forms.md](references/forms.md) for:
- Analyzing form fields
- Creating field mappings
- Handling different field types

Basic usage:
```bash
python scripts/fill_form.py form.pdf data.json -o filled.pdf
```

## Page Rotation

```bash
# Rotate all pages 90 degrees clockwise
python scripts/rotate_pages.py input.pdf 90 -o rotated.pdf

# Rotate specific pages
python scripts/rotate_pages.py input.pdf 90 --pages 1,3,5 -o rotated.pdf
```

## Requirements

- Python 3.9+
- pypdf: `pip install pypdf`
- pdfplumber: `pip install pdfplumber`
```

---

## Reference-Heavy Skill

A skill with extensive documentation.

### Structure
```
bigquery-analyst/
├── SKILL.md
└── references/
    ├── schemas/
    │   ├── users.md
    │   ├── orders.md
    │   └── products.md
    ├── patterns.md
    └── optimization.md
```

### SKILL.md
```yaml
---
name: bigquery-analyst
description: Query BigQuery data warehouse with knowledge of table schemas and query patterns. Use when analyzing data, generating reports, or answering questions about users, orders, or products.
---

# BigQuery Analyst

Query the data warehouse with schema knowledge and optimized patterns.

## Available Tables

| Table | Reference | Description |
|-------|-----------|-------------|
| users | [schemas/users.md](references/schemas/users.md) | User accounts and profiles |
| orders | [schemas/orders.md](references/schemas/orders.md) | Purchase transactions |
| products | [schemas/products.md](references/schemas/products.md) | Product catalog |

## Query Workflow

1. Identify relevant tables from user question
2. Load schema reference for those tables
3. Construct query using schema knowledge
4. Apply optimization patterns if needed

## Common Queries

### User Metrics
```sql
SELECT 
  DATE(created_at) as date,
  COUNT(*) as new_users
FROM users
WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY date
ORDER BY date
```

### Order Analysis
```sql
SELECT 
  u.email,
  COUNT(o.id) as order_count,
  SUM(o.total) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.email
ORDER BY total_spent DESC
LIMIT 10
```

## Advanced Topics

- **Query patterns**: See [references/patterns.md](references/patterns.md)
- **Performance optimization**: See [references/optimization.md](references/optimization.md)
```

---

## Multi-Framework Skill

A skill supporting multiple frameworks/platforms.

### Structure
```
cloud-deploy/
├── SKILL.md
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

### SKILL.md
```yaml
---
name: cloud-deploy
description: Deploy applications to cloud platforms (AWS, GCP, Azure). Use when deploying containers, serverless functions, or infrastructure to any major cloud provider.
---

# Cloud Deployment

Deploy applications to AWS, GCP, or Azure.

## Provider Selection

Identify target provider, then load the relevant reference:

| Provider | Reference | Key Services |
|----------|-----------|--------------|
| AWS | [references/aws.md](references/aws.md) | ECS, Lambda, CloudFormation |
| GCP | [references/gcp.md](references/gcp.md) | Cloud Run, Cloud Functions, Deployment Manager |
| Azure | [references/azure.md](references/azure.md) | Container Apps, Functions, ARM |

## General Workflow

1. **Containerize** - Create Dockerfile
2. **Configure** - Set environment variables
3. **Deploy** - Use provider-specific commands
4. **Verify** - Check deployment status

## Quick Deploy Examples

### AWS (ECS)
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
docker build -t $ECR_URL/app:latest .
docker push $ECR_URL/app:latest
aws ecs update-service --cluster prod --service app --force-new-deployment
```

### GCP (Cloud Run)
```bash
gcloud builds submit --tag gcr.io/$PROJECT/app
gcloud run deploy app --image gcr.io/$PROJECT/app --platform managed
```

### Azure (Container Apps)
```bash
az acr build --registry $ACR --image app:latest .
az containerapp update --name app --resource-group rg --image $ACR.azurecr.io/app:latest
```

## Provider-Specific Details

Load the appropriate reference for detailed instructions:
- Infrastructure as Code templates
- Service configuration options
- Networking and security setup
- Monitoring and logging
```

---

## Guidelines Skill

A skill for enforcing standards.

### Structure
```
brand-guidelines/
├── SKILL.md
└── assets/
    ├── logo-primary.svg
    ├── logo-white.svg
    └── color-palette.json
```

### SKILL.md
```yaml
---
name: brand-guidelines
description: Enforce brand consistency in documents, presentations, and designs. Use when creating any branded content to ensure correct colors, typography, and logo usage.
---

# Brand Guidelines

Maintain brand consistency across all outputs.

## Colors

### Primary Palette
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Brand Blue | #1a73e8 | 26, 115, 232 | Primary actions, headers |
| Brand Green | #34a853 | 52, 168, 83 | Success states |
| Brand Red | #ea4335 | 234, 67, 53 | Errors, alerts |

### Neutral Palette
| Name | Hex | Usage |
|------|-----|-------|
| Dark Gray | #202124 | Body text |
| Medium Gray | #5f6368 | Secondary text |
| Light Gray | #f1f3f4 | Backgrounds |

## Typography

### Fonts
- **Headings**: Roboto Bold
- **Body**: Open Sans Regular
- **Code**: Roboto Mono

### Sizes
| Element | Size | Weight |
|---------|------|--------|
| H1 | 32px | Bold |
| H2 | 24px | Bold |
| H3 | 18px | Semi-bold |
| Body | 14px | Regular |
| Caption | 12px | Regular |

## Logo Usage

### Files
- Primary: `assets/logo-primary.svg`
- On dark backgrounds: `assets/logo-white.svg`

### Rules
- Minimum size: 24px height
- Clear space: 1x logo height on all sides
- Never stretch, rotate, or recolor
- Never place on busy backgrounds

## Application Examples

### Document Header
```
[Logo - left aligned, 32px height]
[Title - Roboto Bold, 24px, Brand Blue]
[Subtitle - Open Sans, 14px, Medium Gray]
```

### Presentation Slide
```
Background: White or Light Gray
Title: Roboto Bold, 32px, Dark Gray
Body: Open Sans, 18px, Dark Gray
Accent: Brand Blue for highlights
```
```

---

## Key Takeaways

1. **Match structure to purpose** - Scripts for automation, references for knowledge, assets for output
2. **Keep SKILL.md lean** - Core workflow only, details in references
3. **Write actionable descriptions** - Include triggers and use cases
4. **Provide quick references** - Tables and examples for common tasks
5. **Link to resources** - Clear paths to bundled files
