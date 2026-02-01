---
description: Manage context files - add, remove, pack, or view current context
argument-hint: "<show|add|remove|pack|prune> [options]"
---

# /cw:context - Context Management

Manage the context files tracked by the workflow.

## Usage

```bash
/cw:context show                    # Display current context
/cw:context add src/auth/*.ts       # Add files
/cw:context remove src/old.ts       # Remove files
/cw:context pack src/utils/         # Compress to interface-only
/cw:context prune                   # Remove stale files
/cw:context budget                  # Show token usage
```

## Context Tiers

| Tier | Description | Token Impact |
|------|-------------|--------------|
| **Active** | Files being modified | High (full content) |
| **Project** | Reference (read-only) | Medium |
| **Packed** | Interface summaries | Low |
| **Archived** | Stored but not loaded | None |

## Commands

### show

```
📂 Current Context

🔴 Active: 3.6KB (~900 tokens)
  • src/auth/jwt.ts (2.1KB)
  • src/middleware/auth.ts (1.5KB)

🟡 Project: 4.0KB (~1000 tokens)
  • package.json, tsconfig.json, CLAUDE.md

🟢 Packed: 0.5KB (~125 tokens)
  • src/utils/helpers.ts → 12 exports

📊 Total: 8.1KB (~2025 tokens)
```

### add

```bash
/cw:context add src/auth/*.ts           # Glob pattern
/cw:context add src/auth/ --tier project # Specific tier
```

### pack

Compress to interface-only (signatures, no bodies):

```
📦 Packed: src/utils/helpers.ts
  Before: 5.2KB | After: 0.3KB | Saved: 4.9KB
```

### prune

Remove files not accessed in N turns:

```bash
/cw:context prune --threshold 3    # Custom threshold
/cw:context prune --dry-run        # Preview only
```

### budget

```bash
/cw:context budget              # Show usage
/cw:context budget --limit 5000 # Set limit
```

## Manifest

State tracked in `.caw/context_manifest.json`:
- Files by tier with reasons and timestamps
- Token usage statistics

## Auto-Updates

| Event | Action |
|-------|--------|
| File edited | Move to Active tier |
| File read | Update last_accessed |
| Step completed | Add files from Notes |
| Threshold reached | Suggest pruning |

## Best Practices

| Action | When |
|--------|------|
| **Add** | Files you're modifying, dependencies |
| **Pack** | Large utilities, type files |
| **Prune** | After completing phase |
| **Remove** | Superseded implementations |

## Integration

- **Manifest**: `.caw/context_manifest.json`
- **Hooks**: PostToolUse updates context
- **Commands**: Works with `/cw:status`, `/cw:next`
