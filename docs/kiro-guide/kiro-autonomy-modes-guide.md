# Kiro Autonomy Modes Guide

This guide explains Kiro's autonomy modes and how to effectively manage file changes during AI-assisted development. It's designed for team members using different IDEs or LLM tools who need to understand or replicate this pattern.

## What Are Autonomy Modes?

Autonomy modes control how Kiro handles file modifications in your workspace. They balance productivity with control, letting you choose the right level of oversight for your situation.

## Available Modes

| Mode | Description | File Changes | Best For |
|------|-------------|--------------|----------|
| **Autopilot** | Kiro modifies files autonomously | Applied immediately | Trusted tasks, rapid iteration |
| **Supervised** | User reviews changes before/after | Applied with review option | Learning, critical code, unfamiliar tasks |

## Mode Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│                      AUTOPILOT MODE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Request ──▶ Kiro Executes ──▶ Files Modified              │
│                                           │                     │
│                                           ▼                     │
│                                    Changes Applied              │
│                                    (can revert if needed)       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     SUPERVISED MODE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Request ──▶ Kiro Executes ──▶ Files Modified              │
│                                           │                     │
│                                           ▼                     │
│                                    Review Opportunity           │
│                                           │                     │
│                              ┌────────────┴────────────┐        │
│                              ▼                         ▼        │
│                         Keep Changes            Revert Changes  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Autopilot Mode

### When to Use

✅ **Good for**:
- Routine tasks you've done before
- Well-defined spec execution
- Rapid prototyping
- Trusted, low-risk changes
- Experienced users

❌ **Avoid for**:
- Critical production code
- Unfamiliar codebases
- Complex refactoring
- Learning new patterns

### How It Works

1. You send a request to Kiro
2. Kiro analyzes and executes the task
3. Files are modified immediately
4. You can review changes in git diff
5. Revert if needed using git

### Best Practices

```markdown
## Autopilot Safety Checklist

Before enabling autopilot:
- [ ] Working on a git branch (not main)
- [ ] Recent commit as restore point
- [ ] Tests exist for critical code
- [ ] Task is well-understood

During autopilot:
- [ ] Review changes periodically
- [ ] Run tests after significant changes
- [ ] Commit working states frequently

After autopilot session:
- [ ] Review full git diff
- [ ] Run complete test suite
- [ ] Verify no unintended changes
```

### Recovery from Unwanted Changes

```bash
# View what changed
git diff

# Revert specific file
git checkout -- path/to/file.py

# Revert all changes
git checkout -- .

# Revert to last commit
git reset --hard HEAD
```

## Supervised Mode

### When to Use

✅ **Good for**:
- Learning Kiro's capabilities
- Critical or sensitive code
- Complex multi-file changes
- Unfamiliar codebases
- Team code reviews

❌ **May slow down**:
- Simple, repetitive tasks
- Well-understood changes
- Rapid iteration cycles

### How It Works

1. You send a request to Kiro
2. Kiro analyzes and executes the task
3. Files are modified
4. You're given opportunity to review
5. Accept or revert changes

### Review Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUPERVISED REVIEW FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Kiro completes task                                         │
│         ↓                                                       │
│  2. Review changes in editor                                    │
│         ↓                                                       │
│  3. Check diff for each modified file                           │
│         ↓                                                       │
│  4. Decision point:                                             │
│         │                                                       │
│         ├──▶ Accept all → Continue working                      │
│         │                                                       │
│         ├──▶ Partial accept → Revert specific files             │
│         │                                                       │
│         └──▶ Reject all → Revert and retry with new prompt      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Choosing the Right Mode

### Decision Matrix

| Scenario | Recommended Mode | Reason |
|----------|------------------|--------|
| Executing approved spec tasks | Autopilot | Well-defined, tested workflow |
| Bug fix in critical code | Supervised | Need careful review |
| Adding new feature | Supervised → Autopilot | Start supervised, switch when comfortable |
| Refactoring | Supervised | High risk of unintended changes |
| Documentation updates | Autopilot | Low risk, easy to review |
| Learning new codebase | Supervised | Understand what Kiro does |
| Rapid prototyping | Autopilot | Speed over precision |
| Production hotfix | Supervised | Maximum caution required |

### Mode Switching Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODE SWITCHING STRATEGY                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  New Project/Feature                                            │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────┐                                            │
│  │  SUPERVISED     │  Learn patterns, verify behavior           │
│  │  (First few     │                                            │
│  │   iterations)   │                                            │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼ Comfortable with patterns                           │
│  ┌─────────────────┐                                            │
│  │  AUTOPILOT      │  Rapid execution, periodic review          │
│  │  (Routine       │                                            │
│  │   tasks)        │                                            │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼ Critical change needed                              │
│  ┌─────────────────┐                                            │
│  │  SUPERVISED     │  Careful review for important changes      │
│  │  (Critical      │                                            │
│  │   sections)     │                                            │
│  └─────────────────┘                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Managing File Changes

### Before Making Changes

1. **Create a branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Commit current state**:
   ```bash
   git add .
   git commit -m "checkpoint before Kiro changes"
   ```

