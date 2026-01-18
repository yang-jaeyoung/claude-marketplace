---
description: Validate compliance with project rules, conventions, and workflow requirements
---

# /cw:check - Compliance Check

Validate adherence to project rules, workflow requirements, and code conventions using the ComplianceChecker agent.

## Usage

```bash
/cw:check                # Quick check (workflow + rules)
/cw:check --workflow     # Only task_plan.md structure
/cw:check --rules        # Only CLAUDE.md rules
/cw:check --docs         # Only documentation requirements
/cw:check --conventions  # Only code patterns
/cw:check --all          # Full compliance audit
```

## Behavior

### Step 1: Detect Rule Sources

Scan project for compliance rule sources:

```
Priority order:
1. CLAUDE.md          → Project-specific rules
2. .eslintrc.*        → Linting rules
3. tsconfig.json      → TypeScript config
4. pyproject.toml     → Python config
5. .caw/task_plan.md  → Workflow structure
6. Inferred patterns  → From existing code
```

**Detection Output**:
```
🔍 Rule Sources Detected

📜 CLAUDE.md (12 rules)
📋 .caw/task_plan.md (workflow structure)
🔧 .eslintrc.json (ESLint rules)
📝 tsconfig.json (TypeScript config)

Running compliance check...
```

### Step 2: Invoke ComplianceChecker Agent

Call the ComplianceChecker agent via Task tool:

```markdown
## ComplianceChecker Invocation

**Mode**: [quick | full | focused]
**Focus**: [workflow | rules | docs | conventions | all]

**Rule Sources**:
- CLAUDE.md: [path if exists]
- Lint config: [path if exists]
- task_plan.md: [path if exists]

**Instructions**:
1. Parse all rule sources
2. Check current state against rules
3. Generate compliance report
4. Suggest fixes for violations
```

### Step 3: Display Compliance Report

**Summary Output**:
```
📋 Compliance Check Complete

Status: 🟡 Minor Issues (2 warnings)

┌──────────────────┬────────┬────────┐
│ Category         │ Status │ Issues │
├──────────────────┼────────┼────────┤
│ Project Rules    │ 🟢 Pass │   0    │
│ Workflow         │ 🟡 Warn │   1    │
│ Conventions      │ 🟢 Pass │   0    │
│ Documentation    │ 🟡 Warn │   1    │
└──────────────────┴────────┴────────┘

──────────────────────────────────────────
📜 Project Rules (CLAUDE.md)
──────────────────────────────────────────
✅ All 12 rules passing

──────────────────────────────────────────
📋 Workflow (task_plan.md)
──────────────────────────────────────────
✅ Valid structure (3 phases, 10 steps)
✅ Status icons valid
⚠️ Step 2.3 missing completion notes

──────────────────────────────────────────
📖 Documentation
──────────────────────────────────────────
✅ README.md exists
⚠️ 2 public functions missing JSDoc

──────────────────────────────────────────
✅ Action Items
──────────────────────────────────────────

🟡 Warnings (non-blocking):
  1. Add notes to step 2.3 in .caw/task_plan.md
  2. Add JSDoc to generateToken(), validateToken()

💡 Quick fixes available:
   /cw:fix --workflow   # Fix task_plan.md issues
   /cw:fix --docs       # Generate JSDoc templates
```

## Check Modes

### Quick Check (Default)

```bash
/cw:check
```

- Workflow structure validation
- CLAUDE.md rules check
- Fast execution (~2 seconds)

### Workflow Only

```bash
/cw:check --workflow
```

Validates .caw/task_plan.md:
- Metadata section exists
- Phases properly numbered
- Valid status icons (⏳🔄✅❌⏭️)
- Single step in-progress
- Completion notes present

### Rules Only

```bash
/cw:check --rules
```

Checks CLAUDE.md compliance:
- Naming conventions
- File structure rules
- Forbidden patterns
- Required dependencies

### Documentation Only

```bash
/cw:check --docs
```

Validates documentation:
- Public API has JSDoc/docstrings
- README reflects current state
- Changelog updated for changes
- Migration guide for breaking changes

### Conventions Only

```bash
/cw:check --conventions
```

Checks code patterns:
- Import order consistency
- Error handling patterns
- Logging format
- Test structure

### Full Audit

```bash
/cw:check --all
```

Complete compliance check:
- All categories above
- Cross-reference validation
- Pattern consistency across codebase
- Historical compliance trends

## Compliance Categories

### Project Rules (CLAUDE.md)

| Check | Example |
|-------|---------|
| Naming | `Components use PascalCase` |
| Structure | `Services in src/services/` |
| Forbidden | `No console.log in production` |
| Required | `All APIs must have tests` |

### Workflow (.caw/task_plan.md)

| Check | Requirement |
|-------|-------------|
| Structure | Valid YAML frontmatter |
| Phases | Numbered, with descriptions |
| Steps | Have status, notes when complete |
| Progress | Only one step in-progress |

### Documentation

| Check | Requirement |
|-------|-------------|
| JSDoc | Public functions documented |
| README | Reflects current features |
| Changelog | Updated for releases |
| API docs | Endpoints documented |

### Conventions

| Check | Source |
|-------|--------|
| Imports | Detected from existing files |
| Errors | Error handling pattern |
| Logging | Logger usage pattern |
| Tests | Test file structure |

## Severity Levels

| Icon | Level | Meaning |
|------|-------|---------|
| 🔴 | Error | Must fix - blocks workflow |
| 🟡 | Warning | Should fix - quality issue |
| 🔵 | Info | Consider - suggestion |
| 🟢 | Pass | Compliant |

## Exit Codes

For CI/CD integration:

| Code | Meaning |
|------|---------|
| 0 | All checks pass |
| 1 | Warnings present |
| 2 | Errors present |

## Edge Cases

### No Rule Sources Found

```
ℹ️ No rule sources detected

No CLAUDE.md, lint configs, or .caw/task_plan.md found.

💡 Options:
   • Create CLAUDE.md with project rules
   • /cw:start to create .caw/task_plan.md
   • Run /cw:check --conventions for pattern detection
```

### All Checks Pass

```
🎉 Full Compliance!

All checks passed with no issues.

📊 Summary:
  • Rules checked: 15
  • Files scanned: 23
  • Patterns verified: 8

✅ Ready to commit/deploy
```

### Critical Violations

```
🔴 Critical Violations Found

Cannot proceed until fixed:

1. CLAUDE.md Rule Violation
   Rule: "No secrets in code"
   File: src/config.ts:15
   Found: API_KEY = "sk-..."

2. Workflow Violation
   Rule: "Complete steps must have notes"
   Steps: 2.1, 2.3, 2.4 missing notes in .caw/task_plan.md

💡 Fix violations and re-run:
   /cw:check
```

## Pre-Commit Integration

Add to git hooks for automatic checking:

```bash
# .git/hooks/pre-commit
#!/bin/bash
claude "/cw:check --quick"
if [ $? -ne 0 ]; then
  echo "Compliance check failed. Fix issues before committing."
  exit 1
fi
```

## Integration

- **Reads**: CLAUDE.md, .caw/task_plan.md, lint configs, source files
- **Invokes**: ComplianceChecker agent via Task tool
- **Outputs**: Compliance report with severity levels
- **Suggests**: `/cw:fix`, manual fixes, re-check
