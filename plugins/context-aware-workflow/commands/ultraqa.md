---
description: Advanced automated QA with intelligent diagnosis and targeted fixes
argument-hint: "[--target build|test|lint|all] [--max-cycles N] [--deep]"
---

# /cw:ultraqa - Ultra Quality Assurance

Advanced QA automation that intelligently diagnoses build/test/lint failures and applies targeted fixes. Uses tiered agents for root cause analysis based on complexity.

## Usage

```bash
# Basic - auto-detect and fix all issues
/cw:ultraqa

# Target specific issue type
/cw:ultraqa --target build      # Fix build errors
/cw:ultraqa --target test       # Fix failing tests
/cw:ultraqa --target lint       # Fix linting issues
/cw:ultraqa --target all        # Fix everything (default)

# Deep diagnosis mode
/cw:ultraqa --deep              # Use Opus for thorough analysis

# Custom settings
/cw:ultraqa --max-cycles 5 --target test
/cw:ultraqa --continue          # Resume from previous state
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--target` | all | Target type: build, test, lint, or all |
| `--max-cycles` | 5 | Maximum fix attempts |
| `--deep` | false | Enable deep diagnosis (uses Opus) |
| `--continue` | false | Resume from saved state |
| `--verbose` | false | Show detailed diagnosis |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ULTRAQA WORKFLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [1] DETECT           [2] DIAGNOSE         [3] FIX              │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐          │
│   │ Run Build│   ───► │ Analyze  │   ───► │ Apply    │          │
│   │ Run Tests│        │ Root     │        │ Targeted │          │
│   │ Run Lint │        │ Cause    │        │ Fix      │          │
│   └──────────┘        └──────────┘        └──────────┘          │
│        │                   │                   │                 │
│        ▼                   ▼                   ▼                 │
│   Error Output       Diagnosis Report     Fix Applied            │
│                                                                  │
│   [4] VERIFY ◄───────────────────────────────────────────────   │
│   ┌──────────┐                                                   │
│   │ Re-run   │  ───► Pass? ───► COMPLETE                        │
│   │ Failed   │           │                                       │
│   │ Command  │           └───► More issues? ───► Loop            │
│   └──────────┘                                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Selection Strategy

### Standard Mode

```
Diagnose Phase:
  Agent: cw:reviewer-opus (Opus)
  Capabilities:
    ✅ Root cause analysis
    ✅ Error pattern matching
    ✅ Fix suggestions

Fix Phase:
  Agent: cw:Fixer (Opus)
  Capabilities:
    ✅ Targeted fixes
    ✅ Multi-file refactoring
    ✅ Test-aware modifications
```

### Deep Mode (--deep)

```
Diagnose Phase:
  Agent: cw:architect (Opus)
  Capabilities:
    ✅ Deep root cause analysis
    ✅ Cross-file dependency tracking
    ✅ Pattern recognition across errors
    ✅ Intelligent fix suggestions

Fix Phase:
  Agent: cw:Fixer (Opus)
  Capabilities:
    ✅ Comprehensive fixes
    ✅ Architectural improvements
    ✅ Security-aware modifications
```

## Detection Phase

### Build Error Detection

```bash
# Run project build command
detect_build_command()  # npm run build, cargo build, go build, etc.
execute_and_capture_output()

# Parse error output
errors = parse_build_errors(output)
# Returns: [{file, line, error_type, message}]
```

### Test Failure Detection

```bash
# Run test suite
detect_test_command()  # npm test, pytest, cargo test, etc.
execute_and_capture_output()

# Parse test results
failures = parse_test_failures(output)
# Returns: [{test_name, file, assertion, expected, actual}]
```

### Lint Issue Detection

```bash
# Run linter
detect_lint_command()  # eslint, pylint, clippy, etc.
execute_and_capture_output()

# Parse lint output
issues = parse_lint_issues(output)
# Returns: [{file, line, rule, severity, message}]
```

## Diagnosis Phase

### Diagnosis Prompt

```markdown
## Root Cause Analysis

Analyze the following errors and provide root cause analysis:

**Build Errors:**
[error_list]

**Context:**
- Project type: [detected_type]
- Files involved: [file_list]
- Recent changes: [git_diff_summary]

**Required Analysis:**
1. Root cause identification
2. Dependency chain analysis
3. Fix priority ordering
4. Potential side effects
5. Recommended fix approach

Output structured diagnosis report.
```

## Fix Phase

### Fix Strategy by Type

#### Build Errors

```
Priority: High
Strategy:
  1. Type errors → Add/fix type annotations
  2. Import errors → Add missing imports, fix paths
  3. Syntax errors → Fix syntax issues
  4. Missing dependencies → Add to package.json/Cargo.toml/etc.
```

#### Test Failures

```
Priority: Medium
Strategy:
  1. Assertion failures → Fix implementation or update expectations
  2. Setup failures → Fix test configuration
  3. Timeout failures → Optimize or increase timeout
  4. Mock failures → Update mock data
```

#### Lint Issues

