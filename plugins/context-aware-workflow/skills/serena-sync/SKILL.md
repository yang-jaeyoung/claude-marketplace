---
name: serena-sync
description: Synchronize CAW workflow state with Serena memory for cross-session knowledge persistence. Enables bidirectional sync between .caw/ files and Serena MCP memory system.
allowed-tools: Read, Write, Glob
mcp_servers:
  - serena
---

# Serena Sync Skill

Bidirectional synchronization between CAW workflow state and Serena MCP memory system for cross-session knowledge persistence.

## Purpose

1. **Persist Knowledge**: Save project insights, domain knowledge, and lessons learned to Serena memory
2. **Restore Context**: Load previously saved knowledge when starting new sessions
3. **Merge Changes**: Handle conflicts when both CAW and Serena have updates

## Memory Schema

| Memory Name | Content | Updated By |
|-------------|---------|------------|
| `project_onboarding` | Project type, frameworks, conventions, key files | Bootstrapper |
| `domain_knowledge` | Business rules, domain concepts, patterns | Planner, Builder |
| `lessons_learned` | Error resolutions, debugging insights, gotchas | Builder |
| `workflow_patterns` | Successful workflow approaches, best practices | Reflect skill |
| `session_backup` | Last session state (optional backup) | Session Persister |

## Operations

### 1. Sync to Serena (`--to-serena`)

Upload CAW knowledge to Serena memory:

```
Source Files → Serena Memory
─────────────────────────────────────────────
.caw/knowledge/**     → domain_knowledge
.caw/insights/**      → caw_insights (persistent marked only)
.caw/learnings.md     → lessons_learned
CLAUDE.md (Lessons)   → lessons_learned (append)
```

**Workflow**:
1. Read all `.caw/knowledge/` files
2. Parse and categorize content
3. Call `write_memory("domain_knowledge", aggregated_content)`
4. Read `.caw/insights/` for persistent-marked insights
5. Call `write_memory("caw_insights", filtered_insights)`
6. Parse CLAUDE.md for Lessons Learned section
7. Call `write_memory("lessons_learned", lessons)`

### 2. Sync from Serena (`--from-serena`)

Restore knowledge from Serena memory:

```
Serena Memory → CAW Files
─────────────────────────────────────────────
project_onboarding  → context_manifest.json (pre-populate)
domain_knowledge    → .caw/knowledge/from_serena.md
lessons_learned     → .caw/learnings.md (merge)
workflow_patterns   → .caw/knowledge/patterns.md
```

**Workflow**:
1. Call `list_memories()` to check available memories
2. For each relevant memory:
   - Call `read_memory(memory_name)`
   - Write to corresponding CAW file
   - Handle merge if file exists
3. Report restored content summary

### 3. Bidirectional Sync (default)

Merge both directions with conflict resolution:

```
1. Read CAW state (timestamps)
2. Read Serena memory metadata
3. Determine which is newer for each category
4. Apply newer_wins strategy
5. Sync both directions
```

### 4. Status Check (`--status`)

Report current sync state:

```markdown
## Serena Sync Status

| Category | CAW | Serena | Sync State |
|----------|-----|--------|------------|
| Domain Knowledge | 2024-01-15 14:30 | 2024-01-14 10:00 | CAW newer |
| Lessons Learned | 2024-01-14 09:00 | 2024-01-15 16:00 | Serena newer |
| Workflow Patterns | Not found | 2024-01-10 08:00 | Serena only |

**Recommendation**: Run `/cw:sync` to synchronize
```

## Conflict Resolution

### Strategy: `newer_wins`

Default strategy - most recent timestamp wins:

```
CAW timestamp > Serena timestamp → Use CAW content
CAW timestamp < Serena timestamp → Use Serena content
CAW timestamp = Serena timestamp → No action needed
```

### Strategy: `merge`

Combine content from both sources:

```
1. Identify unique entries in CAW
2. Identify unique entries in Serena
3. Combine into unified content
4. Write to both destinations
```

### Strategy: `manual`

Ask user to resolve conflicts:

```markdown
## Conflict Detected: domain_knowledge

**CAW Version** (2024-01-15 14:30):
- Rule A: value1
- Rule B: value2

**Serena Version** (2024-01-14 10:00):
- Rule A: different_value
- Rule C: value3

Which version should be used?
1. Keep CAW version
2. Keep Serena version
3. Merge both
```

