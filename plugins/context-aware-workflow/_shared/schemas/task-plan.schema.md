# Task Plan Schema

Location: `.caw/task_plan.md`

## Structure

```markdown
# Task Plan: [Title]

## Metadata
| Field | Value |
|-------|-------|
| **Created** | [timestamp] |
| **Source** | User request / Plan Mode import |
| **Status** | Planning / In Progress / Complete |
| **Methodology** | Tidy First (Kent Beck) |

## Context Files
### Active Context
| File | Reason | Status |
|------|--------|--------|
| `path/file` | [reason] | 📝 Edit / 👁️ Read |

### Project Context (Read-Only)
- `GUIDELINES.md`
- `package.json`

## Task Summary
[2-3 sentence summary]

## Execution Phases

### Phase N: [Name]
**Phase Deps**: - | phase N | phase N, M

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| N.0 | [structural prep] | 🧹 Tidy | ⏳ | Builder | - | |
| N.1 | [behavioral change] | 🔨 Build | ⏳ | Builder | N.0 | |

## Validation Checklist
- [ ] Tests pass
- [ ] Follows conventions
- [ ] Tidy commits separate from Build commits

## Open Questions
- [Unresolved items]
```

## Phase Dependency Notation

### Phase-Level Dependencies (Phase Deps)

Specifies dependencies between Phases. Predecessor Phases must complete before starting the dependent Phase.

| Notation | Meaning | Example |
|----------|---------|---------|
| `-` | Independent, can start immediately | Phase 1 (Setup) |
| `phase N` | Starts after Phase N completes | `phase 1` |
| `phase N, M` | Starts after both Phase N and M complete | `phase 2, 3` |

**Determining Parallel Execution**:
- Phases with identical Phase Deps can run in parallel
- Example: Phase 2 (`phase 1`), Phase 3 (`phase 1`) → **Parallel possible**

### Step-Level Dependencies (Deps Column)

Specifies dependencies between Steps.

| Notation | Meaning | Example |
|----------|---------|---------|
| `-` | Independent, can execute immediately when Phase starts | |
| `N.M` | Execute after specific Step completes | `2.1` |
| `N.M, N.K` | Execute after multiple Steps complete | `2.1, 2.3` |
| `N.*` | Execute after entire Phase N completes | `1.*` |
| `!N.M` | Cannot run concurrently with Step N.M (mutual exclusion) | `!2.3` |

## Step Type Column (Tidy First)

All Steps must specify their Type according to Kent Beck's Tidy First methodology.

| Icon | Type | Description | Commit Prefix |
|------|------|-------------|---------------|
| 🧹 | Tidy | Structural changes (no behavior change) | `[tidy]` |
| 🔨 | Build | Behavioral changes (new features, bug fixes) | `[feat]`, `[fix]` |
| 🔧 | Refactor | Mixed changes (avoid if possible) | `[refactor]` |

### Tidy First Principles

1. **Structural changes first**: Clean up code before behavior changes
2. **Separate commits**: Never mix Tidy and Build commits
3. **Small units**: Each change should be minimal

### Tidy Step Examples

| Task | Type | Description |
|------|------|-------------|
| Rename variables/functions | 🧹 Tidy | Clearer naming |
| Extract method | 🧹 Tidy | Separate duplicate code |
| Reorganize files | 🧹 Tidy | Directory cleanup |
| Remove unused code | 🧹 Tidy | Delete dead code |
| Make dependencies explicit | 🧹 Tidy | Expose implicit dependencies |

### Build Step Examples

| Task | Type | Description |
|------|------|-------------|
| Add new function | 🔨 Build | New feature |
| Modify logic | 🔨 Build | Behavior change |
| Fix bug | 🔨 Build | Defect fix |
| Add tests | 🔨 Build | New test cases |

### Step Order Rules

```
Phase N:
  N.0 [Tidy] Structural cleanup  ─┐
  N.1 [Tidy] Refactoring         ─┼─ Tidy first
  N.2 [Build] Feature impl       ─┤
  N.3 [Build] Tests              ─┘ Build later
```

## Status Icons

