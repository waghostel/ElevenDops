# Kiro Workflow Patterns Guide

This guide presents common development workflows that combine Kiro's features (steering, specs, hooks, context keys) for typical development scenarios. It's designed for team members to understand and replicate effective patterns.

## Overview

Kiro's features work together to create powerful workflows:

```
┌─────────────────────────────────────────────────────────────────┐
│                    KIRO FEATURE INTEGRATION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │   Steering   │────▶│    Specs     │────▶│    Hooks     │     │
│  │   (Rules)    │     │   (Plans)    │     │ (Automation) │     │
│  └──────────────┘     └──────────────┘     └──────────────┘     │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              ↓                                  │
│                    ┌──────────────────┐                         │
│                    │  Context Keys    │                         │
│                    │  (Information)   │                         │
│                    └──────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow 1: Feature Development

### Scenario
Building a new feature from scratch with proper planning and implementation.

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SETUP STEERING (if not exists)                              │
│     • Create project-overview.md                                │
│     • Create coding-standards.md                                │
├─────────────────────────────────────────────────────────────────┤
│  2. CREATE SPEC                                                 │
│     • requirements.md → approval                                │
│     • design.md → approval                                      │
│     • tasks.md → approval                                       │
├─────────────────────────────────────────────────────────────────┤
│  3. EXECUTE TASKS                                               │
│     • One task at a time                                        │
│     • Use context keys for reference                            │
│     • Hooks auto-run tests on save                              │
├─────────────────────────────────────────────────────────────────┤
│  4. REVIEW & COMPLETE                                           │
│     • Review #Git Diff                                          │
│     • Run final tests                                           │
│     • Update documentation                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Document Creation

**Step 1: Steering Setup**

Create `.kiro/steering/project-overview.md`:
```markdown
---
inclusion: always
---

# Project Overview

## Purpose
[What the project does]

## Technology Stack
- Backend: FastAPI
- Frontend: Streamlit
- Database: Firestore

## Key References
- **Requirements**: #[[file:user-need/user-need-phase1.md]]
- **API Docs**: #[[file:docs/api/index.md]]
```

**Step 2: Spec Creation**

Tell Kiro: "Create a spec for [feature name]"

Kiro will create:
- `.kiro/specs/feature-name/requirements.md`
- `.kiro/specs/feature-name/design.md`
- `.kiro/specs/feature-name/tasks.md`

**Step 3: Hook Setup (Optional)**

Create auto-test hook via Kiro Hook UI:
```yaml
name: "Auto Test on Save"
trigger:
  event: onFileSave
  filePattern: "backend/**/*.py"
action:
  type: executeCommand
  command: "pytest tests/ -v --tb=short"
```

### Execution Commands

```
# Start feature development
"Create a spec for audio upload feature"

# After approvals, execute tasks
"Execute task 1 from audio-upload spec"
"Continue with next task"

# Review before commit
"Review my #Git Diff for the audio feature"
```

---

## Workflow 2: Bug Fixing

### Scenario
Investigating and fixing a bug with proper context.

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  1. GATHER CONTEXT                                              │
│     • #Terminal - error output                                  │
│     • #Problems - diagnostics                                   │
│     • #File - relevant source files                             │
├─────────────────────────────────────────────────────────────────┤
│  2. ANALYZE                                                     │
│     • Identify root cause                                       │
│     • Check related code                                        │
│     • Review recent changes (#Git Diff)                         │
├─────────────────────────────────────────────────────────────────┤
│  3. FIX                                                         │
│     • Implement fix                                             │
│     • Run tests                                                 │
│     • Verify fix resolves issue                                 │
├─────────────────────────────────────────────────────────────────┤
│  4. PREVENT                                                     │
│     • Add test for the bug                                      │
│     • Update steering if pattern issue                          │
│     • Document if complex                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Execution Commands

```
# Gather context
"I'm seeing this error in #Terminal. The relevant code is in 
#File:backend/services/audio.py. What's causing it?"

# Analyze with more context
"Check #File:backend/services/elevenlabs_service.py for related issues.
Also show me the #Problems in the current file."

# Fix and verify
"Fix the issue and run the tests to verify"

# Prevent regression
"Add a test case for this bug in #File:tests/test_audio_service_props.py"
```

### Quick Bug Fix Template

For simple bugs, use this pattern:
```
Fix the #Problems in #File:path/to/file.py

Error from #Terminal:
[paste error]

