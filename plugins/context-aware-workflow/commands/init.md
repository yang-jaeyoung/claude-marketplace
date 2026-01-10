---
description: Initialize CAW environment without starting a task. Sets up .caw/ workspace, detects project context, and prepares for workflow.
---

# /caw:init - Environment Initialization

Initialize the CAW environment without starting a planning workflow.

## Usage

```bash
# Basic initialization
/caw:init

# Force reset and reinitialize
/caw:init --reset

# Initialize with specific project type hint
/caw:init --type nodejs

# Verbose mode for debugging
/caw:init --verbose
/caw:init -v

# Quiet mode (errors only)
/caw:init --quiet
/caw:init -q

# Machine-readable JSON output
/caw:init --json
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--reset` | | Archive existing state and reinitialize |
| `--type <type>` | | Hint project type (nodejs, python, rust, go, java) |
| `--verbose` | `-v` | Show detailed step-by-step logging |
| `--quiet` | `-q` | Show only errors |
| `--json` | | Output machine-readable JSON |

## Behavior

### Standard Initialization

When invoked:

1. **Invoke Bootstrapper Agent** using Task tool with `subagent_type="caw:bootstrapper"`
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

### Already Initialized

If `.caw/context_manifest.json` already exists:

```
Environment already initialized.

Current Status:
- Project Type: nodejs
- Active Files: 3
- Last Updated: 2024-01-15

Use /caw:init --reset to reinitialize.
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
| Existing Plans | Found `.claude/plan.md` |

### Next Steps
- `/caw:start "task description"` - Start planning a task
- `/caw:start --from-plan` - Import existing plan
- `/caw:context` - View current context
```

## When to Use

| Scenario | Command |
|----------|---------|
| New project, just want to set up CAW | `/caw:init` |
| Want to start working on a task | `/caw:start "task"` (auto-inits) |
| Reset after major project changes | `/caw:init --reset` |
| Check if initialized | `/caw:status` |
| Debug initialization issues | `/caw:init --verbose` |
| CI/CD automation | `/caw:init --json` |
| Minimal output in scripts | `/caw:init --quiet` |

## Integration

- **Bootstrapper Agent**: This command directly invokes the Bootstrapper
- **/caw:start**: Automatically calls init if not initialized
- **/caw:status**: Shows initialization state