## Memory Format Templates

### project_onboarding

```markdown
# Project Onboarding

## Basic Info
- **Project Type**: nodejs
- **Root**: .
- **Last Updated**: 2024-01-15T14:30:00Z

## Detected Frameworks
| Name | Version | Category |
|------|---------|----------|
| React | 18.2.0 | frontend |
| TypeScript | 5.3.0 | language |
| Jest | 29.7.0 | testing |

## Conventions
- ESLint + Prettier for code style
- Conventional Commits for git
- Feature branch workflow

## Key Files
- package.json - Dependencies
- tsconfig.json - TypeScript config
- GUIDELINES.md - Project conventions
```

### domain_knowledge

```markdown
# Domain Knowledge

## Business Rules
1. **User Authentication**: JWT tokens with 24h expiry
2. **Data Validation**: Zod schemas for all inputs
3. **Error Handling**: Custom AppError class with codes

## Patterns
- Repository pattern for data access
- Factory pattern for object creation
- Observer pattern for events

## Architecture Decisions
- ADR-001: Use PostgreSQL for primary database
- ADR-002: GraphQL for API layer
```

### lessons_learned

```markdown
# Lessons Learned

## 2024-01-15: JWT Token Refresh Issue

**Problem**: Tokens not refreshing correctly on 401 response
**Cause**: Race condition in token refresh logic
**Solution**: Implemented mutex lock for refresh operation
**Prevention**: Always use atomic operations for auth state

## 2024-01-14: Build Failure on CI

**Problem**: Tests passing locally but failing on CI
**Cause**: Timezone difference in date assertions
**Solution**: Use UTC for all date comparisons
**Prevention**: Add CI environment parity checks
```

### workflow_patterns

```markdown
# Workflow Patterns

## Successful Approaches

### Feature Development
1. Start with failing test
2. Implement minimum code to pass
3. Refactor for clarity
4. Add edge case tests

### Bug Fixing
1. Reproduce in test
2. Identify root cause with debugger
3. Fix with minimal change
4. Add regression test

## Anti-patterns to Avoid
- Skipping tests for "simple" changes
- Large refactors without incremental commits
- Ignoring TypeScript errors with `any`
```

## Integration Points

### With Bootstrapper
- Bootstrapper calls `write_memory("project_onboarding", ...)` after initialization
- On subsequent inits, reads from Serena first

### With Planner
- Planner can call `read_memory("domain_knowledge")` for context
- After planning, can update domain knowledge

### With Builder
- Builder appends to `lessons_learned` after difficult debugging
- Uses existing lessons to avoid repeated mistakes

### With Reflect Skill
- Reflect saves insights to `workflow_patterns`
- Ralph Loop outputs become persistent patterns

## Error Handling

| Scenario | Action |
|----------|--------|
| Serena not available | Fall back to local-only mode, warn user |
| Memory not found | Create new memory with current content |
| Parse error | Log error, skip that memory, continue |
| Write failure | Retry once, then report error |

## Usage Examples

```bash
# Full bidirectional sync
/cw:sync

# Upload CAW knowledge to Serena
/cw:sync --to-serena

# Restore from Serena memory
/cw:sync --from-serena

# Check sync status
/cw:sync --status

# Force overwrite (no merge)
/cw:sync --to-serena --force
```

## Output Format

### Successful Sync

```markdown
## Serena Sync Complete

### Uploaded to Serena
| Memory | Size | Status |
|--------|------|--------|
| domain_knowledge | 2.1 KB | Updated |
| lessons_learned | 1.5 KB | Created |

### Downloaded from Serena
| Memory | Size | Status |
|--------|------|--------|
| workflow_patterns | 3.2 KB | Restored |

**Total**: 3 memories synced
**Duration**: 1.2s
```

### Sync with Conflicts

```markdown
## Serena Sync Complete (with conflicts)

### Resolved Conflicts
| Category | Resolution | Winner |
|----------|------------|--------|
| domain_knowledge | newer_wins | CAW |
| lessons_learned | merge | Both |

### Synced Successfully
- workflow_patterns: Serena → CAW
- project_onboarding: CAW → Serena

**Action Required**: Review merged content in `.caw/learnings.md`
```
