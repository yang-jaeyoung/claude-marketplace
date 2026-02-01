---
description: Fix issues identified by Reviewer agent - quick auto-fixes or comprehensive refactoring
argument-hint: "[--interactive] [--category <cat>] [--deep]"
---

# /cw:fix - Fix Review Issues

Automatically fix or interactively resolve issues identified by the Reviewer agent.

## Usage

```bash
/cw:fix                        # Auto-fix simple issues
/cw:fix --interactive          # Review each fix
/cw:fix --category docs        # Fix specific category
/cw:fix --priority high        # Fix by priority
/cw:fix --deep                 # Use Fixer agent
/cw:fix --dry-run              # Preview only
```

## Mode Selection

| Mode | Categories | Action |
|------|------------|--------|
| **Quick Fix** (default) | constants, docs, imports, style, naming | Auto-fix |
| **Fixer Agent** (`--deep`) | logic, performance, security, architecture | Multi-file refactoring |

## Fix Categories

| Category | Auto-Fix | Action |
|----------|----------|--------|
| `constants` | ✅ Yes | Magic numbers → NAMED_CONSTANTS |
| `docs` | ✅ Yes | Generate JSDoc templates |
| `style` | ✅ Yes | Run linter auto-fix |
| `imports` | ✅ Yes | Organize imports |
| `naming` | ⚠️ Semi | Suggest + confirm |
| `logic` | ❌ --deep | Algorithm improvements |
| `performance` | ❌ --deep | Query optimization |
| `security` | ❌ --deep | Vulnerability fixes |
| `architecture` | ❌ --deep | Pattern refactoring |

## Workflow

1. **Load**: Read `.caw/last_review.json` or task_plan.md
2. **Categorize**: Parse issues by category and priority
3. **Execute**: Apply fixes (quick or Fixer agent)
4. **Verify**: Run tests and quality checks

## Output

```
🔧 Quick Fix Mode

Auto-fixable:
  ✓ 3 magic numbers → constants
  ✓ 2 missing JSDoc → templates
  ✓ 5 lint violations → auto-fix

Non-auto-fixable (use --deep):
  ⚠ 2 performance suggestions

Applied: 10 fixes | Skipped: 2
```

## Interactive Mode

```
[1/10] src/auth/jwt.ts:45
       Issue: Magic number 3600

       Current:  const expiresIn = 3600;
       Suggested: const TOKEN_EXPIRY = 3600;

       [A]pply [S]kip [E]dit [Q]uit
```

## Options

| Option | Description |
|--------|-------------|
| `--interactive`, `-i` | Review each fix |
| `--category <cat>` | Specific category only |
| `--priority <level>` | Filter by priority |
| `--deep` | Use Fixer agent |
| `--dry-run` | Preview only |
| `--file <path>` | Specific file only |

## Integration

**Flow**: `/cw:review` → `/cw:fix` → Quality Gate → `/cw:review`
