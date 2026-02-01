---
description: Review implemented code for quality, best practices, and potential issues
argument-hint: "[path] [--phase N] [--step N.M]"
---

# /cw:review - Code Review

Analyze implemented code for quality and potential issues using the Reviewer agent.

## Usage

```bash
/cw:review                    # Review current phase
/cw:review src/auth/          # Review directory
/cw:review src/auth/jwt.ts    # Review file
/cw:review --phase 2          # Review phase 2
/cw:review --step 2.3         # Review specific step
/cw:review --deep             # Deep analysis (Opus)
/cw:review --focus security   # Focused review
```

## Scope Detection

| Argument | Scope |
|----------|-------|
| (none) | Files from most recent completed phase |
| `path` | Specific file or directory |
| `--phase N` | All files modified in phase N |
| `--step N.M` | Files from specific step |
| `--all` | All files in task_plan.md |

## Review Modes

| Mode | Depth | Agent |
|------|-------|-------|
| Standard | Blocking issues | cw:Reviewer (Sonnet) |
| Deep (`--deep`) | Thorough analysis | cw:reviewer-opus |
| Focused (`--focus`) | Specific concern | Specialized |

## Review Categories

| Category | Checks |
|----------|--------|
| **Correctness** | Logic errors, edge cases, test coverage |
| **Code Quality** | Naming, organization, readability |
| **Best Practices** | Idioms, patterns, error handling |
| **Security** | Input validation, auth checks, sanitization |
| **Performance** | Algorithm efficiency, resource usage |

## Severity Levels

| Icon | Level | Meaning |
|------|-------|---------|
| 🔴 | Critical | Must fix - bugs, security |
| 🟠 | Major | Should fix - significant |
| 🟡 | Minor | Consider - improvements |
| 🟢 | Suggestion | Optional - nice to have |

## Output

```
📋 Code Review Complete

Files reviewed: 3 | Time: 15s

| Category | Score | Issues |
|----------|-------|--------|
| Correctness | 🟢 Good | 0 |
| Code Quality | 🟡 Fair | 2 |
| Security | 🟢 Good | 0 |

Overall: 🟢 Approved with suggestions

📄 src/auth/jwt.ts
  🟢 Clean token generation logic
  🟡 Line 45: Extract magic number
  🟡 Line 78: Batch DB queries

💡 Next: /cw:fix or /cw:next
```

## Workflow Integration

```
/cw:next (Implement) → /cw:review (Check)
                            ↓
                    Pass: Next step
                    Fail: Fix & re-review
```

## Integration

- **Reads**: task_plan.md, source files, config files
- **Invokes**: Reviewer agent via Task tool
- **Updates**: task_plan.md with review notes
- **Suggests**: `/cw:fix`, `/cw:next`
