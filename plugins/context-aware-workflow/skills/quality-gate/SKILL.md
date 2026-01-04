---
name: quality-gate
description: Validates quality criteria before marking workflow steps as complete. Use when Builder agent finishes a step to ensure code quality, tests pass, and conventions are followed.
allowed-tools: Read, Bash, Glob, Grep
---

# Quality Gate

Automated quality validation before step completion to ensure consistent code quality.

## Triggers

This skill activates when:
1. Builder agent marks a step as complete
2. User runs `/caw:next` and step finishes
3. Manual quality check request
4. Before phase transition

## Quality Checks

### Check Categories

| Category | Weight | Checks |
|----------|--------|--------|
| Code Changes | Required | Files modified, changes exist |
| Compilation | Required | No syntax/type errors |
| Linting | Important | Style rules followed |
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
4. Tests → Required, fail-fast
5. Conventions → Run, collect warnings
```

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

Step 2.3 완료로 표시됩니다.
다음 단계로 진행하시겠습니까? [Y/n]
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
