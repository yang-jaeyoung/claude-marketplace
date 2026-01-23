# Parallel Validation System

Enhanced review phase with 3-architect parallel validation (inspired by OMC Autopilot).

## Overview

During `/cw:auto` review phase, spawn 3 parallel Reviewer agents for comprehensive validation:

1. **Functional Reviewer**: Verifies all requirements implemented correctly
2. **Security Reviewer**: Checks for vulnerabilities and security issues
3. **Quality Reviewer**: Reviews code maintainability and best practices

All three must return `APPROVED` for the phase to complete.

## Validation Types

### 1. Functional Validation
| Focus | Check |
|-------|-------|
| Requirements | All spec.md requirements implemented |
| Acceptance | All acceptance criteria met |
| Integration | No broken integrations |
| Edge Cases | Edge cases handled |
| Error Handling | Errors handled gracefully |

### 2. Security Validation
| Focus | Check |
|-------|-------|
| Input Validation | All user inputs validated |
| Authentication | Auth flows secure |
| Authorization | Proper access controls |
| Data Protection | Sensitive data protected |
| Dependencies | No known vulnerabilities |
| OWASP Top 10 | Common vulnerabilities checked |

### 3. Quality Validation
| Focus | Check |
|-------|-------|
| Code Style | Follows project conventions |
| Complexity | Acceptable cyclomatic complexity |
| Duplication | No significant code duplication |
| Documentation | Adequate documentation |
| Testing | Sufficient test coverage |
| Maintainability | Easy to understand and modify |

## Implementation

### Task Tool Invocation

```markdown
## Parallel Validation Execution

Spawn 3 Reviewer agents in parallel using Task tool:

### Functional Review
Use Task tool with:
- subagent_type: "cw:Reviewer"
- prompt: "Functional completeness review..."
- model: sonnet

### Security Review
Use Task tool with:
- subagent_type: "cw:Reviewer"
- prompt: "Security vulnerability review..."
- model: sonnet

### Quality Review
Use Task tool with:
- subagent_type: "cw:Reviewer"
- prompt: "Code quality and maintainability review..."
- model: sonnet

All three tasks should be called in a single message for parallel execution.
```

### Prompt Templates

#### Functional Reviewer Prompt
```
## Functional Completeness Review

Review the implemented code for functional completeness.

**Files to Review:** {files_modified}
**Spec:** {spec_path}

**Checklist:**
1. [ ] All P0 requirements from spec.md implemented
2. [ ] All P1 requirements implemented (or justified deferral)
3. [ ] Acceptance criteria verifiable
4. [ ] Edge cases handled per spec
5. [ ] Error scenarios handled
6. [ ] Integration points working

**Output Format:**
```json
{
  "type": "functional",
  "verdict": "APPROVED" | "REJECTED" | "NEEDS_FIX",
  "issues": [
    {
      "severity": "critical" | "major" | "minor",
      "file": "path/to/file.ts",
      "line": 42,
      "description": "Issue description",
      "suggestion": "How to fix"
    }
  ],
  "summary": "Brief summary"
}
```

If all checks pass, output verdict: "APPROVED"
If critical issues found, output verdict: "REJECTED"
If minor issues found, output verdict: "NEEDS_FIX"
```

#### Security Reviewer Prompt
```
## Security Vulnerability Review

Review the implemented code for security issues.

**Files to Review:** {files_modified}

**Checklist:**
1. [ ] Input validation on all user inputs
2. [ ] No SQL/NoSQL injection risks
3. [ ] No XSS vulnerabilities
4. [ ] No command injection risks
5. [ ] Proper authentication checks
6. [ ] Proper authorization checks
7. [ ] Sensitive data not exposed
8. [ ] No hardcoded secrets
9. [ ] Dependencies secure (no known CVEs)
10. [ ] CSRF protection where needed

**Output Format:**
```json
{
  "type": "security",
  "verdict": "APPROVED" | "REJECTED" | "NEEDS_FIX",
  "issues": [...],
  "summary": "Brief summary"
}
```

Any security vulnerability = verdict: "REJECTED"
```

