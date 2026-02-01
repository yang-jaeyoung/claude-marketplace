---
description: Run automated Review-Fix cycles until quality criteria are met
argument-hint: "[--step N.M] [--max-cycles N] [--severity minor|major|critical]"
---

# /cw:qaloop - Quality Assurance Loop

Automated build → review → fix cycle that continues until quality criteria are satisfied or max cycles reached.

## Usage

```bash
# Basic usage - QA current step
/cw:qaloop

# QA specific step
/cw:qaloop --step 2.3

# QA entire phase
/cw:qaloop --phase 2

# Custom settings
/cw:qaloop --max-cycles 5 --severity major
/cw:qaloop --step 1.1 --max-cycles 3 --exit-on critical
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--step N.M` | Current | Target specific step for QA |
| `--phase N` | - | Run QA on entire phase |
| `--max-cycles` | 3 | Maximum review-fix iterations |
| `--severity` | major | Minimum severity to fix (minor/major/critical) |
| `--exit-on` | major | Exit when no issues at this severity |
| `--no-build` | false | Skip build step (review only) |
| `--continue` | false | Resume from saved state |

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   BUILD     │ ──► │   REVIEW    │ ──► │    FIX      │ ──► │ EXIT CHECK   │
│  (Execute)  │     │ (Analyze)   │     │ (Correct)   │     │              │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬───────┘
      ▲                                                            │
      │                                                            │
      └──────────────────── Issues remain? ────────────────────────┘

Exit Conditions:
✅ No critical/major issues (review passed)
⏱️ Max cycles reached
🔁 Same issues 3 times (stalled)
❌ Build failure persists
```

## Agent Selection

### Standard Mode

```
Build Phase:    cw:Builder (Sonnet) - Standard build
Diagnose:       cw:Reviewer (Sonnet) - Review with diagnosis
Fix:            cw:Fixer (Sonnet) - Targeted fixing
```

### Deep Mode (--deep)

```
Build Phase:    cw:Builder (Sonnet) - Standard build
Diagnose:       cw:reviewer-opus (Opus) - Deep root cause analysis
Fix:            cw:Fixer (Opus) - Comprehensive fixing
```

## Execution Flow

### Phase 1: Initialization

```
[1] Check prerequisites
    ├─ .caw/task_plan.md exists?
    ├─ Target step/phase valid?
    └─ Previous qaloop_state.json?

[2] Initialize state
    {
      "qaloop_id": "qa_YYYYMMDD_HHMMSS",
      "status": "running",
      "target": { "type": "step", "id": "2.3" },
      "config": {
        "max_cycles": 3,
        "exit_severity": "major"
      }
    }

[3] Select agents based on mode
    build_agent = "cw:Builder"
    diagnose_agent = "cw:Reviewer" or "cw:reviewer-opus" (--deep)
    fix_agent = "cw:Fixer"
```

### Phase 2: QA Cycle

```
WHILE cycle_number <= max_cycles AND status == "running":

  [BUILD]
  ────────────────────────────────────────────────
  Invoke build_agent:
    "Execute step [target] and run tests/build"

  IF build_failed:
    Record build error
    IF same_error_3_times:
      status = "stalled"
      EXIT
    CONTINUE to next cycle

  [REVIEW]
  ────────────────────────────────────────────────
  Invoke diagnose_agent:
    "Review implementation for:
     - Correctness issues
     - Code quality problems
     - Security vulnerabilities
     - Performance concerns

     Categorize by severity: critical, major, minor"

  Parse review results:
    critical_issues = [...]
    major_issues = [...]
    minor_issues = [...]

  [EXIT CHECK]
  ────────────────────────────────────────────────
  IF no issues at exit_severity or higher:
    status = "passed"
    EXIT

  IF all issues are same as previous cycle:
    stall_count += 1
    IF stall_count >= 3:
      status = "stalled"
      EXIT

  [FIX]
  ────────────────────────────────────────────────
  Filter issues by severity >= config.severity

  FOR each fixable_issue:
    Invoke fix_agent:
      "Fix issue: [issue_description]
       File: [file_path]
       Line: [line_number]"

    Record fix attempt

  [RECORD]
  ────────────────────────────────────────────────
  cycles.append({
    "number": cycle_number,
    "build_result": "success" | "failed",
    "review_result": {
      "critical": count,
      "major": count,
      "minor": count
    },
    "fixes_applied": count,
    "issue_hashes": [...for stall detection]
  })

  cycle_number += 1
```

### Phase 3: Completion

```
[1] Generate summary
    - Total cycles run
    - Issues found/fixed
    - Remaining issues
    - Exit reason

[2] Update state file
    qaloop_state.status = final_status
    qaloop_state.completed_at = now()

