---
name: quality-gate
description: Validates quality criteria before marking workflow steps as complete. Use when Builder agent finishes a step to ensure code quality, tests pass, and conventions are followed.
allowed-tools: Read, Bash, Glob, Grep
forked-context: true
forked-context-returns: |
  status: PASSED | FAILED | PASSED_WITH_WARNINGS
  summary: { passed: N, warnings: N, failed: N }
  key_errors: [최대 3개 핵심 에러 메시지]
  action_needed: [다음 단계 제안]
triggers:
  # NOTE: These are CAW internal triggers, NOT Claude Code hooks (hooks.json)
  # Quality Gate is invoked by Builder agent, not by Claude Code hook system
  BuilderComplete:
    action: validate
    required: true
    condition: "requires .caw/ directory"

  # Additional triggers
  ManualRequest:
    action: validate
    required: false
  PhaseTransition:
    action: validate
    required: true
---

# Quality Gate

Automated quality validation before step completion to ensure consistent code quality.

## Triggers

This skill activates when:
1. Builder agent marks a step as complete
2. User runs `/cw:next` and step finishes
3. Manual quality check request
4. Before phase transition

## Quality Checks

### Check Categories

| Category | Weight | Checks |
|----------|--------|--------|
| Code Changes | Required | Files modified, changes exist |
| Compilation | Required | No syntax/type errors |
| Linting | Important | Style rules followed |
| Tidy First | Important | Change type separation (Kent Beck) |
| Tests | Important | Related tests pass |
| Conventions | Recommended | Pattern compliance |

### Check Details

#### 1. Code Changes Verification
```yaml
check: code_changes
required: true
validation:
  - git_diff_exists: true
  - files_modified: > 0
  - no_unintended_changes: true
```

#### 2. Compilation Check
```yaml
check: compilation
required: true
commands:
  typescript: "npx tsc --noEmit"
  javascript: "node --check {files}"
  python: "python -m py_compile {files}"
  go: "go build ./..."
```

#### 3. Lint Check
```yaml
check: linting
required: false  # Warning only
commands:
  typescript: "npx eslint {files}"
  python: "ruff check {files}"
  go: "golangci-lint run"
detection:
  - package.json → eslint
  - pyproject.toml → ruff/flake8
  - .golangci.yml → golangci-lint
```

#### 4. Test Check
```yaml
check: tests
required: true
commands:
  jest: "npx jest --findRelatedTests {files}"
  pytest: "python -m pytest {test_files}"
  go: "go test ./..."
detection:
  - package.json → jest/vitest/mocha
  - pytest.ini → pytest
  - *_test.go → go test
```

#### 5. Convention Check
```yaml
check: conventions
required: false
validations:
  - naming: matches project patterns
  - structure: follows directory conventions
  - imports: consistent with codebase
source: pattern-learner skill
```

#### 6. Tidy First Check (Kent Beck)
```yaml
check: tidy_first
required: true  # For Tidy steps, important for Build steps
validations:
  - step_type_match: changes match declared Type (🧹 or 🔨)
  - no_mixed_changes: structural and behavioral not mixed
  - commit_prefix: matches step type ([tidy] or [feat]/[fix])
source: commit-discipline skill

step_type_detection:
  source: task_plan.md
  table: "Steps" section
  column: Type
  parsing:
    regex: '\| (\d+\.\d+) \| .* \| (🧹 Tidy|🔨 Build) \|'
    current_step: step with Status = "🔄" (in_progress)
  values:
    "🧹 Tidy": tidy
    "🧹": tidy
    "🔨 Build": build
    "🔨": build
  fallback: build  # Default if type cannot be determined
```

**Tidy Step (🧹) Validation:**
```yaml
tidy_step_checks:
  - no_new_exports: true
  - no_new_functions: true
  - no_logic_changes: true
  - tests_unchanged_behavior: tests pass before AND after
  - commit_prefix: "[tidy]"
```

**Build Step (🔨) Validation:**
```yaml
build_step_checks:
  - has_tests: new/modified tests exist
  - no_unrelated_structural: structural changes in target area only
  - commit_prefix: "[feat]" | "[fix]" | "[test]"
```

**Mixed Change Detection:**
```yaml
mixed_change_response:
  detection:
    - structural_indicators AND behavioral_indicators present
  action:
    - status: FAILED
    - message: "Mixed structural and behavioral changes detected"
    - suggestion: "Split into separate [tidy] and [feat] commits"
```

## Behavior

### Step 1: Detect Framework

```
1. Read package.json, pyproject.toml, go.mod
2. Identify test framework
3. Identify linting tools
4. Cache detection results
```

### Step 2: Run Checks

Execute checks in order:

```
1. Code Changes → Required, fail-fast
2. Compilation → Required, fail-fast
3. Linting → Run, collect warnings
4. Tidy First → Required for 🧹, important for 🔨 (early feedback)
5. Tests → Required, fail-fast
6. Conventions → Run, collect warnings
```

> **Note**: Tidy First runs before Tests to provide early feedback on mixed changes,
> avoiding unnecessary test execution when commit discipline is violated.

### Step 3: Aggregate Results

```yaml
result:
  status: PASSED | FAILED | PASSED_WITH_WARNINGS
  checks:
    - name: code_changes
      status: passed
      details: "3 files modified"
    - name: compilation
      status: passed
      details: "TypeScript compiled successfully"
    - name: linting
      status: warning
      details: "2 warnings in auth.ts"
    - name: tests
      status: passed
      details: "5 tests passed"
  summary:
    passed: 4
    warnings: 1
    failed: 0
```

