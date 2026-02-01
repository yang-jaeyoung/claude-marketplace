---
description: Validate compliance with project rules, conventions, and workflow requirements
argument-hint: "[--workflow] [--rules] [--all]"
---

# /cw:check - Compliance Check

Validate adherence to project rules, workflow requirements, and code conventions.

## Usage

```bash
/cw:check                # Quick check (workflow + rules)
/cw:check --workflow     # Only task_plan.md structure
/cw:check --rules        # Only CLAUDE.md rules
/cw:check --docs         # Only documentation
/cw:check --conventions  # Only code patterns
/cw:check --all          # Full compliance audit
```

## Workflow

1. **Detect Sources**: CLAUDE.md, .eslintrc, tsconfig.json, task_plan.md
2. **Invoke ComplianceChecker**: Parse rules, check state, generate report
3. **Display Report**: Summary table with issues and fixes

## Check Modes

| Mode | Focus |
|------|-------|
| (default) | Workflow structure + CLAUDE.md rules |
| `--workflow` | task_plan.md: phases, status icons, completion notes |
| `--rules` | CLAUDE.md: naming, structure, forbidden patterns |
| `--docs` | JSDoc, README, changelog |
| `--conventions` | Imports, error handling, logging, tests |
| `--all` | All categories + cross-reference validation |

## Output

```
📋 Compliance Check Complete

Status: 🟡 Minor Issues (2 warnings)

| Category | Status | Issues |
|----------|--------|--------|
| Project Rules | 🟢 Pass | 0 |
| Workflow | 🟡 Warn | 1 |
| Documentation | 🟡 Warn | 1 |

🟡 Warnings:
  1. Add notes to step 2.3 in task_plan.md
  2. Add JSDoc to generateToken()

💡 Quick fixes: /cw:fix --workflow | /cw:fix --docs
```

## Severity Levels

| Icon | Level | Meaning |
|------|-------|---------|
| 🔴 | Error | Must fix - blocks workflow |
| 🟡 | Warning | Should fix - quality issue |
| 🔵 | Info | Consider - suggestion |
| 🟢 | Pass | Compliant |

## Exit Codes (CI/CD)

| Code | Meaning |
|------|---------|
| 0 | All pass |
| 1 | Warnings |
| 2 | Errors |

## Integration

- **Reads**: CLAUDE.md, task_plan.md, lint configs
- **Invokes**: ComplianceChecker agent
- **Suggests**: `/cw:fix`
