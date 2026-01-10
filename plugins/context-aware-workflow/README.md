# Context-Aware Workflow (CAW)

Context-aware workflow orchestration plugin for Claude Code. Acts as a **Context-Aware Project Manager** that enforces structured workflows while collaborating interactively with developers.

## Philosophy

- **Hybrid Automation**: Combines natural language interface with rigorous programmatic logic
- **Human-in-the-Loop**: Propose → Review → Execute pattern
- **Context Engineering**: Active/Project/Archived tiered context management
- **Plan Mode Integration**: Seamlessly imports existing Claude Code plans

## Features

### MVP (v0.1.0)

- `/caw:init` - Initialize CAW environment (standalone setup)
- `/caw:start` - Initialize workflow with task description or import Plan Mode plans
- **Bootstrapper Agent** - Environment initialization and project detection
- **Planner Agent** - Analyzes requirements and generates structured `task_plan.md`
- **ContextManager Skill** - Intelligent context file management (pack, prune, search)
- **Workflow Hooks** - Plan detection and coding-without-plan warnings

## Installation

```bash
# Option 1: Use directly
claude --plugin-dir /path/to/context-aware-workflow

# Option 2: Copy to project
cp -r context-aware-workflow /your/project/.claude-plugin/
```

## Usage

### Initialize Environment (Optional)

```bash
# Initialize CAW environment only
/caw:init

# Reset and reinitialize
/caw:init --reset
```

### Start a New Workflow

```bash
# With task description (auto-initializes if needed)
/caw:start "Implement user authentication with JWT"

# Import from Plan Mode
/caw:start --from-plan

# Specify plan file
/caw:start --plan-file .claude/plan.md
```

### Workflow Loop

1. **Bootstrap**: Bootstrapper initializes `.caw/` environment (auto on first run)
2. **Discovery**: Planner Agent asks clarifying questions
3. **Planning**: Generates `task_plan.md` in `.caw/`
4. **Execution**: Code with plan-aware hooks (warnings if no plan exists)
5. **Review**: Manual review of implementation

## Generated Artifacts

| File | Purpose |
|------|---------|
| `.caw/task_plan.md` | Current task plan |
| `.caw/context_manifest.json` | Active/Packed/Ignored file tracking |
| `.caw/sessions/` | Session state snapshots |
| `.caw/archives/` | Completed/abandoned plans |

## Configuration

Create `.claude/caw.local.md` for project-specific settings (optional):

```markdown
# CAW Local Settings

## Context Preferences
- Max active files: 10
- Auto-prune after: 5 turns

## Plan Preferences
- Default plan location: .claude/plan.md
- Auto-detect plans: true
```

## Roadmap

### Completed (v1.2.1)
- [x] Quick Fix skill for auto-fixable issues
- [x] Reviewer JSON output (`last_review.json`)
- [x] JSON schema for Reviewer → Fixer data flow

### Completed (v1.2.0)
- [x] Fixer Agent for intelligent code fixes
- [x] `/caw:fix` - Review result auto/manual fixing

### Completed (v1.1.0)
- [x] Bootstrapper Agent for environment initialization
- [x] `/caw:init` - Environment setup command

### Completed (v1.0.0)
- [x] Builder Agent for TDD execution
- [x] Reviewer Agent for code quality review
- [x] `/caw:status` - Workflow state display
- [x] `/caw:review` - Plan/code review trigger
- [x] ComplianceChecker Agent for guideline compliance

### Planned
- [ ] VS Code extension integration
- [ ] GitHub Actions integration
- [ ] Multi-project support

## License

MIT
