# Claude Marketplace

Personal Claude Code plugins marketplace by jyyang.

## Available Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [codex-cli](./plugins/codex-cli) | 1.0.0 | Codex CLI integration for Claude Code |
| [mssql](./plugins/mssql) | 1.0.0 | MS SQL Server integration with Windows Authentication |
| [context-aware-workflow](./plugins/context-aware-workflow) | 1.0.0 | Context-aware workflow orchestration with Plan Mode integration |

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
