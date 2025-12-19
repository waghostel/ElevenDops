# Kiro Troubleshooting Guide

This guide helps diagnose and resolve common issues when working with Kiro. It's designed for team members using different IDEs or LLM tools who need to understand or replicate troubleshooting patterns.

## Quick Diagnosis Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                    ISSUE DIAGNOSIS FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  What's the problem?                                            │
│         │                                                       │
│         ├──▶ Kiro not responding ──▶ See "Connection Issues"    │
│         │                                                       │
│         ├──▶ Wrong output ──▶ See "Context Issues"              │
│         │                                                       │
│         ├──▶ File changes fail ──▶ See "File Operation Issues"  │
│         │                                                       │
│         ├──▶ MCP tools fail ──▶ See "MCP Issues"                │
│         │                                                       │
│         ├──▶ Specs not working ──▶ See "Spec Issues"            │
│         │                                                       │
│         ├──▶ Hooks not triggering ──▶ See "Hook Issues"         │
│         │                                                       │
│         └──▶ Steering not applied ──▶ See "Steering Issues"     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Connection Issues

### Symptoms
- Kiro doesn't respond to messages
- Long loading times
- "Connection failed" errors

### Solutions

**1. Check Kiro Status**
- Look for Kiro icon in status bar
- Check if Kiro panel is responsive

**2. Restart Kiro**
- Command Palette → "Kiro: Restart"
- Or close and reopen the IDE

**3. Check Network**
- Verify internet connection
- Check if firewall blocks Kiro
- Try disabling VPN temporarily

**4. Clear Cache**
- Close IDE
- Delete Kiro cache folder
- Restart IDE

### Prevention
- Keep Kiro updated
- Maintain stable network connection
- Report persistent issues to support

---

## Context Issues

### Symptoms
- Kiro ignores project conventions
- Generated code doesn't match patterns
- Missing information in responses

### Diagnosis

```
┌─────────────────────────────────────────────────────────────────┐
│  Context Issue Checklist                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ Are steering files in .kiro/steering/?                       │
│  □ Is front matter syntax correct?                              │
│  □ Are file references valid?                                   │
│  □ Is the codebase indexed?                                     │
│  □ Are you using correct context keys?                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Solutions

**1. Verify Steering Files**
```bash
# Check steering files exist
ls .kiro/steering/

# Verify front matter syntax
cat .kiro/steering/project-overview.md | head -10
```

**2. Check File References**
```markdown
# Correct syntax
#[[file:docs/api/index.md]]

# Wrong syntax (spaces)
#[[ file: docs/api/index.md ]]

# Wrong syntax (absolute path)
#[[file:/home/user/project/docs/api/index.md]]
```

**3. Refresh Codebase Index**
- Command Palette → "Kiro: Reindex Codebase"
- Wait for indexing to complete

**4. Provide Explicit Context**
```
# Instead of assuming context
"Fix the bug"

# Provide explicit context
"Fix the bug in #File:backend/services/audio.py
Error from #Terminal: [paste error]
Follow patterns in #File:backend/services/elevenlabs_service.py"
```

### Prevention
- Always include relevant context keys
- Keep steering files up to date
- Use file references in documentation

---

## File Operation Issues

### Symptoms
- Files not created/modified
- Permission errors
- Wrong file locations

### Solutions

**1. Check Permissions**
```bash
# Check file permissions
ls -la path/to/file.py

# Check directory permissions
ls -la path/to/directory/
```

**2. Verify Path**
- Paths should be relative to workspace root
- Check for typos in file names
- Verify directory exists

**3. Check File Locks**
- Close file in other editors
- Check for running processes using the file
- Restart IDE if file is locked

**4. Git Issues**
```bash
# Check if file is ignored
git check-ignore path/to/file.py

# Check git status
git status
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "File not found" | Wrong path | Verify path is relative to workspace |
| "Permission denied" | No write access | Check file/folder permissions |
| "File is locked" | Open elsewhere | Close file in other applications |
| "Directory not found" | Missing parent | Create parent directories first |

---

## MCP Issues

### Symptoms
- MCP tools not available
- Tool execution fails
- Server not starting

### Diagnosis

**1. Check Configuration**
```bash
# Workspace config
cat .kiro/settings/mcp.json

# User config (outside workspace)
cat ~/.kiro/settings/mcp.json
```

**2. Verify JSON Syntax**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["package@latest"],
      "disabled": false
    }
  }
}
```

**3. Check Server Status**
- Open MCP Server view in Kiro panel
- Look for error indicators
- Check server logs

### Solutions

**1. Fix Configuration**
```json
// Common issues:

// Missing comma
{
  "mcpServers": {
    "server1": { ... }  // ← missing comma
    "server2": { ... }
  }
}

// Wrong field name
{
  "mcpServers": {
    "server": {
      "cmd": "uvx"  // ← should be "command"
    }
  }
}
```

**2. Install Prerequisites**
```bash
# Install uv (for uvx)
pip install uv

# Verify installation
uvx --version
```

**3. Test Server Manually**
```bash
# Run server command directly
uvx package-name@latest --help
```

**4. Reconnect Server**
- MCP Server view → Click reconnect
- Or restart Kiro

### Common MCP Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Server not found" | Wrong command | Verify command path |
| "Connection refused" | Server crashed | Check server logs, restart |
| "Tool not found" | Wrong tool name | Use `activate` to get correct names |
| "Invalid arguments" | Schema mismatch | Check tool's inputSchema |

---

## Spec Issues

### Symptoms
- Spec not created properly
- Tasks not executing
- Wrong phase progression

### Diagnosis

```
┌─────────────────────────────────────────────────────────────────┐
│  Spec Issue Checklist                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ Is spec in .kiro/specs/{feature-name}/?                      │
│  □ Do all three files exist (requirements, design, tasks)?      │
│  □ Is markdown syntax correct?                                  │
│  □ Are task checkboxes properly formatted?                      │
│  □ Did you get approval at each phase?                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Solutions

