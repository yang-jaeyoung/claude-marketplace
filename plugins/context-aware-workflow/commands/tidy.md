---
description: Analyze and apply structural improvements following Kent Beck's Tidy First methodology
argument-hint: "[--scope <path>] [--preview] [--apply]"
---

# /caw:tidy - Tidy First Preparation

Analyze target code for structural improvements and apply tidying before implementing new features. Following Kent Beck's Tidy First methodology.

## Usage

```bash
# Analyze current step target
/caw:tidy

# Analyze specific directory or file
/caw:tidy --scope src/auth/

# Preview suggestions without applying
/caw:tidy --preview

# Apply suggested tidying automatically
/caw:tidy --apply

# Add tidy step to task plan
/caw:tidy --add-step

# Split mixed changes into separate commits
/caw:tidy --split
```

## Flags

| Flag | Description |
|------|-------------|
| `--scope <path>` | Target specific file or directory |
| `--preview` | Show suggestions only, don't modify |
| `--apply` | Apply suggested changes automatically |
| `--add-step` | Add Tidy step to task_plan.md |
| `--commit` | Commit tidy changes with `[tidy]` prefix |
| `--split` | Split mixed changes into separate Tidy and Build commits |

## Workflow

### Default Behavior (No Flags)

```
/caw:tidy

1. Read current pending step from task_plan.md
2. Identify target files for that step
3. Analyze for structural issues
4. Present findings with suggested actions
```

### Output Example

```markdown
🧹 Tidy First Analysis

**Target**: Step 2.1 - JWT utility module
**Files**: src/auth/jwt.ts, src/auth/types.ts

## Structural Issues Found

### 1. Unclear Naming (3 issues)
| Location | Current | Suggested |
|----------|---------|-----------|
| jwt.ts:12 | `val` | `tokenPayload` |
| jwt.ts:45 | `cb` | `verifyCallback` |
| jwt.ts:78 | `e` | `tokenError` |

### 2. Code Duplication (1 issue)
| Files | Pattern | Suggestion |
|-------|---------|------------|
| jwt.ts:23-30, jwt.ts:67-74 | Token parsing | Extract to `parseToken()` |

### 3. Dead Code (2 issues)
- `jwt.ts:112` - Unused function `oldValidate`
- `jwt.ts:145` - Unreachable code block

## Recommended Actions

Option 1: Add Tidy Step (Recommended)
  → `/caw:tidy --add-step`
  → Creates Step 2.0 with tidy tasks

Option 2: Apply Now
  → `/caw:tidy --apply`
  → Apply changes immediately

Option 3: Skip
  → `/caw:next`
  → Proceed without tidying (not recommended)
```

## Analysis Categories

### Naming Analysis

Checks for unclear variable and function names:

```yaml
patterns:
  - single_letter: [a, b, c, e, i, j, k, n, x, y, z]
  - abbreviations: [cb, fn, val, tmp, res, req, err]
  - generic: [data, info, item, obj, value, result]

suggestions:
  - Use domain-specific names
  - Prefer full words over abbreviations
  - Name should describe purpose, not type
```

### Duplication Detection

Identifies repeated code patterns:

```yaml
detection:
  - exact_match: Identical code blocks (>3 lines)
  - similar_pattern: Similar structure with different values
  - copy_paste: Nearly identical with minor variations

suggestions:
  - Extract to shared function
  - Create utility method
  - Use abstraction/inheritance
```

### Dead Code Detection

Finds unused code:

```yaml
detection:
  - unused_functions: No callers found
  - unreachable_code: After return/throw/break
  - commented_code: Large commented blocks
  - unused_imports: Imported but not used

suggestions:
  - Remove unused functions
  - Delete unreachable code
  - Remove or restore commented code
  - Clean up imports
```

### Structure Analysis

Checks code organization:

```yaml
detection:
  - large_functions: >50 lines
  - deep_nesting: >3 levels
  - long_files: >300 lines
  - mixed_concerns: Multiple responsibilities

suggestions:
  - Extract methods
  - Flatten conditionals
  - Split into modules
  - Apply single responsibility
```

## Adding Tidy Steps

### /caw:tidy --add-step

Inserts a Tidy step before the current pending step:

**Before:**
```markdown
| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 2.1 | JWT utility module | 🔨 Build | ⏳ | Builder | - | |
```

