---
description: Add MCP server to Codex CLI
argument-hint: "<name> [--url <url>]"
allowed-tools: ["Bash"]
---

# Codex MCP Add

Add a new MCP (Model Context Protocol) server to Codex CLI configuration.

## Instructions

1. Parse the arguments:
   - First argument: server name
   - `--url <url>`: Optional server URL

2. Run the Codex MCP add command:

```bash
codex mcp add <name> --url <url>
```

Or for local servers:
```bash
codex mcp add <name>
```

3. Display the result to the user

## Options

- Name: Unique identifier for the MCP server
- URL: Server endpoint (optional for local servers)

## Usage Examples

```
/codex:mcp-add myserver --url https://mcp.example.com
/codex:mcp-add local-tools
/codex:mcp-add github-tools --url https://mcp.github.io/api
```

## Notes

- MCP servers extend Codex with additional tools
- Server names must be unique
- Use `/codex:mcp-list` to view configured servers
- This is an experimental feature
- Consult MCP server documentation for specific configuration
