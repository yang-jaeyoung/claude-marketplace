---
description: List configured MCP servers for Codex CLI
allowed-tools: ["Bash"]
---

# Codex MCP List

List all configured MCP (Model Context Protocol) servers for Codex CLI.

## Instructions

1. Run the Codex MCP list command:

```bash
codex mcp list
```

2. Display the list of configured servers to the user

## Output

The command shows:
- Server name
- Server URL/endpoint
- Connection status
- Available tools/resources

## Usage Examples

```
/codex:mcp-list
```

## Notes

- Lists all MCP servers configured in Codex CLI
- Shows connection status for each server
- Use `/codex:mcp-add` to add new servers
- This is an experimental feature
