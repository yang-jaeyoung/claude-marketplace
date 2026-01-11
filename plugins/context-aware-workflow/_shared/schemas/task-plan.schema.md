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
| # | Step | Status | Notes |
|---|------|--------|-------|
| N.1 | [description] | ⏳/🔄/✅/❌ | |

## Validation Checklist
- [ ] Tests pass
- [ ] Follows conventions

## Open Questions
- [Unresolved items]
```