#### Quality Reviewer Prompt
```
## Code Quality Review

Review the implemented code for maintainability and quality.

**Files to Review:** {files_modified}

**Checklist:**
1. [ ] Follows project coding conventions
2. [ ] Reasonable function/method length
3. [ ] Appropriate naming conventions
4. [ ] No significant code duplication
5. [ ] Adequate inline documentation
6. [ ] Cyclomatic complexity acceptable
7. [ ] SOLID principles followed
8. [ ] Test coverage adequate
9. [ ] No dead code
10. [ ] Error messages helpful

**Output Format:**
```json
{
  "type": "quality",
  "verdict": "APPROVED" | "REJECTED" | "NEEDS_FIX",
  "issues": [...],
  "summary": "Brief summary"
}
```
```

## Verdict Aggregation

### Aggregation Logic

```python
def aggregate_verdicts(verdicts: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Aggregate 3 reviewer verdicts.

    Returns:
        (final_verdict, all_issues)
    """
    all_issues = []
    for v in verdicts:
        all_issues.extend(v.get('issues', []))

    # Any REJECTED = final REJECTED
    if any(v['verdict'] == 'REJECTED' for v in verdicts):
        return 'REJECTED', all_issues

    # Any NEEDS_FIX = final NEEDS_FIX
    if any(v['verdict'] == 'NEEDS_FIX' for v in verdicts):
        return 'NEEDS_FIX', all_issues

    # All APPROVED = final APPROVED
    return 'APPROVED', all_issues
```

### State Update

After validation:

```json
{
  "review": {
    "parallel_validation": {
      "enabled": true,
      "architects_spawned": 3,
      "verdicts": [
        {
          "type": "functional",
          "verdict": "APPROVED",
          "issues": [],
          "timestamp": "2024-01-15T10:55:00Z"
        },
        {
          "type": "security",
          "verdict": "NEEDS_FIX",
          "issues": [{"severity": "major", "description": "..."}],
          "timestamp": "2024-01-15T10:55:01Z"
        },
        {
          "type": "quality",
          "verdict": "APPROVED",
          "issues": [],
          "timestamp": "2024-01-15T10:55:02Z"
        }
      ],
      "all_approved": false,
      "validation_rounds": 1
    }
  }
}
```

## Retry Logic

### When REJECTED or NEEDS_FIX

1. Collect all issues from verdicts
2. Auto-fix fixable issues via Fixer agent
3. Re-run parallel validation (max 3 rounds)
4. If still not approved after 3 rounds, prompt user intervention

```markdown
## Validation Retry Flow

Round 1: Initial validation
├─ All APPROVED → Continue to REVIEW_COMPLETE
└─ Not approved → Collect issues

Round 2: Fix and retry
├─ Apply Fixer agent to issues
├─ Re-run parallel validation
├─ All APPROVED → Continue
└─ Not approved → One more round

Round 3: Final attempt
├─ Apply Fixer agent to remaining issues
├─ Re-run parallel validation
├─ All APPROVED → Continue
└─ Not approved → User intervention required
```

## Output File

### `.caw/validation-results.json`

```json
{
  "schema_version": "1.0",
  "task": "Add logout button",
  "timestamp": "2024-01-15T10:55:00Z",
  "rounds": [
    {
      "round": 1,
      "verdicts": [...],
      "final_verdict": "NEEDS_FIX",
      "issues_count": 2
    },
    {
      "round": 2,
      "verdicts": [...],
      "final_verdict": "APPROVED",
      "issues_count": 0
    }
  ],
  "final_result": {
    "verdict": "APPROVED",
    "total_rounds": 2,
    "total_issues_found": 2,
    "total_issues_fixed": 2,
    "remaining_issues": []
  }
}
```

## Integration with auto.md

In `/cw:auto` review phase:

```markdown
### Stage 5: Review (Enhanced with Parallel Validation)

IF config.parallel_validation enabled:
  1. Spawn 3 Reviewer agents in parallel
  2. Wait for all verdicts
  3. Aggregate results
  4. IF all_approved:
       Output REVIEW_COMPLETE signal
     ELSE:
       Transition to fix phase
       After fix, retry validation (max 3 rounds)
       IF still not approved:
         Pause for user intervention

ELSE (single reviewer mode):
  1. Invoke single Reviewer agent
  2. Continue as before
```

## Configuration

Enable/disable in auto-state.json config:

```json
{
  "config": {
    "parallel_validation": true
  }
}
```

Or via command flag:

```bash
/cw:auto "task" --no-parallel-validation
```
