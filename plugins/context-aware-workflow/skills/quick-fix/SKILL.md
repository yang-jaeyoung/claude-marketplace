---
name: quick-fix
description: Auto-fixes simple review issues like magic numbers, missing docs, style violations, and import ordering. Invoked automatically after review or manually via /cw:fix.
allowed-tools: Read, Edit, Bash, Glob, Grep
forked-context: true
forked-context-returns: |
  status: SUCCESS | PARTIAL | FAILED
  summary: { fixed: N, skipped: N, failed: N }
  changes: [{ file, line, category, description }]
  remaining: [깊은 분석이 필요한 이슈 목록]
hooks:
  ReviewComplete:
    action: suggest
    message: "Auto-fixable issues found. Run /cw:fix to apply."
    condition: "last_review.json has auto_fixable > 0"
---

# Quick Fix Skill

Automated quick fixes for simple, auto-fixable code issues identified by the Reviewer agent.

## Triggers

This skill activates when:
1. User runs `/cw:fix` (without --deep flag)
2. User runs `/cw:fix --category <type>`
3. Reviewer completes and finds auto-fixable issues
4. Manual quick-fix request for specific files

## Auto-Fixable Categories

| Category | Auto-Fix | Description |
|----------|----------|-------------|
| `constants` | ✅ Yes | Magic numbers → named constants |
| `docs` | ✅ Yes | Missing JSDoc/docstrings → templates |
| `style` | ✅ Yes | Lint violations → auto-fix via linter |
| `imports` | ✅ Yes | Import ordering/cleanup |
| `naming` | ⚠️ Semi | Variable naming (needs confirmation) |

## Workflow

### Step 1: Load Review Results

```yaml
sources:
  primary: .caw/last_review.json
  fallback: .caw/task_plan.md (review notes)

extract:
  - auto_fixable issues
  - file locations and line numbers
  - suggested fixes
  - category classifications
```

### Step 2: Filter by Category

```yaml
if --category provided:
  filter issues by specified category
else:
  process all auto_fixable categories:
    - constants
    - docs
    - style
    - imports

skip categories requiring agent:
  - logic
  - performance
  - security
  - architecture
```

### Step 3: Apply Fixes by Category

#### Constants Fix

Extract magic numbers to named constants:

```typescript
// Detection pattern
const regex = /(?<![a-zA-Z_])(\d+)(?![a-zA-Z_])/g;

// Before
const expiresIn = 3600;
if (retries > 3) { ... }

// After
const TOKEN_EXPIRY_SECONDS = 3600;
const MAX_RETRIES = 3;
const expiresIn = TOKEN_EXPIRY_SECONDS;
if (retries > MAX_RETRIES) { ... }
```

**Naming Rules**:
```yaml
constant_naming:
  time_seconds: "{CONTEXT}_SECONDS"
  time_ms: "{CONTEXT}_MS"
  count: "MAX_{CONTEXT}" or "{CONTEXT}_COUNT"
  size: "MAX_{CONTEXT}_SIZE" or "{CONTEXT}_LIMIT"
  default: "{CONTEXT}_VALUE"
```

#### Documentation Fix

Generate JSDoc/docstring templates:

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

**Template Generation**:
```yaml
jsdoc_template:
  description: "Infer from function name using verb analysis"
  params: "Extract from function signature"
  returns: "Extract from return type"
  throws: "Detect from error handling patterns"

python_docstring:
  style: google | numpy | sphinx (detect from project)
  description: "Infer from function name"
  args: "Extract from signature with types"
  returns: "Extract from return annotation"
```

#### Style Fix

Run linter auto-fix:

```yaml
commands:
  typescript:
    eslint: "npx eslint --fix {files}"
    prettier: "npx prettier --write {files}"
  python:
    ruff: "ruff --fix {files}"
    black: "black {files}"
  go:
    gofmt: "gofmt -w {files}"

detection:
  - Check package.json for eslint/prettier
  - Check pyproject.toml for ruff/black
  - Check for .eslintrc, .prettierrc files
```

#### Imports Fix

Organize imports:

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

**Import Organization**:
```yaml
import_order:
  1_external: "node_modules packages"
  2_internal: "project absolute imports"
  3_relative: "relative imports (../)"
  4_types: "type-only imports"

tools:
  typescript: "eslint-plugin-import --fix"
  python: "isort {files}"
```

