---
description: Review implemented code for quality, best practices, and potential issues
---

# /cw:review - Code Review

Analyze implemented code for quality, adherence to best practices, and potential issues using the Reviewer agent.

## Usage

```bash
/cw:review                    # Review recent changes (current phase)
/cw:review src/auth/          # Review specific directory
/cw:review src/auth/jwt.ts    # Review specific file
/cw:review --phase 2          # Review all changes from phase 2
/cw:review --step 2.3         # Review changes from specific step
/cw:review --all              # Review entire implementation
```

## Behavior

### Step 1: Determine Review Scope

Based on arguments, identify files to review:

| Argument | Scope |
|----------|-------|
| (none) | Files from most recent completed phase |
| `path` | Specific file or directory |
| `--phase N` | All files modified in phase N |
| `--step N.M` | Files from specific step |
| `--all` | All files mentioned in .caw/task_plan.md |

### Step 2: Validate Scope

1. Check for `.caw/task_plan.md` existence
2. If not found:

```
⚠️ No active workflow

.caw/task_plan.md not found. Cannot determine review scope.

💡 Options:
   • /cw:review <path> to review specific files
   • /cw:start to begin a workflow first
```

3. Verify files exist and are readable

### Step 3: Gather Context

Before invoking Reviewer, collect:

```
• .caw/task_plan.md requirements for context
• Project configuration files (.eslintrc, tsconfig.json, etc.)
• Existing test files for coverage analysis
• CLAUDE.md or project conventions
```

### Step 4: Invoke Reviewer Agent

Call the Reviewer agent via Task tool:

```markdown
## Reviewer Agent Invocation

**Scope**: [Files/directories to review]

**Context**:
- Phase: [Phase number]
- Requirements: [Extracted from task_plan.md]
- Conventions: [From project config files]

**Instructions**:
1. Analyze each file for quality issues
2. Check adherence to project conventions
3. Identify potential bugs and security issues
4. Generate structured review report
```

### Step 5: Display Review Report

**Summary Output**:
```
📋 Code Review Complete

Files reviewed: 3
Time: 15 seconds

┌─────────────────┬────────┬────────┐
│ Category        │ Score  │ Issues │
├─────────────────┼────────┼────────┤
│ Correctness     │ 🟢 Good │   0    │
│ Code Quality    │ 🟡 Fair │   2    │
│ Best Practices  │ 🟢 Good │   1    │
│ Security        │ 🟢 Good │   0    │
│ Performance     │ 🟡 Fair │   1    │
└─────────────────┴────────┴────────┘

Overall: 🟢 Approved with suggestions

──────────────────────────────────────────
📄 src/auth/jwt.ts
──────────────────────────────────────────

🟢 Strengths:
  • Clean token generation logic
  • Proper TypeScript types
  • Good error handling

🟡 Suggestions:
  • Line 45: Extract magic number to constant
  • Line 78: Consider batching DB queries

──────────────────────────────────────────
✅ Action Items (4 total)
──────────────────────────────────────────

🟡 Medium Priority:
  1. jwt.ts:45 - Extract TOKEN_EXPIRY constant
  2. jwt.ts:78 - Optimize database calls

🟢 Low Priority:
  3. Add edge case tests for token refresh
  4. Add JSDoc comments to public API

💡 Next steps:
   • Fix issues and run /cw:review again
   • Or proceed with /cw:next
```

## Review Modes

### Quick Review (Default)

```bash
/cw:review
```

- Reviews current phase files
- Standard depth analysis
- Focuses on blocking issues

### Deep Review

```bash
/cw:review --deep
```

- More thorough analysis
- Includes style nitpicks
- Performance profiling suggestions
- Security audit depth

### Focused Review

```bash
/cw:review --focus security
/cw:review --focus performance
/cw:review --focus tests
```

- Specialized analysis for specific concern
- Deeper checks in focused area
- Relevant recommendations only

## Review Categories

### Correctness
- Logic errors and bugs
- Edge case handling
- Requirements fulfillment
- Test coverage adequacy

### Code Quality
- Naming conventions
- Code organization
- Comments and documentation
- Readability and clarity

### Best Practices
- Language idioms
- Framework patterns
- Error handling
- Resource management

### Security
- Input validation
- Authentication checks
- Data sanitization
- Vulnerability patterns

### Performance
- Algorithm efficiency
- Resource usage
- Unnecessary operations
- Optimization opportunities

## Severity Levels

| Icon | Level | Meaning |
|------|-------|---------|
| 🔴 | Critical | Must fix - bugs, security flaws |
| 🟠 | Major | Should fix - significant issues |
| 🟡 | Minor | Consider fixing - improvements |
| 🟢 | Suggestion | Optional - nice to have |

## Score Ratings

| Icon | Rating | Description |
|------|--------|-------------|
| 🟢🟢 | Excellent | Exceeds standards |
| 🟢 | Good | Meets standards |
| 🟡 | Fair | Minor improvements needed |
| 🟠 | Poor | Significant issues |
| 🔴 | Critical | Blocking problems |

## Edge Cases

### No Completed Steps

```
ℹ️ Nothing to review yet

No completed steps found in .caw/task_plan.md.

💡 Complete some steps first:
   /cw:next
```

### All Issues Fixed

```
🎉 Clean Review!

All files passed review with no issues.

📊 Stats:
  • Files reviewed: 5
  • Lines analyzed: 847
  • Test coverage: 92%

💡 Ready to proceed:
   /cw:next for next step
   /cw:status to see progress
```

### Critical Issues Found

```
🔴 Critical Issues Found

Review cannot be approved until fixed:

1. src/auth/jwt.ts:23
   SQL Injection vulnerability
   User input directly concatenated to query

2. src/api/users.ts:45
   Missing authentication check
   Endpoint accessible without token

💡 Fix critical issues and run:
   /cw:review --step 2.3
```

## Integration with Workflow

```
┌─────────────────┐
│   /cw:next     │ ──── Implement step
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /cw:review    │ ──── Quality check
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Pass      Fail
    │         │
    ▼         ▼
  Next      Fix & Re-review
  Step
```

## Configuration

Review behavior can be customized via project config:

```yaml
# .caw/config.yaml (future feature)
review:
  auto_review: true          # Review after each step
  severity_threshold: minor  # Minimum severity to report
  categories:
    - correctness
    - security
    - performance
  ignore_patterns:
    - "*.test.ts"
    - "*.spec.ts"
```

## Integration

- **Reads**: `.caw/task_plan.md`, source files, config files
- **Invokes**: Reviewer agent via Task tool
- **Updates**: `.caw/task_plan.md` with review notes
- **Suggests**: `/cw:next`, re-review after fixes
