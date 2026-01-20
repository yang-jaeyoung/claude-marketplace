---
description: Initialize CAW environment without starting a task. Sets up .caw/ workspace, detects project context, and prepares for workflow.
argument-hint: "[--reset] [--type <type>] [--verbose]"
---

# /cw:init - Environment Initialization

Initialize the CAW environment without starting a planning workflow.

## Usage

```bash
# Basic initialization
/cw:init

# Force reset and reinitialize
/cw:init --reset

# Initialize with specific project type hint
/cw:init --type nodejs

# Verbose mode for debugging
/cw:init --verbose
/cw:init -v

# Quiet mode (errors only)
/cw:init --quiet
/cw:init -q

# Machine-readable JSON output
/cw:init --json
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--reset` | | Archive existing state and reinitialize |
| `--type <type>` | | Hint project type (nodejs, python, rust, go, java) |
| `--verbose` | `-v` | Show detailed step-by-step logging |
| `--quiet` | `-q` | Show only errors |
| `--json` | | Output machine-readable JSON |
| `--serena-sync` | | Sync initialization with Serena memory (save onboarding) |
| `--from-serena` | | Restore context from Serena memory only (skip detection) |
| `--no-serena` | | Skip Serena integration (local-only mode) |

## Behavior

### Standard Initialization

When invoked:

1. **Invoke Bootstrapper Agent** using Task tool with `subagent_type="cw:bootstrapper"`
2. Bootstrapper will:
   - Check if `.caw/` already exists
   - Create directory structure if needed
   - Analyze project to detect type and conventions
   - Find existing Plan Mode outputs
   - Generate `context_manifest.json`
   - Report initialization status

### Reset Mode (--reset)

When invoked with `--reset`:

1. **Archive existing state** to `.caw/archives/`
2. **Clear session data**
3. **Reinitialize** from scratch
4. Useful when:
   - Project structure changed significantly
   - Want to start fresh
   - Manifest became corrupted

### Serena Integration (NEW)

#### With `--serena-sync`

1. Run standard initialization
2. After manifest creation, save to Serena:
   ```
   write_memory("project_onboarding", {
     project_type, frameworks, conventions, key_files
   })
   ```
3. Report: "Serena onboarding saved for future sessions"

#### With `--from-serena`

1. Skip local detection
2. Restore from Serena memory:
   ```
   read_memory("project_onboarding")
   ```
3. Pre-populate `context_manifest.json` from Serena
4. Report: "Context restored from Serena memory"

#### With `--no-serena`

1. Skip all Serena operations
2. Local-only initialization
3. Useful for offline work or when Serena unavailable

### Already Initialized

If `.caw/context_manifest.json` already exists:

```
Environment already initialized.

Current Status:
- Project Type: nodejs
- Active Files: 3
- Last Updated: 2024-01-15
- Serena Onboarding: ✅ Saved

Use /cw:init --reset to reinitialize.
```

## Output

After successful initialization:

```markdown
## CAW Environment Initialized

| Item | Status |
|------|--------|
| Workspace | `.caw/` created |
| Project Type | Node.js (TypeScript) |
| Guidelines | Found `GUIDELINES.md` |
| Plans Directory | `{resolved_plansDirectory}` |
| Existing Plans | Found in configured location |

### Next Steps
- `/cw:start "task description"` - Start planning a task
- `/cw:start --from-plan` - Import existing plan
- `/cw:context` - View current context
```

## When to Use

| Scenario | Command |
|----------|---------|
| New project, just want to set up CAW | `/cw:init` |
| Want to start working on a task | `/cw:start "task"` (auto-inits) |
| Reset after major project changes | `/cw:init --reset` |
| Check if initialized | `/cw:status` |
| Debug initialization issues | `/cw:init --verbose` |
| CI/CD automation | `/cw:init --json` |
| Minimal output in scripts | `/cw:init --quiet` |

## Integration

- **Bootstrapper Agent**: This command directly invokes the Bootstrapper
- **/cw:start**: Automatically calls init if not initialized
- **/cw:status**: Shows initialization state