### Step 4: Verify Fixes

After each fix category:

```yaml
verification:
  - Run linter on modified files
  - Check for syntax errors
  - Ensure no new issues introduced

rollback_on:
  - Syntax error introduced
  - More issues than before
  - Type errors in TypeScript
```

### Step 5: Report Results

```markdown
🔧 Quick Fix Complete

Applied Fixes:
  ✅ constants: 3 magic numbers extracted
     • src/auth/jwt.ts:45 → TOKEN_EXPIRY_SECONDS
     • src/auth/jwt.ts:67 → MAX_RETRIES
     • src/api/users.ts:89 → PAGE_SIZE

  ✅ docs: 2 JSDoc templates added
     • src/auth/jwt.ts:generateToken()
     • src/auth/jwt.ts:validateToken()

  ✅ style: 5 lint violations fixed
     • eslint --fix applied to 2 files

  ⏭️ Skipped (needs --deep):
     • 2 performance suggestions
     • 1 architecture recommendation

Summary: 10 fixed, 3 skipped, 0 failed

💡 For complex fixes: /cw:fix --deep
```

## Interactive Mode

When `--interactive` flag is used:

```
🔧 Interactive Fix Mode

[1/10] src/auth/jwt.ts:45
       Category: constants
       Issue: Magic number 3600

       Current:
         const expiresIn = 3600;

       Suggested:
         const TOKEN_EXPIRY_SECONDS = 3600;
         const expiresIn = TOKEN_EXPIRY_SECONDS;

       [A]pply  [S]kip  [E]dit name  [Q]uit
       > _
```

## Dry Run Mode

When `--dry-run` flag is used:

```
🔧 Quick Fix Preview (Dry Run)

Would apply:
  constants:
    ✓ src/auth/jwt.ts:45 - 3600 → TOKEN_EXPIRY_SECONDS
    ✓ src/api/users.ts:89 - 30 → MAX_PAGE_SIZE

  docs:
    ✓ src/auth/jwt.ts:67 - Add JSDoc to generateToken()

  style:
    ✓ 5 ESLint auto-fixes in 2 files

Summary: 8 changes ready to apply

💡 Run without --dry-run to apply changes
```

## Forked Context Behavior

See [Forked Context Pattern](../../_shared/forked-context.md).

**Returns**: `status: SUCCESS | PARTIAL | FAILED` with fix summary

**Output Examples:**
- `🔧 Quick Fix: 10 fixed, 3 skipped` - Summary
- `changes: [{file, line, category, description}]` - Applied changes
- `remaining: [complex issues for --deep]` - Fixer agent items

## Configuration

### `.caw/quick-fix.json` (Optional)

```json
{
  "auto_categories": ["constants", "docs", "style", "imports"],
  "skip_categories": ["naming"],
  "constants": {
    "naming_style": "SCREAMING_SNAKE_CASE",
    "min_occurrences": 1
  },
  "docs": {
    "style": "jsdoc",
    "required_tags": ["param", "returns"]
  },
  "style": {
    "tool": "eslint",
    "config_file": ".eslintrc.js"
  },
  "imports": {
    "order": ["external", "internal", "relative", "types"],
    "newline_between_groups": true
  }
}
```

## Integration

### With Reviewer Agent

```yaml
flow:
  1. Reviewer completes code analysis
  2. Reviewer writes .caw/last_review.json
  3. If auto_fixable issues exist:
     - Show suggestion: "Run /cw:fix to apply quick fixes"
  4. User runs /cw:fix
  5. Quick Fix skill processes auto_fixable issues
  6. Complex issues remain for /cw:fix --deep
```

### With Fixer Agent

```yaml
handoff:
  quick_fix_handles:
    - constants
    - docs
    - style
    - imports

  fixer_agent_handles:
    - logic
    - performance
    - security
    - architecture

  trigger_fixer:
    - /cw:fix --deep
    - Complex issues detected
    - Quick fix insufficient
```

## Boundaries

**Will:**
- Extract magic numbers to constants
- Generate documentation templates
- Run linter auto-fix
- Organize imports
- Apply safe, automated transformations

**Will Not:**
- Refactor logic or algorithms
- Make architectural changes
- Fix security vulnerabilities
- Optimize performance
- Make changes requiring analysis
