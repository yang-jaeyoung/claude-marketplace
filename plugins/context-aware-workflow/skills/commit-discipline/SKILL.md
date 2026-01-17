---
name: commit-discipline
description: Enforces Kent Beck's Tidy First commit separation rules. Validates that structural and behavioral changes are never mixed in the same commit.
allowed-tools: Bash, Read, Grep
forked-context: true
forked-context-returns: |
  status: VALID | INVALID | MIXED_CHANGE_DETECTED
  change_type: tidy | build | mixed
  suggestion: [commit split recommendation if mixed]
---

# Commit Discipline Skill

Enforces Tidy First methodology by ensuring proper commit separation between structural (Tidy) and behavioral (Build) changes.

## Core Principle

> "Never mix structural and behavioral changes in the same commit.
> Always make structural changes first when both are needed."
> — Kent Beck, Tidy First

## Triggers

This skill activates when:
1. Builder agent is about to commit changes
2. Before git commit execution via hook
3. Manual validation request
4. During `/caw:review` to check commit history

## Commit Types

| Prefix | Type | Description | Allowed Changes |
|--------|------|-------------|-----------------|
| `[tidy]` | Structural | Code cleanup with no behavior change | Rename, extract, reorganize, remove dead code |
| `[feat]` | Behavioral | New functionality | New functions, features |
| `[fix]` | Behavioral | Bug fixes | Logic corrections |
| `[test]` | Behavioral | Test changes | New tests, test updates |
| `[docs]` | Neutral | Documentation only | Comments, README |
| `[refactor]` | Mixed | **Avoid** - use tidy+feat instead | - |

## Change Classification

### Structural Changes (Tidy)

Changes that **do not** alter program behavior:

```markdown
✅ Valid Tidy Changes:
- Rename variable: `val` → `userToken`
- Rename function: `proc` → `processPayment`
- Extract method: Split large function into smaller ones
- Move code: Relocate to different file/module
- Remove dead code: Delete unused functions
- Reorder: Change declaration order
- Formatting: Whitespace, indentation
```

**Verification**: All tests must pass before AND after the change.

### Behavioral Changes (Build)

Changes that **alter** program behavior:

```markdown
✅ Valid Build Changes:
- Add new function
- Modify existing logic
- Add/change return values
- Add new tests
- Fix bugs
- Add new dependencies
```

**Verification**: New tests must be written. All tests must pass.

## Detection Algorithm

```yaml
analyze_staged_changes:
  inputs:
    - git diff --staged
    - git diff --staged --stat

  structural_indicators:
    - rename_pattern: "rename from .* to .*"
    - similar_line_count: before ≈ after (±5%)
    - no_new_exports: true
    - no_new_functions: true
    - no_logic_changes: no new if/for/while/try

  behavioral_indicators:
    - new_exports: true
    - new_functions: true
    - logic_additions: new if/for/while/try
    - new_test_files: true
    - new_dependencies: package.json changes

  classification:
    - all_structural: type = "tidy"
    - all_behavioral: type = "build"
    - mixed: type = "mixed" → SPLIT_REQUIRED
```

## Validation Workflow

### Pre-Commit Validation

```
1. Read git diff --staged
2. Classify each changed file
3. Aggregate classification:
   - If all tidy → ✅ Proceed with [tidy] prefix
   - If all build → ✅ Proceed with [feat]/[fix] prefix
   - If mixed → ❌ Block and suggest split
```

### Mixed Change Response

```
⚠️ Mixed Change Detected

Staged changes contain both structural and behavioral modifications:

Structural (Tidy):
  • src/auth/jwt.ts: Renamed `val` → `tokenPayload`
  • src/utils/helpers.ts: Extracted `formatDate` method

Behavioral (Build):
  • src/auth/jwt.ts: Added new `refreshToken` function
  • src/auth/jwt.ts: Modified validation logic

Recommendation:
1. Unstage behavioral changes:
   git reset HEAD src/auth/jwt.ts (lines 45-78)

2. Commit structural only:
   git commit -m "[tidy] Improve naming in auth module"

3. Stage and commit behavioral:
   git add src/auth/jwt.ts
   git commit -m "[feat] Add token refresh functionality"
```

## Commit Message Templates

### Tidy Commit

```
[tidy] <Short description>

Changes:
- Renamed X to Y for clarity
- Extracted Z method from W
- Removed unused function Q

No behavior change. All tests pass.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Build Commit

```
[feat] <Short description>

Changes:
- Added new functionality X
- Updated Y to handle Z case

Tests: N new, M updated, all passing

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Integration with Hooks

### hooks.json Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tool_name": "Bash",
          "command_pattern": "git commit"
        },
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Validate this commit follows Tidy First discipline: separate structural and behavioral changes. Check if the staged changes are purely structural (tidy) or purely behavioral (build). If mixed, block and suggest splitting."
          }
        ]
      }
    ]
  }
}
```

## Metrics Tracking

Track commit discipline over time:

```json
{
  "commit_discipline": {
    "tidy_commits": 15,
    "build_commits": 42,
    "mixed_commits_prevented": 8,
    "split_suggestions_accepted": 7,
    "compliance_rate": "98%"
  }
}
```

## Edge Cases

### Large Refactoring

When a large refactor is needed:

```
Approach:
1. Plan the refactoring as multiple Tidy steps
2. Each step should be small and atomic
3. Commit after each step: [tidy] Step 1 of 5: ...
4. Run tests after each commit
5. Only after all tidy commits, proceed to Build
```

### Emergency Fixes

For critical hotfixes:

```
Allowance:
- [hotfix] prefix permitted for critical fixes
- Should still avoid mixing structural changes
- Document why separation wasn't possible
- Create follow-up Tidy step if needed
```

## Boundaries

**Will:**
- Analyze staged changes for type classification
- Block mixed commits with clear explanation
- Suggest commit splitting strategy
- Validate commit message prefixes
- Track compliance metrics

**Will Not:**
- Automatically split commits (requires user action)
- Modify staged changes
- Force commit without user consent
- Block legitimate mixed changes in emergencies
