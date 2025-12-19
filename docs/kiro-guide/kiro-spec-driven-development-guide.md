# Kiro Spec-Driven Development Guide for LLMs

This guide teaches LLMs how to follow Kiro's spec-driven development methodology—a structured approach to transforming rough ideas into well-designed, testable software through iterative refinement.

## Overview

Spec-driven development in Kiro follows a three-phase workflow:

```
Idea → Requirements → Design → Tasks → Implementation
```

Each phase produces a document that must be explicitly approved by the user before proceeding. The goal is to produce:
1. A comprehensive specification with correctness properties
2. A working implementation that conforms to that specification
3. A test suite providing evidence the software obeys correctness properties

## Directory Structure

All spec files live in `.kiro/specs/{feature_name}/`:

```
.kiro/
└── specs/
    └── {feature-name}/           # kebab-case
        ├── requirements.md       # Phase 1
        ├── design.md             # Phase 2
        └── tasks.md              # Phase 3
```

---

## Phase 1: Requirements Document

### Purpose
Transform a rough idea into formal, testable requirements using EARS patterns and INCOSE quality rules.

### EARS Patterns (Required)

Every acceptance criterion MUST follow exactly one pattern:

| Pattern | Template | Example |
|---------|----------|---------|
| Ubiquitous | THE \<system\> SHALL \<response\> | THE System SHALL store user data securely |
| Event-driven | WHEN \<trigger\>, THE \<system\> SHALL \<response\> | WHEN a user submits a form, THE System SHALL validate inputs |
| State-driven | WHILE \<condition\>, THE \<system\> SHALL \<response\> | WHILE offline, THE System SHALL queue requests |
| Unwanted event | IF \<condition\>, THEN THE \<system\> SHALL \<response\> | IF authentication fails, THEN THE System SHALL log the attempt |
| Optional feature | WHERE \<option\>, THE \<system\> SHALL \<response\> | WHERE premium tier, THE System SHALL enable advanced features |
| Complex | [WHERE] [WHILE] [WHEN/IF] THE \<system\> SHALL \<response\> | WHERE admin, WHEN deleting a user, THE System SHALL require confirmation |

### INCOSE Quality Rules

Requirements MUST:
- Use active voice (who does what)
- Avoid vague terms ("quickly", "adequate", "user-friendly")
- Avoid escape clauses ("where possible", "as appropriate")
- Avoid negative statements ("SHALL NOT")
- Express one thought per requirement
- Use explicit, measurable conditions
- Use consistent, defined terminology
- Avoid pronouns ("it", "them")
- Avoid absolutes ("never", "always", "100%")
- Be solution-free (focus on WHAT, not HOW)

### Document Template

```markdown
# Requirements Document

## Introduction

[1-2 paragraph summary of the feature/system]

## Glossary

- **Term 1**: [Definition]
- **Term 2**: [Definition]

## Requirements

### Requirement 1

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. WHEN [event], THE [System_Name] SHALL [response]
2. WHILE [state], THE [System_Name] SHALL [response]
3. IF [undesired event], THEN THE [System_Name] SHALL [response]

### Requirement 2
...
```

### Special Considerations

**Parsers and Serializers**: Always include:
- A requirement for a pretty printer/serializer
- An acceptance criterion for round-trip testing (parse → print → parse = original)

### Workflow Rules

1. Generate initial requirements WITHOUT asking clarifying questions first
2. Ask user: "Do the requirements look good? If so, we can move on to the design."
3. Iterate until explicit approval received
4. Do NOT proceed to design without approval

---

## Phase 2: Design Document

### Purpose
Create a comprehensive technical design that addresses all requirements and defines correctness properties for testing.

### Document Sections

1. **Overview** - High-level description
2. **Architecture** - System structure (use Mermaid diagrams)
3. **Components and Interfaces** - Classes, methods, signatures
4. **Data Models** - Types, enums, structures
5. **Correctness Properties** - Formal testable properties
6. **Error Handling** - Strategy and exception types
7. **Testing Strategy** - Unit + property-based testing approach

### Correctness Properties

#### Pre-work Analysis

Before writing properties, analyze EACH acceptance criterion:

```
X.Y Criteria Name
  Thoughts: [step-by-step analysis of testability]
  Testable: yes - property | yes - example | edge-case | no
```