**After:**
```markdown
| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 2.0 | Clean up auth naming | 🧹 Tidy | ⏳ | Builder | - | Auto-generated |
| 2.1 | JWT utility module | 🔨 Build | ⏳ | Builder | 2.0 | |
```

## Apply Mode

### /caw:tidy --apply

Executes tidy changes automatically:

```
🧹 Applying Tidy Changes

[1/4] Renaming variables...
  ✓ jwt.ts:12 - val → tokenPayload
  ✓ jwt.ts:45 - cb → verifyCallback
  ✓ jwt.ts:78 - e → tokenError

[2/4] Extracting methods...
  ✓ Created parseToken() from duplicate code

[3/4] Removing dead code...
  ✓ Removed oldValidate function
  ✓ Removed unreachable block

[4/4] Running tests...
  ✓ All 15 tests pass

🧪 Verification: No behavior change detected

Ready to commit:
  git commit -m "[tidy] Clean up auth module naming and structure"

Proceed with commit? [Y/n]
```

## Split Mode

### /caw:tidy --split

Automatically separates mixed changes into separate Tidy and Build commits:

```
🔀 Splitting Mixed Changes

Analyzing staged changes...

Found mixed changes:
  Structural (Tidy): 3 changes
  Behavioral (Build): 2 changes

[Step 1/3] Separating changes...
  ✓ Identified tidy changes: rename, extract method
  ✓ Identified build changes: new function, logic update

[Step 2/3] Creating Tidy commit...
  ✓ Staged structural changes only
  ✓ Tests pass (behavior unchanged)
  → git commit -m "[tidy] Rename variables and extract method"

[Step 3/3] Creating Build commit...
  ✓ Staged behavioral changes
  ✓ Tests pass
  → git commit -m "[feat] Add token refresh functionality"

✅ Split Complete

Created 2 commits:
  1. [tidy] Rename variables and extract method
  2. [feat] Add token refresh functionality

Both commits are properly separated and tested.
```

### Split Workflow

```yaml
split_process:
  1_analyze:
    - Parse git diff --staged
    - Classify each hunk as structural or behavioral
    - Group related changes together

  2_stage_tidy:
    - git reset HEAD (unstage all)
    - git add -p (stage only structural hunks)
    - Verify tests pass
    - Commit with [tidy] prefix

  3_stage_build:
    - git add remaining changes
    - Verify tests pass
    - Commit with appropriate prefix ([feat]/[fix])

  4_verify:
    - Ensure no changes left unstaged
    - Confirm both commits are clean
```

## Integration

### With task_plan.md

- Reads current step target from plan
- Can insert Tidy steps dynamically
- Updates dependencies when steps added

### With Builder Agent

- Builder checks for tidy suggestions before Build steps
- Can invoke `/caw:tidy --preview` automatically
- Suggests running tidy when issues found

### With commit-discipline Skill

- Ensures tidy commits are properly prefixed
- Validates no behavioral changes in tidy commits
- Tracks tidy commit metrics

## Serena Integration

Uses Serena MCP tools for precise analysis:

```
# Find symbols to analyze
get_symbols_overview("src/auth/jwt.ts")

# Check for references before removing
find_referencing_symbols("oldValidate", "src/auth/jwt.ts")

# Apply renames
rename_symbol("val", "tokenPayload", "src/auth/jwt.ts")

# Extract methods
replace_symbol_body("processToken", "src/auth/jwt.ts", <new_body>)
```

## Edge Cases

### No Issues Found

```
✅ No Tidy Needed

Target files are already clean:
- src/auth/jwt.ts
- src/auth/types.ts

Proceeding directly to Build step is recommended.

Run: /caw:next
```

### Many Issues Found

```
⚠️ Extensive Tidying Needed

Found 15+ structural issues. Consider:

1. Create multiple Tidy steps:
   /caw:tidy --add-step --split

2. Prioritize critical issues:
   /caw:tidy --apply --priority high

3. Discuss scope with team first
```

## Output Files

| File | Description |
|------|-------------|
| `.caw/tidy_analysis.json` | Structured analysis results |
| `.caw/tidy_history.json` | History of tidy operations |

## Boundaries

**Will:**
- Analyze code for structural issues
- Suggest improvements
- Apply safe, reversible changes
- Commit with proper prefix

**Will Not:**
- Make behavioral changes
- Apply changes without test verification
- Modify code outside specified scope
- Force changes without user consent