| Icon | Status | Description |
|------|--------|-------------|
| ⏳ | Pending | Waiting to execute |
| 🔄 | In Progress | Currently executing |
| ✅ | Complete | Completed |
| ❌ | Blocked | Blocked (dependency not met or error) |
| ⏭️ | Skipped | Skipped |
| 🌳 | In Worktree | Working in separate worktree |

## Agent Column

| Value | Description |
|-------|-------------|
| Builder | Default implementation agent |
| Builder-Haiku | Lightweight agent for simple tasks |
| Builder-Opus | Advanced agent for complex tasks |
| Reviewer | Code review agent |

## Example: Full Task Plan (Tidy First)

```markdown
# Task Plan: User Authentication System

## Metadata
| Field | Value |
|-------|-------|
| **Created** | 2026-01-16 10:00 |
| **Source** | User request |
| **Status** | In Progress |
| **Methodology** | Tidy First (Kent Beck) |

## Context Files
### Active Context
| File | Reason | Status |
|------|--------|--------|
| `src/auth/jwt.ts` | JWT utility implementation | 📝 Edit |
| `src/middleware/auth.ts` | Auth middleware | 📝 Edit |

### Project Context (Read-Only)
- `package.json`
- `tsconfig.json`

## Task Summary
Implement JWT-based user authentication system. Following Tidy First methodology, structural cleanup precedes feature implementation.

## Execution Phases

### Phase 1: Setup
**Phase Deps**: -

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 1.1 | Install dependencies (jsonwebtoken, bcrypt) | 🔨 Build | ✅ | Builder | - | |
| 1.2 | Add type definitions | 🔨 Build | ✅ | Builder | - | ⚡ Parallel with 1.1 |
| 1.3 | Set up test fixtures | 🔨 Build | ✅ | Builder | - | ⚡ Parallel possible |

### Phase 2: Core Implementation
**Phase Deps**: phase 1

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 2.0 | Clean up existing auth code | 🧹 Tidy | ✅ | Builder | - | Naming improvements |
| 2.1 | Implement JWT utility functions | 🔨 Build | 🔄 | Builder | 2.0 | |
| 2.2 | Token generation function | 🔨 Build | ⏳ | Builder | 2.1 | |
| 2.3 | Token validation function | 🔨 Build | ⏳ | Builder | 2.1 | ⚡ Parallel with 2.2 |
| 2.4 | Auth middleware | 🔨 Build | ⏳ | Builder | 2.2, 2.3 | |

### Phase 3: API Layer
**Phase Deps**: phase 1

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 3.0 | User model refactoring | 🧹 Tidy | ⏳ | Builder | - | Normalize field names |
| 3.1 | Extend User model | 🔨 Build | ⏳ | Builder | 3.0 | |
| 3.2 | Password hashing utility | 🔨 Build | ⏳ | Builder | 3.0 | ⚡ Parallel with 3.1 |
| 3.3 | Registration endpoint | 🔨 Build | ⏳ | Builder | 3.1, 3.2 | |

### Phase 4: Integration
**Phase Deps**: phase 2, phase 3

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 4.1 | Login endpoint | 🔨 Build | ⏳ | Builder | - | |
| 4.2 | Apply auth route protection | 🔨 Build | ⏳ | Builder | 4.1 | |
| 4.3 | Integration tests | 🔨 Build | ⏳ | Builder | 4.2 | |

## Validation Checklist
- [ ] All tests pass
- [ ] Follows project conventions
- [ ] Security review complete
- [ ] Tidy/Build commits separated

## Open Questions
- Token expiration time setting?
```

## Parallel Execution Analysis

Parallel execution combinations in the example above:

### Phase Parallel
- Phase 2 and Phase 3: Both only depend on `phase 1` → **Parallel possible**

### Step Parallel (within Phase 1)
- Step 1.1, 1.2, 1.3: All `-` (independent) → **Parallel possible**

### Step Parallel (within Phase 2)
- Step 2.2, 2.3: Both only depend on `2.1` → **Parallel possible**

### Worktree Usage Example

```bash
# After Phase 1 completes

# Terminal 1 (main)
/cw:next --worktree phase 2

# Terminal 2
/cw:next --worktree phase 3

# In each worktree
cd .worktrees/phase-2 && claude
/cw:next --parallel phase 2  # Run 2.2, 2.3 in parallel

# After completion, from main
/cw:merge --all
```