[3] Display report
```

## Stall Detection

The loop detects when the same issues keep reappearing:

```markdown
## Issue Hashing

Each issue generates a hash from:
  hash = md5(file_path + line_range + issue_type + severity)

## Stall Detection Logic

IF current_cycle.issue_hashes == previous_cycle.issue_hashes:
  stall_count += 1

IF stall_count >= 3:
  status = "stalled"
  message = "Same issues detected 3 times. Manual intervention needed."
```

## Progress Display

### Standard Output

```
🔄 /cw:qaloop --step 2.3

Cycle 1/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ⚠️ 2 major, 1 minor
  🔧 Fixing...    ✅ 2 fixed

Cycle 2/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ✅ 0 major, 1 minor

✅ QA Loop Complete

📊 Summary:
  • Cycles: 2 / 3
  • Issues found: 3 (2 critical, 1 minor)
  • Issues fixed: 2
  • Remaining: 1 minor (below threshold)
  • Exit reason: No major issues

💡 Next steps:
   /cw:next to continue
   /cw:review --deep for thorough check
```

### Stalled Output

```
🔄 /cw:qaloop --step 2.3

Cycle 1/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ⚠️ 1 major
  🔧 Fixing...    ✅ 1 fixed

Cycle 2/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ⚠️ 1 major (same issue)
  🔧 Fixing...    ✅ 1 fixed

Cycle 3/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ⚠️ 1 major (same issue)

⚠️ QA Loop Stalled

The same issue keeps reappearing:
  📍 src/auth/jwt.ts:45
     "Token validation logic incomplete"

This may require manual intervention or architectural change.

💡 Options:
   1. Fix manually and run /cw:qaloop --continue
   2. Skip with /cw:next --skip-qa
   3. Get help with /cw:diagnose
```

## State File

### `.caw/qaloop_state.json`

```json
{
  "schema_version": "1.0",
  "qaloop_id": "qa_20240115_103045",
  "status": "running",
  "started_at": "2024-01-15T10:30:45Z",
  "target": {
    "type": "step",
    "id": "2.3",
    "description": "Implement JWT validation"
  },
  "config": {
    "max_cycles": 3,
    "severity_threshold": "major",
    "exit_severity": "major"
  },
  "environment": {
    "agents_used": {
      "build": "cw:Builder",
      "diagnose": "cw:Reviewer",
      "fix": "cw:Fixer"
    }
  },
  "current_cycle": 2,
  "stall_count": 0,
  "cycles": [
    {
      "number": 1,
      "started_at": "2024-01-15T10:30:46Z",
      "completed_at": "2024-01-15T10:32:15Z",
      "build_result": {
        "status": "success",
        "output_summary": "Build completed, 15 tests passed"
      },
      "review_result": {
        "critical": 0,
        "major": 2,
        "minor": 1,
        "issues": [
          {
            "id": "issue_001",
            "severity": "major",
            "file": "src/auth/jwt.ts",
            "line": 45,
            "description": "Token validation missing edge case",
            "hash": "abc123"
          }
        ]
      },
      "fixes_applied": 2,
      "issue_hashes": ["abc123", "def456", "ghi789"]
    }
  ],
  "summary": {
    "total_issues_found": 3,
    "total_issues_fixed": 2,
    "remaining_issues": 1,
    "exit_reason": null
  }
}
```

## Integration with Other Commands

### With /cw:loop

```bash
# QA after each step in loop
/cw:loop "Implement auth" --qa-each-step
```

### With /cw:auto

```bash
# Auto mode includes QA by default
/cw:auto "Add feature"
# Internally runs qaloop after build steps
```

### With /cw:next

```bash
# Run QA after next step
/cw:next && /cw:qaloop
```

## Best Practices

1. **Set appropriate severity**
   - Use `--severity critical` for fast iterations
   - Use `--severity minor` for thorough QA

2. **Monitor for stalls**
   - Stalls indicate design issues
   - Consider `/cw:diagnose` for deep analysis

3. **Use with worktrees**
   - Run QA in worktree for isolation
   - Merge only after QA passes

4. **Integrate in CI**
   - Run qaloop as CI step
   - Fail builds on QA failure

## Comparison with Other Commands

| Feature | /cw:qaloop | /cw:loop | /cw:review |
|---------|------------|----------|------------|
| Purpose | Quality gates | Task completion | One-time review |
| Iteration | Review-Fix cycles | Build iterations | Single pass |
| Auto-fix | ✅ Yes | ✅ Optional | ❌ No |
| Stall detection | ✅ Yes | ✅ Yes | ❌ N/A |
| Best for | Quality assurance | Task execution | Manual review |

## Related Documentation

- [Model Routing](../_shared/model-routing.md) - Agent tier selection
- [Loop Command](./loop.md) - Autonomous execution
- [Review Command](./review.md) - Manual review
