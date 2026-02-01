---
name: quick-fix
description: Auto-fixes simple review issues like magic numbers, missing docs, style violations, and import ordering
allowed-tools: Read, Edit, Bash, Glob, Grep
forked-context: true
forked-context-returns: |
  status: SUCCESS | PARTIAL | FAILED
  summary: { fixed: N, skipped: N, failed: N }
  changes: [{ file, line, category, description }]
  remaining: [Issues requiring --deep]
hooks:
  ReviewComplete:
    action: suggest
    message: "Auto-fixable issues found. Run /cw:fix to apply."
---

# Quick Fix Skill

Automated fixes for simple, auto-fixable code issues.

## Triggers

1. `/cw:fix` (without --deep)
2. `/cw:fix --category <type>`
3. After Reviewer finds auto-fixable issues

## Auto-Fixable Categories

| Category | Fix | Description |
|----------|-----|-------------|
| `constants` | ✅ | Magic numbers → named constants |
| `docs` | ✅ | Missing JSDoc/docstrings → templates |
| `style` | ✅ | Lint violations via linter auto-fix |
| `imports` | ✅ | Import ordering/cleanup |
| `naming` | ⚠️ | Variable naming (needs confirmation) |

**Skip** (needs agent): logic, performance, security, architecture

## Workflow

1. **Load**: `.caw/last_review.json` for auto_fixable issues
2. **Filter**: By category if specified
3. **Apply**: Category-specific fixes
4. **Verify**: Run linter, check syntax
5. **Report**: Summary of changes

## Fix Examples

### Constants
```typescript
// Before: const expiresIn = 3600;
// After:
const TOKEN_EXPIRY_SECONDS = 3600;
const expiresIn = TOKEN_EXPIRY_SECONDS;
```

### Documentation
```typescript
/**
 * Generates a JWT token for the specified user.
 * @param user - The user object
 * @returns The generated JWT token string
 */
function generateToken(user: User): string { ... }
```

### Style
```bash
npx eslint --fix {files}    # TypeScript
ruff --fix {files}          # Python
gofmt -w {files}            # Go
```

### Imports
```typescript
// Order: external → internal → relative → types
import express from 'express';
import { config } from './config';
import { User } from '../types';
```

## Result Output

```
🔧 Quick Fix Complete

  ✅ constants: 3 magic numbers extracted
  ✅ docs: 2 JSDoc templates added
  ✅ style: 5 lint violations fixed
  ⏭️ Skipped: 2 performance, 1 architecture

Summary: 10 fixed, 3 skipped, 0 failed
💡 For complex fixes: /cw:fix --deep
```

## Modes

- `--dry-run`: Preview changes without applying
- `--interactive`: Approve each fix individually
- `--category <type>`: Fix specific category only

## Integration

1. Reviewer writes `.caw/last_review.json`
2. If auto_fixable > 0: suggest `/cw:fix`
3. Quick Fix handles: constants, docs, style, imports
4. Fixer Agent handles: logic, performance, security, architecture

## Boundaries

**Will:** Extract constants, generate docs, run linter auto-fix, organize imports
**Won't:** Refactor logic, fix security issues, optimize performance, make architectural changes