#### Property Categories

| Category | Description | Example |
|----------|-------------|---------|
| Invariants | Properties preserved after transformation | Collection size after map |
| Round Trip | Operation + inverse = original | decode(encode(x)) == x |
| Idempotence | f(x) = f(f(x)) | Distinct filter applied twice |
| Metamorphic | Known relationships between components | len(filter(x)) <= len(x) |
| Model-Based | Optimized vs reference implementation | Fast sort vs simple sort |
| Confluence | Order independence | a + b = b + a |
| Error Conditions | Bad inputs signal errors properly | Invalid input raises exception |

#### Property Format

```markdown
### Property N: [Name]

*For any* [universal quantifier], [property statement]

**Validates: Requirements X.Y**
```

#### Property Reflection

After initial analysis, eliminate redundancy:
- Remove properties implied by others
- Combine properties that can be tested together
- Ensure each property provides unique validation value

### Testing Strategy Requirements

Specify BOTH:
- **Unit tests**: Specific examples, edge cases, error conditions
- **Property-based tests**: Universal properties across all inputs

Choose a PBT library for the target language:
- Python: Hypothesis
- JavaScript/TypeScript: fast-check
- Haskell: QuickCheck
- Scala: ScalaCheck

Configure minimum 100 iterations per property test.

### Workflow Rules

1. Write all sections through Data Models
2. STOP before Correctness Properties
3. Complete prework analysis
4. Write Correctness Properties based on prework
5. Ask user: "Does the design look good? If so, we can move on to the implementation plan."
6. Iterate until explicit approval received

---

## Phase 3: Tasks Document

### Purpose
Create an actionable implementation plan with discrete coding tasks.

### Task Format

```markdown
# Implementation Plan

- [ ] 1. [Epic/Major Task]
  - [Context and details]
  - _Requirements: X.Y, Z.W_

- [ ] 2. [Another Epic]
  - [ ] 2.1 [Sub-task]
    - [Implementation details]
    - _Requirements: A.B_
  - [ ]* 2.2 [Optional sub-task - tests]
    - **Property N: [Property Name]**
    - **Validates: Requirements X.Y**
  - [ ] 2.3 [Required sub-task]
    - [Details]
    - _Requirements: C.D_

- [ ] N. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
```

### Task Rules

1. **Coding tasks only** - No deployment, user testing, or non-code activities
2. **Incremental** - Each task builds on previous tasks
3. **No orphaned code** - Everything integrates with previous steps
4. **Reference requirements** - Every task links to specific requirements
5. **Property tests near implementation** - Place PBT tasks close to related code

### Optional Tasks (marked with *)

- Property-based tests
- Unit tests
- Integration tests
- Test utilities and fixtures

Top-level tasks are NEVER optional. Only sub-tasks can be marked with *.

### Checkpoints

Include checkpoint tasks at reasonable breaks:
```markdown
- [ ] N. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
```

### Workflow Rules

1. Create tasks based on approved design
2. Ask user about optional tasks: "Keep optional tasks (faster MVP)" or "Make all tasks required (comprehensive)"
3. Iterate until explicit approval received
4. STOP after approval - do not begin implementation

---

## Spec Execution Phase

This section describes how to properly execute tasks from an approved spec. Following this process ensures consistent, high-quality implementation.

### Pre-Execution Checklist

