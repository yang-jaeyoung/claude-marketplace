---
description: Manage context files - add, remove, pack, or view current context
---

# /caw:context - Context Management

Manage the context files tracked by the workflow. Add, remove, pack, or view files in the current context.

## Usage

```bash
/caw:context show                    # Display current context
/caw:context add src/auth/*.ts       # Add files to active context
/caw:context remove src/old.ts       # Remove from context
/caw:context pack src/utils/         # Compress to interface-only
/caw:context prune                   # Remove stale files
/caw:context prune --threshold 3     # Custom staleness threshold
```

## Context Tiers

| Tier | Description | Token Impact |
|------|-------------|--------------|
| **Active** | Files being modified | High (full content) |
| **Project** | Reference files (read-only) | Medium |
| **Packed** | Interface summaries only | Low |
| **Archived** | Stored but not loaded | None |

## Commands

### show - Display Current Context

```bash
/caw:context show
```

**Output**:
```
📂 Current Context

══════════════════════════════════════════
🔴 Active Context (will be modified)
══════════════════════════════════════════
  • src/auth/jwt.ts (2.1KB)
    → Main JWT implementation
  • src/middleware/auth.ts (1.5KB)
    → Authentication middleware

  Subtotal: 3.6KB (~900 tokens)

══════════════════════════════════════════
🟡 Project Context (read-only reference)
══════════════════════════════════════════
  • package.json (1.2KB)
    → Dependencies and scripts
  • tsconfig.json (0.8KB)
    → TypeScript configuration
  • CLAUDE.md (2.0KB)
    → Project conventions

  Subtotal: 4.0KB (~1000 tokens)

══════════════════════════════════════════
🟢 Packed Context (interface only)
══════════════════════════════════════════
  • src/utils/helpers.ts → 12 exports
  • src/types/index.ts → 8 types

  Subtotal: 0.5KB (~125 tokens)

══════════════════════════════════════════
📊 Total Context: 8.1KB (~2025 tokens)
══════════════════════════════════════════

💡 Tips:
   • /caw:context pack <file> to reduce token usage
   • /caw:context prune to remove stale files
```

### add - Add Files to Context

```bash
/caw:context add src/auth/jwt.ts           # Single file
/caw:context add src/auth/*.ts             # Glob pattern
/caw:context add src/auth/ --tier project  # Specific tier
```

**Options**:
- `--tier active|project` - Which tier to add to (default: active)
- `--reason "description"` - Why this file is in context

**Output**:
```
✅ Added to Active Context

  + src/auth/jwt.ts (2.1KB)
  + src/auth/middleware.ts (1.5KB)

📊 Context updated: 8.1KB → 11.7KB (+3.6KB)

💡 Consider packing large utility files:
   /caw:context pack src/utils/
```

### remove - Remove Files from Context

```bash
/caw:context remove src/old.ts
/caw:context remove src/deprecated/
```

**Output**:
```
✅ Removed from Context

  - src/old.ts (was in Active)
  - src/deprecated/legacy.ts (was in Project)

📊 Context updated: 11.7KB → 8.5KB (-3.2KB)
```

### pack - Compress to Interface-Only

```bash
/caw:context pack src/utils/helpers.ts
/caw:context pack src/utils/          # Directory
```

**What Gets Packed**:
- Function signatures (no bodies)
- Class definitions (methods as signatures)
- Type/interface declarations
- Export statements

**Output**:
```
📦 Packed: src/utils/helpers.ts

Before: 5.2KB (full file)
After:  0.3KB (interfaces only)

Extracted:
  • function formatDate(date: Date, format?: string): string
  • function parseJSON<T>(json: string): T | null
  • class Logger { info(), error(), debug() }
  • type LogLevel = 'info' | 'warn' | 'error'

📊 Saved: 4.9KB (~1225 tokens)
```

### prune - Remove Stale Files

```bash
/caw:context prune                  # Default: 5 turns unused
/caw:context prune --threshold 3    # Custom threshold
/caw:context prune --dry-run        # Preview only
```

**Staleness Detection**:
- Files not accessed in N turns
- Files not referenced in .caw/task_plan.md
- Files not in recent git changes

**Output**:
```
🧹 Pruning Stale Context

Analyzing file usage...

Files to remove (not used in 5+ turns):
  ⚠️ src/deprecated/old-auth.ts (8 turns ago)
  ⚠️ tests/legacy.test.ts (6 turns ago)

Files to keep (referenced in .caw/task_plan.md):
  ✅ src/auth/jwt.ts
  ✅ src/middleware/auth.ts

Proceed with pruning? [y/N]
```

**With --dry-run**:
```
🔍 Prune Preview (dry run)

Would remove:
  • src/deprecated/old-auth.ts
  • tests/legacy.test.ts

Would keep:
  • src/auth/jwt.ts (in .caw/task_plan.md)
  • src/middleware/auth.ts (recently accessed)

Run without --dry-run to apply changes.
```

## Context Manifest

Context state is tracked in `.caw/context_manifest.json`:

```json
{
  "version": "1.0",
  "updated": "2024-01-15T14:30:00Z",
  "active_task": ".caw/task_plan.md",
  "files": {
    "active": [
      {
        "path": "src/auth/jwt.ts",
        "reason": "Main implementation",
        "added": "2024-01-15T14:00:00Z",
        "last_accessed": "2024-01-15T14:25:00Z"
      }
    ],
    "project": [
      {
        "path": "package.json",
        "reason": "Dependencies"
      }
    ],
    "packed": [
      {
        "path": "src/utils/helpers.ts",
        "summary": "12 exports: formatDate, parseJSON, Logger..."
      }
    ]
  },
  "stats": {
    "total_tokens": 2025,
    "active_tokens": 900,
    "project_tokens": 1000,
    "packed_tokens": 125
  }
}
```

## Automatic Context Updates

Context is automatically updated when:

| Event | Action |
|-------|--------|
| File edited | Move to Active tier |
| File read | Update last_accessed |
| Step completed | Add files from .caw/task_plan.md Notes |
| Session start | Load from manifest |
| Threshold reached | Suggest pruning |

## Token Budget Management

```bash
/caw:context budget              # Show token usage
/caw:context budget --limit 5000 # Set token limit
```

**Output**:
```
📊 Context Token Budget

Current usage: 2025 / 5000 tokens (40%)

By tier:
  🔴 Active:  900 tokens (45%)
  🟡 Project: 1000 tokens (50%)
  🟢 Packed:  125 tokens (6%)

⚠️ Approaching limit recommendations:
   • Pack src/utils/helpers.ts (save ~800 tokens)
   • Prune stale files (save ~500 tokens)
```

## Best Practices

### When to Add
- Files you're actively modifying
- Dependencies needed for understanding
- Configuration files for reference

### When to Pack
- Large utility files with many functions
- Type definition files
- Libraries you only reference

### When to Prune
- After completing a phase
- When switching focus areas
- When context feels cluttered

### When to Remove
- Files no longer relevant to task
- Superseded implementations
- Test files after tests pass

## Integration

- **Manifest**: `.caw/context_manifest.json`
- **Scripts**: `pack_context.py`, `prune_context.py`
- **Hooks**: PostToolUse updates context automatically
- **Commands**: Works with `/caw:status`, `/caw:next`
