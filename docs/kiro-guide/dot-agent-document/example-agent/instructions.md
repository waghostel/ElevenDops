# Agent Instructions

This file provides high-level guidance for AI assistants working on this project.

---

## Project Overview

This is a **[Project Name]** - a web application for [purpose].

### Mission

[Brief description of what the project does and why it exists]

### Target Users

- [User type 1]
- [User type 2]

---

## Technology Stack

| Layer           | Technology                                 |
| :-------------- | :----------------------------------------- |
| Frontend        | React 19 + TypeScript + Vite               |
| Styling         | TailwindCSS 4                              |
| State           | Zustand (global) + TanStack Query (server) |
| Backend         | FastAPI + Python 3.11                      |
| Database        | PostgreSQL + Redis                         |
| Testing         | Jest + Pytest + Hypothesis                 |
| Package Manager | pnpm (frontend) + uv (backend)             |

---

## Core Principles

1. **User Experience First** - Prioritize usability and accessibility
2. **Type Safety** - Use TypeScript and Python type hints everywhere
3. **Test Everything** - Write tests before deployment
4. **Document Decisions** - Record architectural decisions
5. **Security by Default** - Never compromise on security

---

## What I Should Know

### DO's ✅

- Follow existing patterns in the codebase
- Ask for clarification when requirements are unclear
- Run tests before suggesting code is complete
- Check for existing utilities before writing new ones
- Use the project's established error handling patterns

### DON'Ts ❌

- Don't introduce new dependencies without discussion
- Don't skip tests for "simple" changes
- Don't hardcode values that should be configurable
- Don't ignore linting errors
- Don't make assumptions about business logic

---

## Key Directories

| Directory   | Purpose                   |
| :---------- | :------------------------ |
| `backend/`  | FastAPI backend code      |
| `frontend/` | React frontend code       |
| `tests/`    | Test suites               |
| `docs/`     | Documentation             |
| `.kiro/`    | Kiro configuration        |
| `.agent/`   | Agent workflows and rules |

---

## When in Doubt

1. **Check existing code** - Look for similar implementations
2. **Read the docs** - Check documentation in `/docs`
3. **Ask the user** - Don't guess on business requirements
4. **Start small** - Make minimal changes first, then iterate

---

## Sensitive Information

- Never include API keys or secrets in code
- Use environment variables for configuration
- Don't log sensitive user data
- Check `.env.example` for required variables
