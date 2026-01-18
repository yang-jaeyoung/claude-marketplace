---
description: Fix issues identified by Reviewer agent - quick auto-fixes or comprehensive refactoring
---

# /cw:fix - Fix Review Issues

Automatically fix or interactively resolve issues identified by the Reviewer agent.

## Usage

```bash
/cw:fix                        # Auto-fix simple issues from last review
/cw:fix --interactive          # Review each fix before applying
/cw:fix --category docs        # Fix only documentation issues
/cw:fix --category style       # Fix only style/lint issues
/cw:fix --category constants   # Fix only magic numbers
/cw:fix --priority high        # Fix only high priority issues
/cw:fix --deep                 # Use Fixer agent for complex refactoring
/cw:fix --dry-run              # Show what would be fixed without applying
```

## Behavior

### Mode Selection

**Quick Fix (default)**: constants, docs, imports, style, naming → Auto-fix or semi-auto
**Fixer Agent (`--deep`)**: logic, performance, security, architecture → Multi-file refactoring

### Step 1: Load Review Results

1. Check for recent review results in `.caw/last_review.json`
2. If not found, check `.caw/task_plan.md` for review notes
3. If no review data:

```
⚠️ No review results found

Run a review first to identify issues:
   /cw:review

Or specify files directly:
   /cw:fix src/auth/jwt.ts
```

### Step 2: Categorize Issues

Parse review results and categorize:

| Category | Auto-Fixable | Examples |
|----------|--------------|----------|
| `constants` | ✅ Yes | Magic numbers → named constants |
| `docs` | ✅ Yes | Missing JSDoc → template generation |
| `style` | ✅ Yes | ESLint/Prettier violations |
| `imports` | ✅ Yes | Import ordering, unused imports |
| `naming` | ⚠️ Semi | Variable/function naming (needs confirmation) |
| `logic` | ❌ No | Algorithm improvements |
| `performance` | ❌ No | DB query optimization |
| `security` | ❌ No | Vulnerability fixes |
| `architecture` | ❌ No | Pattern refactoring |

### Step 3: Execute Fixes

#### Quick Fix Mode (Default)

For auto-fixable categories:

```
🔧 Quick Fix Mode

Scanning review results...

Auto-fixable issues found:
  ✓ 3 magic numbers → constants
  ✓ 2 missing JSDoc → templates
  ✓ 5 lint violations → auto-fix

Non-auto-fixable (use --deep):
  ⚠ 2 performance suggestions
  ⚠ 1 architecture recommendation

Applying fixes...

✅ Fixed: src/auth/jwt.ts
   • Line 45: 3600 → TOKEN_EXPIRY_SECONDS
   • Line 67: Added JSDoc for generateToken()

✅ Fixed: src/api/users.ts
   • Line 12: Reordered imports
   • Line 89: 30 → MAX_PAGE_SIZE

📊 Summary:
   Applied: 10 fixes
   Skipped: 3 (needs --deep)

💡 For complex fixes:
   /cw:fix --deep
```

#### Interactive Mode

```bash
/cw:fix --interactive
```

```
🔧 Interactive Fix Mode

[1/10] src/auth/jwt.ts:45
       Issue: Magic number 3600

       Current:
         const expiresIn = 3600;

       Suggested:
         const TOKEN_EXPIRY_SECONDS = 3600;
         const expiresIn = TOKEN_EXPIRY_SECONDS;

       [A]pply  [S]kip  [E]dit  [Q]uit
       > A

       ✅ Applied

[2/10] src/auth/jwt.ts:67
       Issue: Missing JSDoc for public function
       ...
```

#### Deep Fix Mode (Fixer Agent)

```bash
/cw:fix --deep
```

Invokes the Fixer agent for comprehensive refactoring:

```
🔧 Deep Fix Mode - Invoking Fixer Agent

Analyzing review results...

Complex issues requiring Fixer agent:
  1. Performance: Batch DB queries in jwt.ts
  2. Architecture: Extract validation to separate module
  3. Logic: Improve error handling flow

Fixer Agent analyzing codebase...

📋 Refactoring Plan:
┌────────────────────────────────────────────────────────────┐
│ 1. Batch DB Queries                                        │
│    Files: src/auth/jwt.ts, src/services/user.ts            │
│    Impact: ~30% reduction in DB calls                      │
│    Risk: Low                                               │
├────────────────────────────────────────────────────────────┤
│ 2. Extract Validation Module                               │
│    Files: New src/validation/auth.ts                       │
│    Impact: Better separation of concerns                   │
│    Risk: Medium - needs test updates                       │
├────────────────────────────────────────────────────────────┤
│ 3. Improve Error Handling                                  │
│    Files: src/auth/jwt.ts, src/middleware/auth.ts          │
│    Impact: Consistent error responses                      │
│    Risk: Low                                               │
└────────────────────────────────────────────────────────────┘

Proceed with refactoring? [Y/n/select]
```

### Step 4: Verify Fixes

After applying fixes:

```
🔍 Verifying fixes...

Running quality checks:
  ✅ TypeScript: No errors
  ✅ ESLint: All rules pass
  ✅ Tests: 15/15 passed

✅ All fixes verified successfully

💡 Next steps:
   • /cw:review to re-check
   • /cw:next to continue workflow
```

## Fix Categories

| Category | Auto-Fix | Action | Example |
|----------|----------|--------|---------|
| `constants` | ✅ Yes | Magic numbers → NAMED_CONSTANTS | `3600 → TOKEN_EXPIRY_SECONDS` |
| `docs` | ✅ Yes | Generate JSDoc/docstrings | `function → /** @param ... */` |
| `style` | ✅ Yes | Run linter auto-fix | `eslint --fix` / `ruff --fix` |
| `imports` | ✅ Yes | Organize: external → internal → types | Reorder + group |
| `naming` | ⚠️ Semi | Suggest + confirm | `d → createdAt` |
| `logic` | ❌ --deep | Fixer agent refactoring | Algorithm improvements |
| `performance` | ❌ --deep | Fixer agent analysis | DB query optimization |
| `security` | ❌ --deep | Fixer agent remediation | Vulnerability fixes |
| `architecture` | ❌ --deep | Fixer agent extraction | Pattern refactoring |

## Options

| Option | Description |
|--------|-------------|
| `--interactive`, `-i` | Review each fix before applying |
| `--category <cat>` | Fix only specific category |
| `--priority <level>` | Filter by priority (high, medium, low) |
| `--deep` | Use Fixer agent for complex refactoring |
| `--dry-run` | Show fixes without applying |
| `--file <path>` | Fix issues in specific file only |
| `--yes`, `-y` | Apply all fixes without confirmation |

## Integration

**Flow**: `/cw:review` → `/cw:fix` → Quality Gate → `/cw:review` (optional re-check)

**Routing**: Simple issues → Quick Fix skill | Complex issues → Fixer Agent (`--deep`)

## Edge Cases

### No Auto-fixable Issues

```
ℹ️ No auto-fixable issues found

Review results contain only complex issues:
  • 2 performance suggestions
  • 1 architecture recommendation

Use Fixer agent for these:
   /cw:fix --deep
```

### Conflicting Fixes

```
⚠️ Conflicting fixes detected

Multiple suggestions for src/auth/jwt.ts:45:
  1. Extract to constant (style)
  2. Inline as parameter default (refactor)

Please choose:
  [1] Extract to constant (recommended)
  [2] Inline as parameter
  [S] Skip this fix
```

### Fix Failed Verification

```
❌ Fix verification failed

Applied fix broke tests:
  • auth.test.ts: Expected TOKEN_EXPIRY to be defined

Rolling back changes...
✅ Rollback complete

💡 This fix needs manual intervention or use:
   /cw:fix --deep for intelligent refactoring
```

## Configuration

```yaml
# .caw/config.yaml (future feature)
fix:
  auto_categories:
    - constants
    - docs
    - style
    - imports
  confirm_categories:
    - naming
  agent_categories:
    - logic
    - performance
    - security
    - architecture
  verify_after_fix: true
  backup_before_fix: true
```

## Integration Points

- **Reads**: `.caw/last_review.json`, `.caw/task_plan.md`, source files
- **Invokes**: Fixer agent (--deep mode), linters, quality-gate skill
- **Writes**: Fixed source files, `.caw/fix_history.json`
- **Suggests**: `/cw:review`, `/cw:next`