### Step 4: Present Results

**Passed:**
```
✅ Quality Gate: Step 2.3 PASSED

Checks:
  ✅ Code changes: 3 files modified
  ✅ TypeScript: Compiled successfully
  ✅ ESLint: No errors
  ✅ Tests: 5 passed, 0 failed
  ✅ Tidy First: Build step, no mixed changes

Step 2.3 완료로 표시됩니다.
다음 단계로 진행하시겠습니까? [Y/n]
```

**Tidy Step Passed:**
```
✅ Quality Gate: Step 2.0 (🧹 Tidy) PASSED

Checks:
  ✅ Code changes: 2 files modified
  ✅ TypeScript: Compiled successfully
  ✅ Tests: All pass (no behavior change)
  ✅ Tidy First: Structural only, valid [tidy] commit

Step 2.0 완료로 표시됩니다.
Commit: [tidy] Rename auth variables for clarity
```

**Passed with Warnings:**
```
⚠️ Quality Gate: Step 2.3 PASSED (warnings)

Checks:
  ✅ Code changes: 3 files modified
  ✅ TypeScript: Compiled successfully
  ⚠️ ESLint: 2 warnings
     └─ src/auth/jwt.ts:45 - Unused variable 'temp'
     └─ src/auth/jwt.ts:67 - Prefer const over let
  ✅ Tests: 5 passed, 0 failed

경고가 있지만 진행 가능합니다.
[1] 진행 (warnings 무시)
[2] 경고 수정 후 재검증
```

**Failed:**
```
❌ Quality Gate: Step 2.3 FAILED

Checks:
  ✅ Code changes: 3 files modified
  ✅ TypeScript: Compiled successfully
  ✅ ESLint: No errors
  ❌ Tests: 3 passed, 2 failed
     └─ auth.test.ts:23 - Expected token to be valid
     └─ auth.test.ts:45 - Timeout in async operation

테스트 실패로 Step을 완료할 수 없습니다.
실패한 테스트를 수정하시겠습니까? [Y/n]
```

**Mixed Change Failed (Tidy First Violation):**
```
❌ Quality Gate: Step 2.1 FAILED

Checks:
  ✅ Code changes: 3 files modified
  ✅ TypeScript: Compiled successfully
  ✅ ESLint: No errors
  ✅ Tests: 5 passed, 0 failed
  ❌ Tidy First: Mixed changes detected!

⚠️ Tidy First Violation

This commit contains BOTH:

Structural changes:
  • jwt.ts:12 - Renamed `val` → `tokenPayload`
  • jwt.ts:45 - Extracted method `parseHeader()`

Behavioral changes:
  • jwt.ts:78 - Added new `refreshToken()` function
  • jwt.ts:95 - Modified validation logic

Action Required:
1. Split into separate commits:
   [tidy] Rename variables and extract method
   [feat] Add token refresh functionality

2. Or run: /cw:tidy --split

Step을 완료할 수 없습니다.
```

## Framework Detection

### Node.js/TypeScript
```javascript
// Detection from package.json
{
  "scripts": {
    "test": "jest",        // → Jest
    "lint": "eslint .",    // → ESLint
    "typecheck": "tsc"     // → TypeScript
  }
}
```

### Python
```python
# Detection from pyproject.toml
[tool.pytest]  # → pytest
[tool.ruff]    # → ruff
[tool.mypy]    # → mypy
```

### Go
```go
// Detection from file patterns
*_test.go      // → go test
.golangci.yml  // → golangci-lint
```

## Configuration

### `.caw/quality-gate.json` (Optional)

```json
{
  "checks": {
    "code_changes": { "required": true },
    "compilation": { "required": true },
    "linting": { "required": false, "fail_on_warning": false },
    "tests": { "required": true, "coverage_threshold": 80 },
    "conventions": { "required": false }
  },
  "timeout": {
    "compilation": 60,
    "tests": 300,
    "linting": 60
  },
  "skip_patterns": [
    "*.md",
    "*.json",
    "docs/*"
  ]
}
```

## Integration

### With Builder Agent

```markdown
## Builder Workflow with Quality Gate

1. Builder completes implementation
2. Builder calls quality-gate skill
3. If PASSED: Update task_plan.md status
4. If FAILED: Builder attempts fix (max 3 retries)
5. If still FAILED: Report to user
```

### With Progress Tracker

```yaml
on_quality_gate:
  passed:
    - Update step status to completed
    - Record completion time
    - Increment completed_steps count
  failed:
    - Keep step status as in_progress
    - Record failure reason
    - Increment retry_count
```

## Retry Logic

```yaml
retry_policy:
  max_retries: 3
  retry_on:
    - test_failure
    - lint_error
  no_retry_on:
    - compilation_error
    - missing_files
  backoff:
    initial: 0
    strategy: immediate  # Let Builder fix first
```

## Boundaries

**Will:**
- Run automated quality checks
- Provide clear pass/fail feedback
- Suggest fixes for common issues
- Integrate with project's existing tools

**Will Not:**
- Automatically fix code issues
- Skip required checks
- Override user decisions
- Modify source code

## Forked Context Behavior

See [Forked Context Pattern](../../_shared/forked-context.md).

**Returns**: `status: PASSED | FAILED | PASSED_WITH_WARNINGS` with check summary

**Output Examples:**
- `✅ Quality Gate PASSED` - Summary: N passed, M warnings
- `❌ Quality Gate FAILED` - Key errors (max 3) + action needed
- `key_errors: [핵심 에러 최대 3개]` - Focused error list
