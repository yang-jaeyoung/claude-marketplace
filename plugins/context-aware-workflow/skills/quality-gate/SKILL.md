---
name: quality-gate
description: Validates quality criteria before marking workflow steps as complete
allowed-tools: Read, Bash, Glob, Grep
forked-context: true
forked-context-returns: |
  status: PASSED | FAILED | PASSED_WITH_WARNINGS
  summary: { passed: N, warnings: N, failed: N }
  key_errors: [Max 3 key error messages]
  action_needed: [Next step suggestions]
triggers:
  BuilderComplete: { action: validate, required: true }
  ManualRequest: { action: validate, required: false }
  PhaseTransition: { action: validate, required: true }
---

# Quality Gate

Automated quality validation before step completion.

## Triggers

Activates when: Builder completes step, `/cw:next` finishes, manual request, phase transition

## Quality Checks

| Category | Weight | Checks | Commands |
|----------|--------|--------|----------|
| Code Changes | Required | Files modified, changes exist | `git diff --staged` |
| Compilation | Required | No syntax/type errors | `tsc --noEmit`, `python -m py_compile` |
| Linting | Warning | Style rules | `eslint`, `ruff check`, `golangci-lint` |
| Tidy First | Required | Change type separation | Structural vs behavioral check |
| Tests | Required | Related tests pass | `jest --findRelatedTests`, `pytest` |
| Conventions | Warning | Pattern compliance | pattern-learner skill |

## Tidy First Check (Kent Beck)

```yaml
step_type_detection:
  source: task_plan.md "Steps" section
  values: { "🧹 Tidy": tidy, "🔨 Build": build }

tidy_step: no_new_exports, no_new_functions, no_logic_changes, commit_prefix: "[tidy]"
build_step: has_tests, no_unrelated_structural, commit_prefix: "[feat]|[fix]|[test]"
mixed_change: FAIL → "Split into separate [tidy] and [feat] commits"
```

## Workflow

1. **Detect Framework**: Read package.json/pyproject.toml/go.mod
2. **Run Checks**: Code Changes → Compilation → Linting → Tidy First → Tests → Conventions
3. **Aggregate Results**: PASSED / FAILED / PASSED_WITH_WARNINGS
4. **Present Results**: Show check status and next action

## Result Examples

```
✅ Quality Gate: Step 2.3 PASSED
  ✅ Code changes: 3 files | ✅ TypeScript | ✅ ESLint | ✅ Tests: 5 passed
  → Step marked complete. Proceed? [Y/n]

⚠️ Quality Gate: Step 2.3 PASSED (warnings)
  ⚠️ ESLint: 2 warnings (unused var, prefer const)
  → [1] Proceed | [2] Fix and revalidate

❌ Quality Gate: Step 2.3 FAILED
  ❌ Tests: 2 failed (auth.test.ts:23, auth.test.ts:45)
  → Fix tests? [Y/n]

❌ Quality Gate: Step 2.1 FAILED (Tidy First Violation)
  Mixed changes: structural (rename, extract) + behavioral (new function)
  → Split: /cw:tidy --split or manual separation
```

## Framework Detection

| Language | Config File | Test | Lint | Type Check |
|----------|-------------|------|------|------------|
| TS/JS | package.json | jest/vitest/mocha | eslint | tsc |
| Python | pyproject.toml | pytest | ruff/flake8 | mypy |
| Go | go.mod | go test | golangci-lint | go vet |

## Configuration (`.caw/quality-gate.json`)

```json
{
  "checks": {
    "tests": { "required": true, "coverage_threshold": 80 },
    "linting": { "required": false, "fail_on_warning": false }
  },
  "timeout": { "compilation": 60, "tests": 300 },
  "skip_patterns": ["*.md", "docs/*"]
}
```

## Integration

- **Builder Agent**: PASSED → update plan, FAILED → retry (max 3), still FAILED → report
- **Progress Tracker**: PASSED → record completion, FAILED → record failure, increment retry

## Boundaries

**Will:** Run automated checks, provide pass/fail feedback, suggest fixes, integrate existing tools
**Won't:** Auto-fix code, skip required checks, override user decisions, modify source