Expected behavior: [describe]
```

---

## Workflow 3: Code Refactoring

### Scenario
Improving code structure without changing behavior.

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  1. ASSESS SCOPE                                                │
│     • Identify files to refactor                                │
│     • Check test coverage                                       │
│     • Review dependencies                                       │
├─────────────────────────────────────────────────────────────────┤
│  2. CREATE REFACTORING SPEC (for large refactors)               │
│     • Document current state                                    │
│     • Define target state                                       │
│     • Plan incremental steps                                    │
├─────────────────────────────────────────────────────────────────┤
│  3. EXECUTE INCREMENTALLY                                       │
│     • Small, testable changes                                   │
│     • Run tests after each change                               │
│     • Commit frequently                                         │
├─────────────────────────────────────────────────────────────────┤
│  4. VERIFY                                                      │
│     • All tests pass                                            │
│     • No behavior changes                                       │
│     • Code quality improved                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Document Creation

**For Large Refactors - Create Spec**

```
"Create a refactoring spec for #Folder:backend/services

Goals:
- Extract common patterns into base class
- Improve error handling consistency
- Add type hints throughout"
```

**For Small Refactors - Direct Execution**

```
"Refactor #File:backend/services/audio.py to:
- Extract the validation logic into a separate method
- Add proper type hints
- Follow patterns from #File:backend/services/elevenlabs_service.py"
```

### Steering for Refactoring

Create `.kiro/steering/refactoring-guidelines.md`:
```markdown
---
inclusion: manual
---

# Refactoring Guidelines

## Principles
1. No behavior changes during refactoring
2. Tests must pass before and after
3. Small, incremental commits

## Patterns to Apply
- Extract method for repeated code
- Use dependency injection
- Follow existing service patterns in #[[file:backend/services/elevenlabs_service.py]]

## Checklist
- [ ] Tests pass before starting
- [ ] Each change is independently testable
- [ ] No new features added
- [ ] Documentation updated if needed
```

---

## Workflow 4: Code Review Assistance

### Scenario
Getting AI assistance for reviewing code changes.

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  1. PREPARE REVIEW                                              │
│     • Stage changes                                             │
│     • Gather context                                            │
├─────────────────────────────────────────────────────────────────┤
│  2. REQUEST REVIEW                                              │
│     • Share #Git Diff                                           │
│     • Reference coding standards                                │
│     • Ask specific questions                                    │
├─────────────────────────────────────────────────────────────────┤
│  3. ADDRESS FEEDBACK                                            │
│     • Fix identified issues                                     │
│     • Re-review if needed                                       │
├─────────────────────────────────────────────────────────────────┤
│  4. FINALIZE                                                    │
│     • Ensure all feedback addressed                             │
│     • Run final tests                                           │
│     • Commit with good message                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Execution Commands

```
# Basic review
"Review my #Git Diff for security issues and code quality"

# Review against standards
"Review #Git Diff against our coding standards in 
#File:.kiro/steering/coding-standards.md"

# Specific review focus
"Review the API changes in #Git Diff:
- Are the endpoints RESTful?
- Is error handling consistent?
- Are there any breaking changes?"

# Review specific files
"Review #File:backend/api/audio.py for:
- Input validation
- Error handling
- Documentation"
```

### Hook for Review Reminder

```yaml
name: "Pre-Commit Review Checklist"
trigger:
  event: onManualTrigger
action:
  type: sendMessage
  message: |
    Please review the current changes:
    - [ ] Code follows project standards
    - [ ] Tests added/updated
    - [ ] No hardcoded secrets
    - [ ] Error handling is proper
    - [ ] Documentation updated if needed
```

---

## Workflow 5: Documentation Updates

### Scenario
Keeping documentation in sync with code changes.

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  1. IDENTIFY CHANGES                                            │
│     • What code changed?                                        │
│     • What docs are affected?                                   │
├─────────────────────────────────────────────────────────────────┤
│  2. UPDATE DOCUMENTATION                                        │
│     • API docs                                                  │
│     • README                                                    │
│     • Inline comments                                           │
├─────────────────────────────────────────────────────────────────┤
│  3. VERIFY CONSISTENCY                                          │
│     • Code matches docs                                         │
│     • Examples work                                             │
│     • Links are valid                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Hook for Documentation Sync

```yaml
name: "Doc Sync Reminder"
trigger:
  event: onFileSave
  filePattern: "backend/api/**/*.py"
action:
  type: sendMessage
  message: |
    API file was modified. Please verify:
    - API documentation is updated
    - OpenAPI spec reflects changes
    - README examples are current
```

### Execution Commands

```
# Update docs after code change
"Update the documentation in #File:docs/api/audio.md to match 
the changes in #File:backend/api/audio.py"

# Generate docs from code
"Generate API documentation for #Folder:backend/api based on 
the docstrings and type hints"