Before executing ANY task, complete these steps in order:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Check for steering documents (.kiro/steering/*.md)      │
│                          ↓                                  │
│  2. Read requirements.md - understand WHAT to build         │
│                          ↓                                  │
│  3. Read design.md - understand HOW to build it             │
│                          ↓                                  │
│  4. Read tasks.md - identify the specific task to execute   │
│                          ↓                                  │
│  5. Execute the task                                        │
│                          ↓                                  │
│  6. Update task status                                      │
└─────────────────────────────────────────────────────────────┘
```

### Step 1: Check Steering Documents

Steering files provide project-wide context and rules that apply to all implementations.

```
.kiro/
└── steering/
    ├── coding-standards.md      # Always included
    ├── api-guidelines.md        # Always included
    └── react-patterns.md        # Conditionally included (fileMatch)
```

**Steering Types**:
- **Always included**: Read these for every task
- **Conditional (fileMatch)**: Read when working on matching files
- **Manual**: Read when user explicitly references them

**Action**: List and read all steering files before starting implementation.

### Step 2: Read Requirements Document

Location: `.kiro/specs/{feature-name}/requirements.md`

**Extract**:
- Glossary terms (use consistent terminology)
- User stories (understand the WHY)
- Acceptance criteria (know the success conditions)
- Requirement numbers referenced by your task

**Example**: If task says `_Requirements: 2.1, 3.3_`, read those specific acceptance criteria carefully.

### Step 3: Read Design Document

Location: `.kiro/specs/{feature-name}/design.md`

**Extract**:
- Architecture overview
- Component interfaces and signatures
- Data models (enums, classes, types)
- Correctness properties (for testing tasks)
- Error handling strategy
- Testing strategy and chosen libraries

### Step 4: Identify Task to Execute

Location: `.kiro/specs/{feature-name}/tasks.md`

**Task Selection Rules**:
1. If user specifies a task → execute that task
2. If no task specified → recommend the next incomplete task
3. Never skip ahead to later tasks
4. Complete sub-tasks before parent tasks

**Task Status Markers**:
```markdown
- [ ] Not started
- [-] In progress
- [x] Completed
- [ ]* Optional (skip unless requested)
```

### Step 5: Execute the Task

#### Execution Rules

1. **ONE task at a time** - Never implement multiple tasks simultaneously
2. **Mark in progress** - Update task status to `[-]` when starting
3. **Follow the design** - Use interfaces, types, and patterns from design.md
4. **Reference requirements** - Ensure implementation satisfies linked acceptance criteria
5. **Write minimal code** - Only what's needed for THIS task
6. **Stop after completion** - Do NOT automatically continue to next task

#### Task Execution Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Mark task as in-progress: - [-]                             │
│                          ↓                                   │
│  Implement the code changes                                  │
│                          ↓                                   │
│  Run tests / validate against requirements                   │
│                          ↓                                   │
│  Fix any issues (max 2 attempts, then ask user)              │
│                          ↓                                   │
│  Mark task as complete: - [x]                                │
│                          ↓                                   │
│  STOP - Wait for user to request next task                   │
└──────────────────────────────────────────────────────────────┘
```

#### Sub-Task Handling

When a task has sub-tasks:
```markdown
- [ ] 2. Implement data models
  - [ ] 2.1 Create enums
  - [ ] 2.2 Create dataclasses
  - [ ]* 2.3 Write unit tests (optional)
```

1. Start with first sub-task (2.1)
2. Complete each sub-task in order
3. Skip optional (*) sub-tasks unless user requests
4. Mark parent complete only when all required sub-tasks done

#### Checkpoint Tasks

When you encounter a checkpoint:
```markdown
- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
```

1. Run all existing tests
2. Fix any failures
3. If stuck after 2 attempts, ask user for guidance
4. Only proceed when all tests pass

### Step 6: Update Task Status

After completing a task, update the tasks.md file:

```markdown
# Before
- [ ] 2.1 Create data models module

# After  
- [x] 2.1 Create data models module
```

---

## Execution Examples

### Example 1: Starting Fresh

User: "Execute task 1 from the todo-app spec"

LLM Actions:
1. Check `.kiro/steering/` for any steering files
2. Read `.kiro/specs/todo-app/requirements.md`
3. Read `.kiro/specs/todo-app/design.md`
4. Read `.kiro/specs/todo-app/tasks.md`
5. Locate task 1 and its details
6. Mark task 1 as in-progress
7. Implement the task
8. Mark task 1 as complete
9. Report completion and STOP

### Example 2: Continuing Work

User: "Continue with the next task"

LLM Actions:
1. Read tasks.md to find first incomplete task
2. Verify requirements.md and design.md are understood
3. Execute the identified task
4. Update status and STOP

### Example 3: Task with Property Test

Task:
```markdown
- [ ] 2.2 Write property test for return type consistency
  - **Property 1: Return Type Consistency**
  - **Validates: Requirements 1.4**
```

LLM Actions:
1. Read Property 1 from design.md Correctness Properties section
2. Read Requirement 1.4 from requirements.md
3. Read Testing Strategy for PBT library choice
4. Implement property test with:
   - Comment: `**Feature: todo-app, Property 1: Return Type Consistency**`
   - Minimum 100 iterations
   - Generators for input types
5. Run test to verify it passes
6. Mark complete and STOP

---

## Full Execution Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SPEC EXECUTION WORKFLOW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐                                                    │
│  │ User Request│ "Execute task X" or "Start implementation"         │
│  └──────┬──────┘                                                    │
│         ↓                                                           │
│  ┌─────────────────────────────────────────┐                        │
│  │ 1. LOAD CONTEXT                         │                        │
│  │    • Check .kiro/steering/*.md          │                        │
│  │    • Read requirements.md               │                        │
│  │    • Read design.md                     │                        │
│  │    • Read tasks.md                      │                        │
│  └──────┬──────────────────────────────────┘                        │
│         ↓                                                           │
│  ┌─────────────────────────────────────────┐                        │
│  │ 2. IDENTIFY TASK                        │                        │
│  │    • User-specified OR next incomplete  │                        │
│  │    • Check if optional (*) - skip?      │                        │
│  │    • Read linked requirements           │                        │
│  └──────┬──────────────────────────────────┘                        │
│         ↓                                                           │
│  ┌─────────────────────────────────────────┐                        │
│  │ 3. EXECUTE TASK                         │                        │
│  │    • Mark as in-progress [-]            │                        │
│  │    • Write code following design        │                        │
│  │    • Run tests/validation               │                        │
│  │    • Fix issues (max 2 attempts)        │                        │
│  └──────┬──────────────────────────────────┘                        │
│         ↓                                                           │
│  ┌─────────────────────────────────────────┐                        │
│  │ 4. COMPLETE                             │                        │
│  │    • Mark as complete [x]               │                        │
│  │    • Report to user                     │                        │
│  │    • STOP - await next instruction      │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Testing During Implementation

### Testing During Implementation

**Property-Based Tests**:
- Tag with: `**Feature: {feature_name}, Property {number}: {property_text}**`
- Implement ONLY the property specified by the task
- Use the PBT library specified in design document
- Configure minimum 100 iterations

**Unit Tests**:
- Co-locate with source files when possible
- Use descriptive test names
- Cover edge cases and error conditions

### Test Failure Handling

- Tests may reveal bugs in code (not just test issues)
- If behavior is confusing and not in spec, ask user
- Do NOT give up - correct code is essential
- Limit fix attempts to 2 tries, then ask user for direction

---

## Key Principles

### User Approval Gates

```
Requirements ──[approval]──> Design ──[approval]──> Tasks ──[approval]──> Implementation
```

Never skip approval. Never assume approval. Always ask explicitly.

### Document Dependencies

- Design depends on Requirements
- Tasks depend on Design
- Implementation depends on all three

### Iteration Over Perfection

- Generate initial documents quickly
- Refine through user feedback
- Multiple iterations are expected and encouraged

### Correctness Focus

The methodology prioritizes:
1. Formal specification of behavior
2. Testable properties
3. Evidence of correctness through PBT

---

## Quick Reference: User Prompts

| Phase | Prompt |
|-------|--------|
| Requirements | "Do the requirements look good? If so, we can move on to the design." |
| Design | "Does the design look good? If so, we can move on to the implementation plan." |
| Tasks | "Keep optional tasks (faster MVP)" or "Make all tasks required (comprehensive)" |

---

## Anti-Patterns to Avoid

### During Spec Creation
❌ Proceeding without explicit user approval  
❌ Combining multiple phases in one interaction  
❌ Skipping prework analysis for correctness properties  
❌ Writing vague requirements ("should be fast")  
❌ Creating non-coding tasks (deployment, user testing)  
❌ Marking top-level tasks as optional  
❌ Guessing at requirements instead of asking  

### During Execution
❌ Implementing multiple tasks at once  
❌ Skipping the context-loading step (steering, requirements, design)  
❌ Starting implementation without reading the full spec  
❌ Automatically continuing to next task without user direction  
❌ Writing tests that mock everything (test real behavior)  
❌ Giving up on failing tests  
❌ Ignoring steering document rules  
❌ Implementing optional (*) tasks without user request  
❌ Skipping checkpoints when tests are failing

---

## Troubleshooting Execution Issues

### Test Failures

```
Attempt 1: Run tests → Fail → Analyze error → Fix
Attempt 2: Run tests → Fail → Analyze error → Fix
Attempt 3: STOP → Ask user for guidance
```

Never:
- Disable or skip failing tests
- Mock away the problem
- Delete the test

### Missing Context

If requirements or design seem incomplete:
1. Ask user if spec needs updating
2. Do NOT guess or assume
3. Return to appropriate phase if needed

### Conflicting Requirements

If task requirements conflict with design:
1. Point out the conflict to user
2. Ask which takes precedence
3. Suggest updating the spec for consistency

### Stuck on Implementation

If unable to implement after reasonable effort:
1. Explain what you've tried
2. Identify the specific blocker
3. Ask user for direction or clarification
4. Do NOT implement a workaround that violates the spec  

---

## Quick Reference: Execution Commands

| User Says | LLM Action |
|-----------|------------|
| "Execute task 3" | Load context → Execute task 3 → Stop |
| "Start the spec" / "Begin implementation" | Load context → Execute task 1 → Stop |
| "Continue" / "Next task" | Find next incomplete task → Execute → Stop |
| "Skip optional tasks" | Mark optional (*) tasks as skipped, continue to next required |
| "Run the checkpoint" | Run all tests, report status, fix if needed |
| "What's the next task?" | Read tasks.md, report next incomplete task (don't execute) |
| "Show progress" | Read tasks.md, summarize completed/remaining tasks |

---

## Example Workflow

1. User: "I want a todo app"
2. LLM: Creates `.kiro/specs/todo-app/requirements.md`
3. LLM: "Do the requirements look good?"
4. User: "Add offline support"
5. LLM: Updates requirements.md
6. LLM: "Do the requirements look good?"
7. User: "Yes"
8. LLM: Creates `.kiro/specs/todo-app/design.md`
9. LLM: "Does the design look good?"
10. User: "Yes"
11. LLM: Creates `.kiro/specs/todo-app/tasks.md`
12. LLM: "Keep optional tasks or make all required?"
13. User: "Keep optional"
14. LLM: "Spec complete. Open tasks.md and click 'Start task' to begin implementation."

---

## Complete Execution Example

Here's a full example of executing a task from start to finish:

### User Request
"Execute task 2.1 from the gemini-deep-research-mvp spec"

### LLM Execution Steps

**Step 1: Check Steering**
```
Checking .kiro/steering/ for project rules...
No steering files found (or read existing ones)
```

**Step 2: Load Requirements**
```
Reading .kiro/specs/gemini-deep-research-mvp/requirements.md...

Key requirements for task 2.1:
- Requirement 1.4: THE Backend Service SHALL return structured data 
  objects or dictionaries from all methods
```

**Step 3: Load Design**
```
Reading .kiro/specs/gemini-deep-research-mvp/design.md...

Relevant design elements:
- ResearchStatus enum: IN_PROGRESS, COMPLETED, FAILED
- StreamEventType enum: INTERACTION_START, CONTENT_DELTA, etc.
- ResearchResult dataclass with fields: interaction_id, status, output_text, error_message
- StreamEvent dataclass with fields: event_type, event_id, interaction_id, etc.
```

**Step 4: Identify Task**
```
Reading .kiro/specs/gemini-deep-research-mvp/tasks.md...

Task 2.1: Create data models module with enums and dataclasses
- Implement ResearchStatus, StreamEventType, DeltaType enums
- Implement ResearchResult and StreamEvent dataclasses
- Requirements: 1.4
```

**Step 5: Execute**
```
Marking task 2.1 as in-progress...

Creating src/models.py:
- ResearchStatus enum
- StreamEventType enum  
- DeltaType enum
- ResearchResult dataclass
- StreamEvent dataclass

Running validation...
All types check passed.
```

**Step 6: Complete**
```
Marking task 2.1 as complete.

✓ Task 2.1 completed successfully.
Created src/models.py with all required enums and dataclasses.

Awaiting your next instruction.
```

---

## Summary

The Kiro spec-driven development methodology ensures:

1. **Clear requirements** using EARS patterns
2. **Comprehensive design** with correctness properties
3. **Actionable tasks** with requirement traceability
4. **Disciplined execution** one task at a time
5. **Quality assurance** through property-based testing

Always remember:
- Load full context before executing
- One task at a time
- Stop after each task
- Never skip approval gates
- Tests reveal bugs in code, not just test issues
