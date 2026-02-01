# Claude Marketplace

A plugin marketplace for Claude Code. Provides plugins to extend and automate AI-powered development workflows.

## Highlights

- **Workflow Automation** - Structured development process from task planning to review
- **AI Tool Integration** - Seamless integration with various AI CLI tools like Gemini and Codex
- **Productivity Boost** - Automate repetitive tasks and apply quality gates

## Available Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [cw](./plugins/context-aware-workflow) | 2.0.0 | Context-aware workflow orchestration - Plan Mode integration, automatic task planning, QA loops, Ralph Loop improvement cycles, model routing |
| [codex-cli](./plugins/codex-cli) | 1.0.0 | Codex CLI integration - code review, auto execution, session management, cloud tasks |
| [gemini-cli](./plugins/gemini-cli) | 1.0.0 | Gemini CLI integration - code review, commit message generation, documentation, release notes |

## Quick Start

```bash
# Add marketplace
claude plugins add github:jyyang/claude-marketplace

# Install plugins
claude plugins install cw
claude plugins install codex-cli
claude plugins install gemini-cli
```

## Plugin Highlights

### Context-Aware Workflow (cw)

Structured development workflow orchestration:

```bash
/cw:start "Implement JWT auth"    # Generate task plan
/cw:loop "Fix bug"                # Auto-repeat until complete
/cw:auto "Add logout button"      # Run full workflow automatically
```

### Codex CLI

OpenAI Codex CLI integration:

```bash
/codex:code How to implement quicksort?
/codex:review src/main.py
/codex:auto Fix all linting errors
```

### Gemini CLI

Google Gemini CLI integration:

```bash
/gemini:review              # Review staged changes
/gemini:commit              # Generate commit message
/gemini:docs src/utils.py   # Generate documentation
```

## Manual Installation

```bash
git clone https://github.com/jyyang/claude-marketplace.git
cp -r claude-marketplace/plugins/<plugin-name> ~/.claude/plugins/
```

## Contributing

1. Create a new folder under `plugins/`
2. Add `.claude-plugin/plugin.json` metadata
3. Configure commands, skills, agents, and hooks
4. Update `marketplace.json`
5. Submit a pull request

## License

MIT License