3. **Verify tests pass**:
   ```bash
   pytest tests/ -v
   ```

### During Changes

1. **Monitor modified files** - Watch for unexpected changes
2. **Run tests frequently** - Catch issues early
3. **Commit working states** - Create restore points

### After Changes

1. **Review full diff**:
   ```bash
   git diff HEAD~1
   ```

2. **Run complete test suite**:
   ```bash
   pytest tests/ -v
   ```

3. **Check for unintended changes**:
   ```bash
   git status
   git diff --stat
   ```

## Reverting Changes

### Revert Single File

```bash
# Revert uncommitted changes
git checkout -- path/to/file.py

# Revert to specific commit
git checkout <commit-hash> -- path/to/file.py
```

### Revert Multiple Files

```bash
# Revert all uncommitted changes
git checkout -- .

# Revert specific directory
git checkout -- backend/services/
```

### Revert to Previous State

```bash
# Soft reset (keep changes staged)
git reset --soft HEAD~1

# Hard reset (discard all changes)
git reset --hard HEAD~1

# Reset to specific commit
git reset --hard <commit-hash>
```

### Using Git Stash

```bash
# Stash current changes
git stash

# Apply stashed changes
git stash pop

# List stashes
git stash list

# Apply specific stash
git stash apply stash@{0}
```

## Adapting for Other Tools

### For Cursor/Continue

Most AI coding tools have similar concepts:
- **Accept/Reject** buttons for changes
- **Diff view** for reviewing modifications
- **Undo** functionality

Apply the same principles:
1. Work on branches
2. Commit frequently
3. Review changes before accepting
4. Use version control for recovery

### For Direct LLM API Usage

Implement your own change management:

```python
import shutil
from pathlib import Path
from datetime import datetime

class ChangeManager:
    def __init__(self, workspace_root: str):
        self.workspace = Path(workspace_root)
        self.backup_dir = self.workspace / ".kiro_backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def backup_file(self, file_path: str) -> str:
        """Create backup before modification."""
        source = self.workspace / file_path
        if source.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.replace('/', '_')}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            shutil.copy2(source, backup_path)
            return str(backup_path)
        return None
    
    def restore_file(self, file_path: str, backup_path: str):
        """Restore file from backup."""
        target = self.workspace / file_path
        shutil.copy2(backup_path, target)
    
    def supervised_write(self, file_path: str, content: str) -> bool:
        """Write with backup and confirmation."""
        backup = self.backup_file(file_path)
        
        # Write new content
        target = self.workspace / file_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        
        # Show diff and ask for confirmation
        print(f"Modified: {file_path}")
        print("Accept changes? (y/n): ", end="")
        
        if input().lower() != 'y':
            if backup:
                self.restore_file(file_path, backup)
            else:
                target.unlink()
            return False
        
        return True
```

## Best Practices

### Do's ✅

1. **Always work on branches** - Never modify main directly
2. **Commit frequently** - Create restore points
3. **Review changes** - Even in autopilot mode
4. **Run tests** - Verify changes don't break anything
5. **Use meaningful commits** - Easy to identify restore points

### Don'ts ❌

1. **Don't skip reviews for critical code** - Use supervised mode
2. **Don't ignore test failures** - Fix before continuing
3. **Don't work without version control** - No safety net
4. **Don't mix unrelated changes** - Hard to revert selectively
5. **Don't trust blindly** - AI can make mistakes

## Workflow Integration

### With Specs

```markdown
## Spec Execution Mode Strategy

- **Requirements phase**: Supervised (review generated requirements)
- **Design phase**: Supervised (review architecture decisions)
- **Task execution**: Autopilot (well-defined tasks)
- **Checkpoint tasks**: Supervised (verify test results)
```

### With Hooks

```yaml
# Hook to remind about mode selection
name: "Mode Reminder"
trigger:
  event: onSessionCreate
action:
  type: sendMessage
  message: |
    Starting new session. Current mode considerations:
    - Critical code? Use supervised mode
    - Routine tasks? Autopilot is fine
    - Remember to commit before major changes
```

## Troubleshooting

### Accidentally Accepted Bad Changes

1. Check git reflog for recent commits:
   ```bash
   git reflog
   ```

2. Reset to known good state:
   ```bash
   git reset --hard <good-commit>
   ```

### Lost Track of Changes

1. View all modifications:
   ```bash
   git diff --stat HEAD~5
   ```

2. Review each file:
   ```bash
   git diff HEAD~5 -- path/to/file.py
   ```

### Mixed Good and Bad Changes

1. Interactive reset:
   ```bash
   git reset -p HEAD~1
   ```

2. Or cherry-pick good changes:
   ```bash
   git stash
   git reset --hard <good-commit>
   git stash pop
   git add -p  # selectively stage
   ```

## Summary

Autonomy modes provide flexibility in how Kiro manages file changes:

1. **Autopilot** - Fast execution, requires discipline
2. **Supervised** - Careful review, slower but safer

Key principles:
- Always use version control
- Match mode to task risk level
- Review changes regardless of mode
- Commit frequently for easy recovery

For questions or improvements to this guide, please update this document or discuss with the team.
