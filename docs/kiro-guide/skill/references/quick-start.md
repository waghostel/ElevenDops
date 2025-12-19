# Quick Start: Creating a Skill

Minimal steps to create a working skill.

## 1. Initialize

```bash
python scripts/init_skill.py my-skill --path ./skills
```

This creates:
```
skills/my-skill/
├── SKILL.md          # Edit this
├── scripts/          # Add scripts here
├── references/       # Add docs here
└── assets/           # Add templates here
```

## 2. Edit SKILL.md

```yaml
---
name: my-skill
description: What it does. When to use it. File types or scenarios.
---

# My Skill

## Overview
[What this skill enables]

## Usage
[How to use it]

## Examples
[Concrete examples]
```

## 3. Add Resources (Optional)

**Scripts** - For repetitive code:
```python
# scripts/process.py
#!/usr/bin/env python3
def main():
    # Your code
    pass

if __name__ == "__main__":
    main()
```

**References** - For detailed docs:
```markdown
# references/api.md
Detailed API documentation...
```

**Assets** - For templates:
```
assets/template.pptx
assets/logo.png
```

## 4. Validate

```bash
python scripts/quick_validate.py skills/my-skill
```

## 5. Package

```bash
python scripts/package_skill.py skills/my-skill
```

Creates `my-skill.skill` (zip file).

## Checklist

- [ ] `name` matches folder name
- [ ] `description` includes triggers (when to use)
- [ ] SKILL.md under 500 lines
- [ ] Scripts tested and working
- [ ] No unnecessary files (README, CHANGELOG, etc.)

## Next Steps

- [skill-format.md](skill-format.md) - Complete format specification
- [design-patterns.md](design-patterns.md) - Proven patterns
- [examples.md](examples.md) - Real skill examples
