# Claude Marketplace

Personal Claude Code plugins marketplace by jyyang.

## Available Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [az-skill-pack](./plugins/az-skill-pack) | 1.0.0 | Brainstorming, security audits, documentation generation, and project analysis |
| [codex-cli](./plugins/codex-cli) | 1.0.0 | Codex CLI integration for Claude Code |
| [context-aware-workflow](./plugins/context-aware-workflow) | 1.8.0 | Context-aware workflow orchestration with Plan Mode integration |
| [gemini-cli](./plugins/gemini-cli) | 1.0.0 | Google Gemini CLI integration for code review and documentation |
| [intent-based-skills](./plugins/intent-based-skills) | 1.0.0 | Intent-based skill framework for consistent and verifiable task execution |
| [mssql](./plugins/mssql) | 1.0.0 | MS SQL Server integration with Windows Authentication |
| [rails8-hotwire](./plugins/rails8-hotwire) | 1.0.0 | Rails 8 + Hotwire full-stack development with specialized agents, hooks, and skills |

## Installation

### Using Claude Code CLI

```bash
# Add this marketplace
claude plugins add github:jyyang/claude-marketplace

# Install a specific plugin
claude plugins install codex-cli
```

### Manual Installation

1. Clone this repository
2. Copy the desired plugin folder to `~/.claude/plugins/`
3. Restart Claude Code

## Contributing

To add a new plugin:

1. Create a new folder under `plugins/`
2. Add `.claude-plugin/plugin.json` with plugin metadata
3. Add commands, skills, agents, or hooks as needed
4. Update `marketplace.json` with the new plugin entry
5. Submit a pull request

## License

MIT License
