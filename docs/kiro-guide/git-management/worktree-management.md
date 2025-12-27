# Multi-Agent Worktree Synchronization Rules

使用一個 share branch 來同步多個 agent 的工作流程。

**Purpose:**
Define a clear workflow for multiple agents working in parallel on different worktrees, using a shared branch for synchronization.

---

### 1. Branch Structure

- **Shared branch:** `share` (or any designated branch)

  - Serves as the central point for synchronizing progress between agents.
  - Should never be rebased. Only merge workbranch commits into it.

- **Workbranches:** `feature/agent-<name>`

  - Each agent works in its own workbranch (own worktree)
  - Rebase is allowed locally to keep commits clean
  - Merge from `share` regularly to stay up-to-date with other agents

---

### 2. Rules

#### [Merge to share branch]

- After completing a task, an agent must merge its workbranch into the shared branch.
- Command example:

```bash
git checkout share
git merge feature/agent-<name>
```

- Purpose: make the agent’s progress available to other agents.

---

#### [Sync from share branch]

- Before starting new work or periodically, an agent must merge the latest changes from the shared branch into its own workbranch.
- Command example:

```bash
git checkout feature/agent-<name>
git merge share
```

- Purpose: keep the agent up-to-date with progress from other agents.

---

### 3. Best Practices

1. **Conflict Resolution:**

   - Resolve any merge conflicts immediately.
   - Communicate if conflicts occur between multiple agents working on the same files.

2. **Branch Naming:**

   - Consistently use `feature/agent-<name>` for workbranches.
   - Use `share` (or a fixed name) for the shared branch.

3. **Rebase Policy:**

   - Allowed only in private workbranches for local history cleanup.
   - Never rebase the shared branch.

4. **CI/CD:**

   - Optional: trigger automated tests when merging to the shared branch to ensure stability.

---

**Summary:**

> The shared branch (`share`) is the central synchronization point.
> Each agent works in its own branch/worktree.
> Merge to share to share progress, merge from share to sync progress from others.
> Rebase is for local cleanup only, conflicts must be resolved immediately.
