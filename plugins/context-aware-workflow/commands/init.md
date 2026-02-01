---
description: Initialize CAW environment without starting a task. Sets up .caw/ workspace, detects project context, and prepares for workflow.
argument-hint: "[--reset] [--with-guidelines] [--deep] [--type <type>] [--verbose]"
---

# /cw:init - Environment Initialization

Initialize the CAW environment without starting a planning workflow.

## Usage

```bash
/cw:init                          # Basic initialization
/cw:init --reset                  # Force reset and reinitialize
/cw:init --type nodejs            # Hint project type
/cw:init --with-guidelines        # Generate GUIDELINES.md
/cw:init --deep                   # Generate hierarchical AGENTS.md files
/cw:init --with-guidelines --deep # Full setup
/cw:init --verbose | -v           # Detailed logging
/cw:init --quiet | -q             # Errors only
/cw:init --json                   # Machine-readable output
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--reset` | | Archive existing state and reinitialize |
| `--type <type>` | | Hint project type (nodejs, python, rust, go, java) |
| `--with-guidelines` | `-g` | Generate `.caw/GUIDELINES.md` with workflow rules |
| `--deep` | `-d` | Generate hierarchical `AGENTS.md` files (deepinit) |
| `--verbose` | `-v` | Detailed step-by-step logging |
| `--quiet` | `-q` | Show only errors |
| `--json` | | Output machine-readable JSON |
| `--serena-sync` | | Save onboarding to Serena memory |
| `--from-serena` | | Restore context from Serena (skip detection) |
| `--no-serena` | | Skip Serena integration |

## Workflow

1. **Invoke Bootstrapper** via Task tool (`subagent_type="cw:bootstrapper"`)
2. Bootstrapper creates `.caw/` structure, detects project, generates `context_manifest.json`

## Modes

| Mode | Behavior |
|------|----------|
| **Standard** | Create .caw/, detect project, generate manifest |
| **Reset** | Archive existing to `.caw/archives/`, reinitialize |
| **Guidelines** | Generate `.caw/GUIDELINES.md` from template |
| **Deep** | Create `AGENTS.md` in each significant directory |

## Deep Init

- Creates `AGENTS.md` in each significant directory
- Excludes: node_modules, .git, dist, build, __pycache__, .venv
- Processes bottom-up (children before parents)
- Preserves content below `<!-- MANUAL: -->` marker

## Output

```markdown
## CAW Environment Initialized

| Item | Status |
|------|--------|
| Workspace | `.caw/` created |
| Project Type | Node.js (TypeScript) |
| Guidelines | ✅ Generated (--with-guidelines) |
| Deep Init | ✅ 12 AGENTS.md files (--deep) |

### Next Steps
- `/cw:start "task"` - Start planning
- `/cw:start --from-plan` - Import existing plan
- `/cw:context` - View current context
```

## When to Use

| Scenario | Command |
|----------|---------|
| New project setup | `/cw:init` |
| Start working on task | `/cw:start` (auto-inits) |
| Reset after major changes | `/cw:init --reset` |
| Generate workflow docs | `/cw:init --with-guidelines` |
| Document codebase for AI | `/cw:init --deep` |
| Full setup | `/cw:init --with-guidelines --deep` |

## Integration

- **Bootstrapper Agent**: Invoked directly
- **/cw:start**: Auto-calls init if needed
- **/cw:status**: Shows initialization state
