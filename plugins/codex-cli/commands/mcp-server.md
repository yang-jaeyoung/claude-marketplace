---
description: Start Codex as MCP server for multi-agent workflows
argument-hint: "[--inspector]"
allowed-tools: ["Bash"]
---

# Codex MCP Server

Start Codex CLI as an MCP server for integration with agent frameworks like OpenAI Agents SDK.

## Instructions

1. Check the arguments:
   - If `--inspector` is provided, run with MCP Inspector
   - Otherwise, run basic MCP server

2. Run the appropriate command:

**Basic MCP server:**
```bash
codex mcp-server
```

**With MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector codex mcp-server
```

3. The server will expose two tools:
   - `codex`: Initiates a Codex session
   - `codex-reply`: Continues an existing session using threadId

## Options

- `--inspector`: Run with MCP Inspector for debugging and testing

## Usage Examples

```
/codex:mcp-server
/codex:mcp-server --inspector
```

## MCP Tools Reference

### codex tool
Initiates a Codex session with configuration:
- `prompt`: Initial user prompt (required)
- `approval-policy`: untrusted, on-request, on-failure, never
- `sandbox`: read-only, workspace-write, danger-full-access
- `model`: Override model (e.g., gpt-5.2, gpt-5.2-codex)
- `base-instructions`: Custom instruction set
- `cwd`: Working directory

### codex-reply tool
Continues an existing session:
- `prompt`: Next user message (required)
- `threadId`: Thread identifier from prior response (required)

## Notes

- MCP server maintains conversation state across multiple agent turns
- Thread-based continuity allows agents to reference prior context
- Use with OpenAI Agents SDK for multi-agent workflows
- Long-running server - use Ctrl+C to stop
