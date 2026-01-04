# Context-Aware Workflow (CAW)

Context-aware workflow orchestration plugin for Claude Code. Acts as a **Context-Aware Project Manager** that enforces structured workflows while collaborating interactively with developers.

## Philosophy

- **Hybrid Automation**: Combines natural language interface with rigorous programmatic logic
- **Human-in-the-Loop**: Propose → Review → Execute pattern
- **Context Engineering**: Active/Project/Archived tiered context management
- **Plan Mode Integration**: Seamlessly imports existing Claude Code plans

## Features

### MVP (v0.1.0)

- `/caw:start` - Initialize workflow with task description or import Plan Mode plans
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

### Start a New Workflow

```bash
# With task description
/caw:start "Implement user authentication with JWT"

# Import from Plan Mode
/caw:start --from-plan

# Specify plan file
/caw:start --plan-file .claude/plan.md
```

### Workflow Loop

1. **Discovery**: Planner Agent asks clarifying questions
2. **Planning**: Generates `task_plan.md` in project root
3. **Execution**: Code with plan-aware hooks (warnings if no plan exists)
4. **Review**: Manual review of implementation

## Generated Artifacts

| File | Purpose |
|------|---------|
| `task_plan.md` | Current task plan (project root) |
| `.claude/context_manifest.json` | Active/Packed/Ignored file tracking |

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

- [ ] Builder Agent for TDD execution
- [ ] Reviewer Agent for guideline compliance
- [ ] `/caw:status` - Workflow state display
- [ ] `/caw:review` - Plan/code review trigger
- [ ] ComplianceChecker skill

## License

MIT
