# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugins marketplace - a monorepo containing multiple plugins that extend Claude Code functionality. Plugins are installed via `claude plugins add github:jyyang/claude-marketplace`.

## Repository Structure

```
claude-marketplace/
├── .claude-plugin/marketplace.json    # Registry of all plugins
└── plugins/
    ├── codex-cli/                     # Pure markdown plugin (commands only)
    ├── mssql/                         # MCP server plugin (TypeScript)
    └── context-aware-workflow/        # Full-featured plugin (agents, skills, hooks, commands)
```

## Build Commands

### mssql MCP Server
```bash
cd plugins/mssql/mcp-server
npm install
npm run build        # Compiles TypeScript to dist/
npm run dev          # Watch mode with tsx
```

### context-aware-workflow Tests
```bash
cd plugins/context-aware-workflow
python -m pytest tests/                           # Run all tests
python tests/test_plugin_structure.py             # Plugin structure validation
```

## Plugin Architecture

### Plugin Types

1. **Markdown-only plugins** (codex-cli): Commands defined as `.md` files with YAML frontmatter
2. **MCP server plugins** (mssql): TypeScript MCP server + optional commands/skills
3. **Full-featured plugins** (context-aware-workflow): Agents, skills, hooks, and commands

### Required Structure

Every plugin must have:
- `.claude-plugin/plugin.json` - Plugin metadata (name, version, description)
- `README.md` - Usage documentation

### plugin.json Schema
```json
{
  "name": "lowercase-with-hyphens",
  "version": "1.0.0",
  "description": "Plugin description",
  "mcpServers": { }  // Optional: MCP server configuration
}
```

### Component Patterns

**Commands** (`commands/*.md`):
```yaml
---
description: Short description shown in help
argument-hint: "<arg_name>"        # Optional
allowed-tools: ["Bash", "Read"]    # Optional tool restrictions
---
# Command instructions in markdown
```

**Agents** (`agents/*.md`):
```yaml
---
name: "AgentName"
description: "What the agent does"
model: sonnet                      # sonnet, opus, or haiku
tier: sonnet                       # Optional: complexity tier indicator
whenToUse: |
  Usage guidance with <example> blocks
tools:
  - Read
  - Write
  - Glob
mcp_servers:
  - serena
  - sequential
---
# Agent system prompt
```

**Tiered Agents** (model routing pattern):
- Base agent: `<name>.md` (default tier, usually Sonnet)
- Lower tier: `<name>-haiku.md` (fast, simple tasks)
- Higher tier: `<name>-opus.md` (complex, security-critical tasks)

Selection is automatic based on task complexity scoring (0.0-1.0).

**Skills** (`skills/*/SKILL.md`):
```yaml
---
name: skill-name
description: What the skill does
allowed-tools: Read, Glob, Grep
forked-context: true               # Runs in isolated context
---
# Skill behavior instructions
```

**Hooks** (`hooks/hooks.json`):
```json
{
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "prompt", "prompt": "..." }] }],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

## MCP Server Development

MCP servers use `@modelcontextprotocol/sdk` with this pattern:

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const server = new McpServer({ name: 'server-name', version: '1.0.0' });

// Register tools with Zod schemas
server.tool('tool_name', 'description', z.object({ ... }).shape, async (params) => {
  return { content: [{ type: 'text', text: 'result' }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Adding a New Plugin

1. Create `plugins/<plugin-name>/`
2. Add `.claude-plugin/plugin.json`
3. Add `README.md`
4. Add components (commands, agents, skills, hooks, mcp-server)
5. Update `.claude-plugin/marketplace.json` at root

## Key Files Reference

- [marketplace.json](.claude-plugin/marketplace.json) - Plugin registry
- [mssql/index.ts](plugins/mssql/mcp-server/src/index.ts) - MCP server example
- [caw/planner.md](plugins/context-aware-workflow/agents/planner.md) - Agent example (Sonnet tier)
- [caw/planner-haiku.md](plugins/context-aware-workflow/agents/planner-haiku.md) - Tiered agent example (Haiku)
- [caw/start.md](plugins/context-aware-workflow/commands/start.md) - Command example
- [caw/reflect.md](plugins/context-aware-workflow/skills/reflect/SKILL.md) - Skill example (Ralph Loop)
- [caw/model-routing.md](plugins/context-aware-workflow/_shared/model-routing.md) - Model routing documentation
- [test_plugin_structure.py](plugins/context-aware-workflow/tests/test_plugin_structure.py) - Structure validation tests
