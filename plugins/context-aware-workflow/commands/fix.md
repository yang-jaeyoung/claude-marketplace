---
description: Fix issues identified by Reviewer agent - quick auto-fixes or comprehensive refactoring
---

# /caw:fix - Fix Review Issues

Automatically fix or interactively resolve issues identified by the Reviewer agent.

## Usage

```bash
/caw:fix                        # Auto-fix simple issues from last review
/caw:fix --interactive          # Review each fix before applying
/caw:fix --category docs        # Fix only documentation issues
/caw:fix --category style       # Fix only style/lint issues
/caw:fix --category constants   # Fix only magic numbers
/caw:fix --priority high        # Fix only high priority issues
/caw:fix --deep                 # Use Fixer agent for complex refactoring
/caw:fix --dry-run              # Show what would be fixed without applying
```

## Behavior

### Mode Selection

```
┌─────────────────────────────────────────────────────────────┐
│                     /caw:fix 모드 선택                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Simple Issues           Complex Issues                     │
│  (auto-fixable)          (needs analysis)                   │
│       │                        │                            │
│       ▼                        ▼                            │
│  ┌─────────┐            ┌─────────────┐                     │
│  │ Quick   │            │   Fixer     │                     │
│  │ Fix     │            │   Agent     │                     │
│  │ (Skill) │            │  (--deep)   │                     │
│  └─────────┘            └─────────────┘                     │
│       │                        │                            │
│       ▼                        ▼                            │
│  • Magic numbers        • Logic improvements                │
│  • JSDoc templates      • Multi-file refactoring            │
│  • Import ordering      • Pattern extraction                │
│  • Lint auto-fix        • Architecture changes              │
│  • Naming suggestions   • Performance optimization          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 1: Load Review Results

1. Check for recent review results in `.caw/last_review.json`
2. If not found, check `.caw/task_plan.md` for review notes
3. If no review data:

```
⚠️ No review results found

Run a review first to identify issues:
   /caw:review

Or specify files directly:
   /caw:fix src/auth/jwt.ts
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
   /caw:fix --deep
```

#### Interactive Mode

```bash
/caw:fix --interactive
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
/caw:fix --deep
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
   • /caw:review to re-check
   • /caw:next to continue workflow
```

## Fix Categories

### Constants (Auto-fixable)

Extracts magic numbers and strings to named constants:

```typescript
// Before
const expiresIn = 3600;
if (retries > 3) { ... }
const url = "https://api.example.com";

// After
const TOKEN_EXPIRY_SECONDS = 3600;
const MAX_RETRIES = 3;
const API_BASE_URL = "https://api.example.com";

const expiresIn = TOKEN_EXPIRY_SECONDS;
if (retries > MAX_RETRIES) { ... }
const url = API_BASE_URL;
```

### Documentation (Auto-fixable)

Generates JSDoc/docstring templates:

```typescript
// Before
function generateToken(user: User, options?: TokenOptions): string {
  ...
}

// After
/**
 * Generates a JWT token for the specified user.
 *
 * @param user - The user object to generate token for
 * @param options - Optional token configuration
 * @returns The generated JWT token string
 */
function generateToken(user: User, options?: TokenOptions): string {
  ...
}
```

### Style (Auto-fixable)

Runs linter with auto-fix:

```bash
# Detected linter
npx eslint --fix {files}
# or
ruff --fix {files}
# or
gofmt -w {files}
```

### Imports (Auto-fixable)

Organizes imports according to project conventions:

```typescript
// Before (random order)
import { jwt } from 'jsonwebtoken';
import { User } from '../types';
import express from 'express';
import { config } from './config';

// After (external → internal → types)
import express from 'express';
import { jwt } from 'jsonwebtoken';

import { config } from './config';

import { User } from '../types';
```

### Naming (Semi-auto)

Suggests improved names with confirmation:

```
🔧 Naming Suggestion

File: src/auth/jwt.ts:12

Current:  const d = new Date();
Suggested: const createdAt = new Date();

Context: Used for token creation timestamp

[A]pply  [S]kip  [C]ustom name
```

### Complex Categories (Fixer Agent Required)

For `logic`, `performance`, `security`, `architecture` - requires `--deep` flag to invoke Fixer agent.

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

```
┌─────────────────┐
│   /caw:review   │ ──── Identify issues
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   /caw:fix      │ ──── Apply fixes
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Simple    Complex
    │         │
    ▼         ▼
  Quick     Fixer
  Fix       Agent
    │         │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ Quality Gate    │ ──── Verify fixes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /caw:review    │ ──── Re-review (optional)
└─────────────────┘
```

## Edge Cases

### No Auto-fixable Issues

```
ℹ️ No auto-fixable issues found

Review results contain only complex issues:
  • 2 performance suggestions
  • 1 architecture recommendation

Use Fixer agent for these:
   /caw:fix --deep
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
   /caw:fix --deep for intelligent refactoring
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
- **Suggests**: `/caw:review`, `/caw:next`