**1. Verify Spec Structure**
```bash
# Check spec directory
ls .kiro/specs/feature-name/

# Expected files:
# - requirements.md
# - design.md
# - tasks.md
```

**2. Fix Task Format**
```markdown
# Correct format
- [ ] 1. Task description
  - Details here
  - _Requirements: 1.1, 1.2_

# Wrong format (no space after checkbox)
- []1. Task description

# Wrong format (wrong checkbox)
- () 1. Task description
```

**3. Reset Spec Progress**
```markdown
# Change completed tasks back to incomplete
- [x] 1. Completed task  →  - [ ] 1. Completed task
```

**4. Re-run Approval**
```
"Review the requirements in #File:.kiro/specs/feature/requirements.md
and confirm if they look good"
```

---

## Hook Issues

### Symptoms
- Hooks not triggering
- Wrong action executed
- Hook errors in output

### Diagnosis

**1. Check Hook Configuration**
- Explorer view → Agent Hooks section
- Verify hook is enabled
- Check trigger conditions

**2. Verify File Pattern**
```yaml
# Test if pattern matches your file
trigger:
  event: onFileSave
  filePattern: "backend/**/*.py"  # Does your file match?
```

### Solutions

**1. Fix File Pattern**
```yaml
# Too specific
filePattern: "backend/services/audio.py"

# Better - matches all Python in services
filePattern: "backend/services/**/*.py"

# Matches all Python files
filePattern: "**/*.py"
```

**2. Check Action Syntax**
```yaml
# Correct sendMessage
action:
  type: sendMessage
  message: "Your message here"

# Correct executeCommand
action:
  type: executeCommand
  command: "pytest tests/ -v"
```

**3. Test Hook Manually**
- For `onManualTrigger`: Click the hook button
- For `onFileSave`: Save a matching file
- Check Kiro output for errors

### Common Hook Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Hook not found" | Deleted or renamed | Recreate hook |
| "Pattern no match" | Wrong glob pattern | Fix filePattern |
| "Command failed" | Invalid command | Test command in terminal |
| "Circular trigger" | Hook triggers itself | Add exclusion pattern |

---

## Steering Issues

### Symptoms
- Steering rules not applied
- Wrong inclusion behavior
- File references not resolved

### Diagnosis

**1. Check Front Matter**
```markdown
---
inclusion: always
---

# Must have valid YAML between ---
```

**2. Verify Inclusion Type**
```yaml
# Always included
inclusion: always

# Conditional on file pattern
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"

# Manual only
inclusion: manual
```

### Solutions

**1. Fix Front Matter Syntax**
```markdown
# Wrong - missing closing ---
---
inclusion: always

# Content here

# Correct
---
inclusion: always
---

# Content here
```

**2. Fix File Match Pattern**
```yaml
# Wrong - missing quotes
fileMatchPattern: backend/**/*.py

# Correct
fileMatchPattern: "backend/**/*.py"
```

**3. Test File Reference**
```markdown
# Verify file exists
#[[file:docs/api/index.md]]

# Check path from workspace root
ls docs/api/index.md
```

**4. Force Reload**
- Close and reopen the file
- Restart Kiro
- Check for syntax errors in YAML

---

## Performance Issues

### Symptoms
- Slow responses
- High memory usage
- IDE lag

### Solutions

**1. Reduce Context Size**
- Use specific file references instead of folders
- Limit `#Codebase` searches
- Remove unnecessary steering files

**2. Clear Index**
- Command Palette → "Kiro: Clear Index"
- Reindex only necessary files

**3. Disable Unused Features**
- Disable unused MCP servers
- Remove unnecessary hooks
- Simplify steering files

**4. Check System Resources**
```bash
# Check memory usage
# Windows
tasklist | findstr kiro

# Mac/Linux
ps aux | grep kiro
```

---

## Debug Mode

### Enable Verbose Logging

1. Open Kiro settings
2. Enable debug/verbose mode
3. Check output panel for detailed logs

### Collect Debug Information

When reporting issues, include:
- Kiro version
- IDE version
- Operating system
- Error messages
- Steps to reproduce
- Relevant configuration files

### Log Locations

```
# Kiro logs (check Kiro output panel)
View → Output → Select "Kiro" from dropdown

# MCP server logs
Check individual server output in MCP panel
```

---

## Common Error Messages

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "Context limit exceeded" | Too much content | Reduce file references |
| "File not found" | Wrong path | Check relative path |
| "Invalid JSON" | Config syntax error | Validate JSON syntax |
| "Server disconnected" | Network/server issue | Restart Kiro |
| "Permission denied" | File access issue | Check permissions |
| "Tool not available" | MCP not configured | Configure MCP server |
| "Pattern not matched" | Wrong glob pattern | Fix pattern syntax |
| "Front matter invalid" | YAML syntax error | Fix YAML format |

---

## Getting Help

### Self-Help Resources
1. This troubleshooting guide
2. Other Kiro guides in `docs/kiro-guide/`
3. Kiro documentation

### Reporting Issues
1. Collect debug information
2. Document steps to reproduce
3. Include error messages
4. Share relevant configuration

### Team Support
- Check if teammates have similar issues
- Share solutions in team documentation
- Update this guide with new solutions

## Summary

Effective troubleshooting follows this pattern:

1. **Identify** - What's the symptom?
2. **Diagnose** - What's the likely cause?
3. **Verify** - Check configuration and logs
4. **Fix** - Apply appropriate solution
5. **Prevent** - Update practices to avoid recurrence

For questions or improvements to this guide, please update this document or discuss with the team.