# Check doc consistency
"Verify #File:README.md examples still work with the current 
implementation in #Folder:backend"
```

---

## Workflow 6: Test-Driven Development

### Scenario
Writing tests before implementation.

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DEFINE REQUIREMENTS                                         │
│     • What should the code do?                                  │
│     • What are the edge cases?                                  │
├─────────────────────────────────────────────────────────────────┤
│  2. WRITE TESTS FIRST                                           │
│     • Unit tests for expected behavior                          │
│     • Property tests for invariants                             │
│     • Tests should fail initially                               │
├─────────────────────────────────────────────────────────────────┤
│  3. IMPLEMENT                                                   │
│     • Write minimal code to pass tests                          │
│     • Refactor while keeping tests green                        │
├─────────────────────────────────────────────────────────────────┤
│  4. VERIFY                                                      │
│     • All tests pass                                            │
│     • Coverage is adequate                                      │
│     • Edge cases handled                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Execution Commands

```
# Write tests first
"Write property-based tests for an audio validation function that:
- Accepts MP3 and WAV formats
- Rejects files over 10MB
- Validates audio duration is under 5 minutes

Put tests in #File:tests/test_audio_validation_props.py"

# Implement to pass tests
"Implement the audio validation function in 
#File:backend/services/audio_service.py to pass the tests"

# Verify
"Run the tests and fix any failures"
```

### Steering for TDD

```markdown
---
inclusion: fileMatch
fileMatchPattern: "tests/**/*.py"
---

# Test Writing Guidelines

## Property-Based Testing
- Use Hypothesis for Python
- Minimum 100 iterations per property
- Test invariants, not just examples

## Test Structure
```python
from hypothesis import given, strategies as st

@given(st.binary(min_size=1, max_size=1000))
def test_property_name(data):
    # Arrange
    # Act
    # Assert invariant
```

## Naming Convention
- `test_<function>_<scenario>_<expected>`
- Example: `test_validate_audio_invalid_format_raises_error`
```

---

## Workflow 7: Onboarding New Team Members

### Scenario
Helping new developers understand the project.

### Setup Documents

**Create comprehensive steering**:

`.kiro/steering/onboarding.md`:
```markdown
---
inclusion: manual
---

# Project Onboarding Guide

## Quick Start
1. Clone repository
2. Copy `.env.example` to `.env`
3. Run `poetry install`
4. Run `poetry run uvicorn backend.main:app --reload`

## Project Structure
- `backend/` - FastAPI backend
- `streamlit_app/` - Streamlit frontend
- `tests/` - Property-based tests
- `.kiro/` - Kiro configuration

## Key Files
- **Entry Point**: #[[file:backend/main.py]]
- **Configuration**: #[[file:backend/config.py]]
- **Main Service**: #[[file:backend/services/elevenlabs_service.py]]

## Development Workflow
1. Create spec for new features
2. Get approval at each phase
3. Execute tasks one at a time
4. Run tests before committing

## Coding Standards
See #[[file:.kiro/steering/coding-standards.md]]
```

### Execution Commands for Onboarding

```
# Project overview
"Explain the project structure in #Folder:backend"

# Understand a feature
"Walk me through how audio generation works, starting from 
#File:backend/api/audio.py"

# Find examples
"Show me examples of how to add a new API endpoint based on 
#Folder:backend/api"
```

---

## Combining Workflows

### Complex Feature with Full Workflow

```
# Day 1: Planning
"Create a spec for the patient conversation logging feature.
Reference the requirements in #File:user-need/user-need-phase1.md"

# Day 2: Design Review
"Review the design in #File:.kiro/specs/conversation-logs/design.md
against our architecture in #File:.kiro/steering/project-overview.md"

# Day 3-5: Implementation
"Execute task 1 from conversation-logs spec"
"Continue with next task"
[repeat until complete]

# Day 6: Review
"Review my #Git Diff for the conversation logging feature.
Ensure it follows #File:.kiro/steering/coding-standards.md"

# Day 7: Documentation
"Update #File:README.md with the new conversation logging feature"
```

## Summary

Effective Kiro workflows combine:

1. **Steering** - Consistent rules and context
2. **Specs** - Structured planning and execution
3. **Hooks** - Automated quality checks
4. **Context Keys** - Precise information sharing

Choose the right workflow for your task:
- New features → Full spec workflow
- Bug fixes → Context-driven debugging
- Refactoring → Incremental with tests
- Reviews → Git diff analysis
- Documentation → Sync with code changes

For questions or improvements to this guide, please update this document or discuss with the team.
