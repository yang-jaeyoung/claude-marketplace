# Plans Directory Resolution

This document defines how CAW resolves the `plansDirectory` setting for Plan Mode integration.

## Settings Priority Order

Resolve `plansDirectory` by checking settings files in this order:

```
1. .claude/settings.local.json   (project local, highest priority)
2. .claude/settings.json         (project)
3. ~/.claude/settings.json       (global/user)
4. Default: ".claude/plans/"     (fallback)
```

## Resolution Procedure

### Step 1: Read Settings Files

```
1. Read `.claude/settings.local.json` → extract "plansDirectory"
2. If not found → Read `.claude/settings.json` → extract "plansDirectory"
3. If not found → Read `~/.claude/settings.json` → extract "plansDirectory"
4. If not found → Use default ".claude/plans/"
```

### Step 2: Path Interpretation

| Path Type | Handling | Example |
|-----------|----------|---------|
| Absolute path (starts with `/`) | Use as-is | `/home/user/plans/` |
| Relative path | Resolve from project root | `.plans/` → `{project_root}/.plans/` |
| Default | Project root relative | `.claude/plans/` |

### Step 3: Validation

After resolving the path:
1. Check if directory exists (don't create if missing)
2. If directory doesn't exist, note for reporting
3. Proceed to plan file search regardless

## Plan File Search Order

After resolving `plansDirectory`, search for plan files in this order:

```
1. {plansDirectory}/current.md        # Explicitly marked current plan
2. {plansDirectory}/*.md              # All plans in configured directory
3. .claude/plan.md                    # Legacy location (ALWAYS check)
4. plan.md, PLAN.md                   # Project root
5. docs/plan.md                       # Documentation folder
```

**Important**: Always check `.claude/plan.md` for backward compatibility, even when `plansDirectory` is configured differently.

## Implementation Example

```markdown
## Resolve plansDirectory

1. **Check settings files** (priority order):
   - Read `.claude/settings.local.json`:
     - If exists and has "plansDirectory" → use that value
   - Else Read `.claude/settings.json`:
     - If exists and has "plansDirectory" → use that value
   - Else Read `~/.claude/settings.json`:
     - If exists and has "plansDirectory" → use that value
   - Else → use default ".claude/plans/"

2. **Interpret path**:
   - If starts with "/" → absolute, use as-is
   - Else → resolve relative to project root

3. **Search for plans**:
   - Glob: {resolved_plansDirectory}/*.md
   - Glob: .claude/plan.md (legacy, always)
   - Glob: plan.md, PLAN.md (project root)
```

## Settings File Format

Expected structure in settings files:

```json
{
  "plansDirectory": ".plans/"
}
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Settings file doesn't exist | Skip to next in priority chain |
| Settings file is invalid JSON | Log warning, skip to next |
| plansDirectory key missing | Skip to next in priority chain |
| Resolved directory doesn't exist | Continue with search (may find no files) |
| Permission denied reading settings | Log warning, use default |

## Reporting

When reporting plan detection results, include:

```markdown
### Plan Detection

| Setting | Value |
|---------|-------|
| plansDirectory Source | `.claude/settings.local.json` / default |
| Resolved Path | `.plans/` |
| Plans Found | 2 files |

Files:
- .plans/auth-implementation.md (active)
- .claude/plan.md (legacy)
```

## Usage in Agents/Commands

Reference this document when implementing plan detection:

- **Bootstrapper Agent**: Step 4 (Detect Existing Plans)
- **/cw:start**: Mode 2 (Import from Plan Mode)
- **plan-detector Skill**: Step 1 (Detect Plan File)
