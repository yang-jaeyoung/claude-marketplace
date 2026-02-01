---
description: Analyze and apply structural improvements following Kent Beck's Tidy First methodology
argument-hint: "[--scope <path>] [--preview] [--apply]"
---

# /cw:tidy - Tidy First Preparation

Analyze target code for structural improvements before implementing features. Following Kent Beck's Tidy First methodology.

## Usage

```bash
/cw:tidy                    # Analyze current step target
/cw:tidy --scope src/auth/  # Specific directory
/cw:tidy --preview          # Show suggestions only
/cw:tidy --apply            # Apply changes
/cw:tidy --add-step         # Add tidy step to plan
/cw:tidy --split            # Separate tidy/build commits
/cw:tidy --commit           # Commit with [tidy] prefix
```

## Flags

| Flag | Description |
|------|-------------|
| `--scope <path>` | Target specific file/directory |
| `--preview` | Show suggestions, don't modify |
| `--apply` | Apply changes automatically |
| `--add-step` | Insert Tidy step in task_plan.md |
| `--commit` | Commit with `[tidy]` prefix |
| `--split` | Split mixed changes into tidy/build commits |

## Analysis Categories

| Category | Detection | Suggestions |
|----------|-----------|-------------|
| **Naming** | Single letters, abbreviations, generics | Domain-specific, full words |
| **Duplication** | Identical blocks, similar patterns | Extract to shared function |
| **Dead Code** | Unused functions, unreachable code | Remove |
| **Structure** | Large functions, deep nesting | Extract methods, flatten |

## Output

```markdown
🧹 Tidy First Analysis

**Target**: Step 2.1 - JWT utility
**Files**: src/auth/jwt.ts

## Issues Found

### Unclear Naming (3)
| Location | Current | Suggested |
|----------|---------|-----------|
| jwt.ts:12 | val | tokenPayload |
| jwt.ts:45 | cb | verifyCallback |

### Code Duplication (1)
jwt.ts:23-30, 67-74 → Extract to parseToken()

### Dead Code (2)
- jwt.ts:112 - Unused oldValidate
- jwt.ts:145 - Unreachable block

## Actions
1. /cw:tidy --add-step (Recommended)
2. /cw:tidy --apply
3. /cw:next (skip)
```

## Add Step Mode

Inserts Tidy step before current pending step:

```markdown
| # | Step | Type | Status |
|---|------|------|--------|
| 2.0 | Clean up auth naming | 🧹 Tidy | ⏳ |
| 2.1 | JWT utility module | 🔨 Build | ⏳ |
```

## Apply Mode

```
🧹 Applying Tidy Changes

[1/4] Renaming variables...
  ✓ jwt.ts:12 - val → tokenPayload

[2/4] Extracting methods...
  ✓ Created parseToken()

[3/4] Removing dead code...
  ✓ Removed oldValidate

[4/4] Running tests...
  ✓ All 15 tests pass

Ready to commit: git commit -m "[tidy] Clean up auth module"
```

## Split Mode

Separates mixed changes into commits:

```
🔀 Splitting Mixed Changes

[1/3] Separating... tidy: 3, build: 2
[2/3] Tidy commit... "[tidy] Rename variables"
[3/3] Build commit... "[feat] Add token refresh"

✅ Created 2 commits
```

## Serena Integration

Uses Serena MCP for precise analysis:
- `get_symbols_overview` - Find symbols
- `find_referencing_symbols` - Check before removal
- `rename_symbol` - Apply renames
- `replace_symbol_body` - Extract methods

## Boundaries

**Will**: Analyze, suggest, apply safe changes, commit with prefix
**Won't**: Behavioral changes, skip test verification, modify outside scope

## Related

- [commit-discipline Skill](../skills/commit-discipline/SKILL.md)
- [Review Command](./review.md)
