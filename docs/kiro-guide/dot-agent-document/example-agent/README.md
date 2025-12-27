# Example `.agent` Folder Structure

This folder demonstrates the recommended structure and content for the `.agent` directory system used by AI coding assistants.

---

## Folder Structure

```
example-agent/
├── workflows/                    # Standard operating procedures (SOPs)
│   ├── build.md                 # Production build workflow
│   ├── deploy.md                # Deployment workflow
│   ├── test.md                  # Test suite workflow (with turbo-all)
│   └── dev-setup.md             # Development environment setup
│
├── rules/                        # Project-wide coding constraints
│   ├── naming-conventions.md    # File and code naming rules
│   ├── api-design.md            # API design standards
│   └── code-quality.md          # Code quality requirements
│
└── instructions.md               # Global agent instructions
```

---

## File Purposes

### Workflows (`workflows/`)

Workflows define step-by-step procedures for common tasks. They are invoked via slash commands (e.g., `/build`, `/test`).

| File           | Slash Command | Purpose                            |
| :------------- | :------------ | :--------------------------------- |
| `build.md`     | `/build`      | Compile and bundle for production  |
| `deploy.md`    | `/deploy`     | Deploy to staging/production       |
| `test.md`      | `/test`       | Run the complete test suite        |
| `dev-setup.md` | `/dev-setup`  | Initialize development environment |

### Rules (`rules/`)

Rules define constraints and conventions the AI must follow when generating code.

| File                    | Purpose                                           |
| :---------------------- | :------------------------------------------------ |
| `naming-conventions.md` | File, directory, and code naming standards        |
| `api-design.md`         | REST API response format and standards            |
| `code-quality.md`       | Error handling, logging, and testing requirements |

### Instructions (`instructions.md`)

High-level guidance about the project, technology stack, and principles.

---

## Key Features Demonstrated

1. **YAML Front Matter** - Each workflow has a `description` field for AI discovery
2. **`// turbo` Annotation** - Auto-runs safe commands without user confirmation
3. **`// turbo-all` Annotation** - Auto-runs all commands in a workflow
4. **Tables and Examples** - Clear, structured documentation
5. **DO's and DON'Ts** - Explicit guidance on what to do and avoid

---

## How to Use This Example

1. Copy this `example-agent/` folder to your project root as `.agent/`
2. Customize the content for your specific project
3. Remove examples that don't apply
4. Add new workflows and rules as needed

---

## Related Documentation

- [Agent System Guide](../guide--agent-system.md)
- [Agent Workflows Guide](../guide--agent-workflows.md)