```
Priority: Low
Strategy:
  1. Auto-fixable → Run lint --fix
  2. Style issues → Apply formatting
  3. Code smell → Refactor per suggestion
  4. Complexity → Split functions/simplify
```

## Progress Display

### Standard Output

```
🔬 /cw:ultraqa --target all

Detecting issues...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Build:  ❌ 3 errors
🧪 Tests:  ⚠️ 2 failures
📝 Lint:   ⚠️ 5 issues
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cycle 1/5 ━━━━━━━━━━━━━━━━━━━━
  🔍 Diagnosing with cw:reviewer-opus...

  📋 Root Cause Analysis:
  ┌────────────────────────────────────────────────
  │ Build Error #1: Missing type export
  │   Root: UserType not exported from types.ts
  │   Impact: 2 dependent files fail
  │   Fix: Export UserType from types.ts:15
  │
  │ Build Error #2: Import path incorrect
  │   Root: utils.ts moved to src/lib/
  │   Impact: 1 file affected
  │   Fix: Update import in auth.ts:3
  └────────────────────────────────────────────────

  🔧 Applying fixes...
      ✅ types.ts: Added export
      ✅ auth.ts: Fixed import path

  🔄 Verifying...
      📦 Build: ✅ Success
      🧪 Tests: ⚠️ 2 failures (unchanged)

Cycle 2/5 ━━━━━━━━━━━━━━━━━━━━
  🔍 Diagnosing test failures...

  📋 Analysis:
  ┌────────────────────────────────────────────────
  │ Test: "should validate user input"
  │   Root: Validation regex updated, test not
  │   Fix: Update test expectation
  │
  │ Test: "should handle empty array"
  │   Root: Edge case not handled in code
  │   Fix: Add empty array check in handler.ts
  └────────────────────────────────────────────────

  🔧 Applying fixes...
      ✅ handler.ts: Added edge case
      ✅ handler.test.ts: Updated expectation

  🔄 Verifying...
      🧪 Tests: ✅ All passing

Cycle 3/5 ━━━━━━━━━━━━━━━━━━━━
  📝 Running lint --fix...
      ✅ 4 auto-fixed
      ⚠️ 1 requires manual fix

✅ UltraQA Complete

📊 Summary:
  • Cycles: 3 / 5
  • Build errors: 3 → 0 ✅
  • Test failures: 2 → 0 ✅
  • Lint issues: 5 → 1 ⚠️

⚠️ Remaining issue (manual fix needed):
  📍 src/utils.ts:42
     "Function has too many parameters (6 > 4)"
     Suggestion: Consider using options object pattern

💡 Next: /cw:review to verify changes
```

## State File

### `.caw/ultraqa_state.json`

```json
{
  "schema_version": "1.0",
  "ultraqa_id": "uqa_20240115_103045",
  "status": "running",
  "started_at": "2024-01-15T10:30:45Z",
  "config": {
    "target": "all",
    "max_cycles": 5,
    "deep_mode": true
  },
  "environment": {
    "project_type": "typescript",
    "build_command": "npm run build",
    "test_command": "npm test",
    "lint_command": "npm run lint"
  },
  "initial_state": {
    "build_errors": 3,
    "test_failures": 2,
    "lint_issues": 5
  },
  "current_cycle": 3,
  "cycles": [
    {
      "number": 1,
      "target": "build",
      "diagnosis": { ... },
      "fixes_applied": 2,
      "result": {
        "build_errors": 0,
        "test_failures": 2,
        "lint_issues": 5
      }
    }
  ],
  "final_state": {
    "build_errors": 0,
    "test_failures": 0,
    "lint_issues": 1
  },
  "summary": {
    "total_fixed": 9,
    "remaining": 1,
    "exit_reason": "all_major_fixed"
  }
}
```

## Comparison with qaloop

| Feature | /cw:ultraqa | /cw:qaloop |
|---------|-------------|------------|
| Focus | Specific error types | Code quality |
| Targets | Build/Test/Lint | Any review issue |
| Diagnosis | Deep root cause | Standard review |
| Best for | CI failures | Quality gates |

## Integration

### With CI/CD

```yaml
# GitHub Actions example
- name: Run UltraQA
  run: |
    claude code /cw:ultraqa --target all --max-cycles 3
```

### With Other Commands

```bash
# After implementation
/cw:next phase 1
/cw:ultraqa --target build

# Before merge
/cw:ultraqa --target all --deep
/cw:review
```

## Best Practices

1. **Run early, run often**
   - Run after each major change
   - Catch issues before they compound

2. **Target appropriately**
   - Use `--target build` for quick fixes
   - Use `--target all` before commits

3. **Use deep mode for complex issues**
   - When standard mode fails
   - For architectural problems

4. **Check fallback warnings**
   - Use --deep for thorough analysis
   - Understand limitations

## Related Documentation

- [Model Routing](../_shared/model-routing.md) - Agent selection
- [QA Loop](./qaloop.md) - Quality assurance loop
- [Review Command](./review.md) - Manual review
