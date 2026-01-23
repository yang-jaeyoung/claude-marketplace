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

## Cross-Platform Compatibility

> ⚠️ **Required**: All code, scripts, and hook commands must work on **macOS, Linux, and Windows**.

### Path Handling
| Item | Windows | macOS/Linux | Recommended |
|------|---------|-------------|-------------|
| Path separator | `\` | `/` | Use `/` (Node.js/Python handle automatically) |
| Path joining | Do not join directly | Do not join directly | Use `path.join()` or `os.path.join()` |

### Shell Commands
```json
// ❌ Platform-specific - Do not use
{ "command": "cat file.txt" }           // Unix only
{ "command": "type file.txt" }          // Windows only
{ "command": "rm -rf dist/" }           // Unix only

// ✅ Cross-platform - Use Python or Node.js
// ⚠️ Important: On macOS, `python` may be an alias not recognized in hooks → use `python3`
{ "command": "python3 -c \"print(open('file.txt').read())\"" }
{ "command": "node -e \"console.log(require('fs').readFileSync('file.txt', 'utf8'))\"" }
{ "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/cleanup.py\"" }
```

### Hook Script Guidelines
1. **Use Python/Node.js instead of shell scripts (.sh)** - `.sh` files cannot run directly on Windows
2. **Use `python3` command** - On macOS, `python` may be an alias not recognized in hook environments
3. **Handle spaces in paths** - Always wrap paths in quotes: `"${CLAUDE_PLUGIN_ROOT}/path"`
4. **Environment variable references**:
   - `$VAR` - Works only in Unix shells
   - `%VAR%` - Works only in Windows cmd
   - Recommended: Use `os.environ` or `process.env` within Python/Node.js

### Plugin Cache Notes
> ⚠️ **Important**: If changes are not reflected after modifying a plugin, you need to **clear the cache**

Claude Code caches installed plugins in `~/.claude/plugins/cache/`.
Even after modifying local or marketplace versions, the cached version may continue to be used.

```bash
# Clear specific plugin cache
rm -rf ~/.claude/plugins/cache/<marketplace-name>/<plugin-name>/

# Example: Clear context-aware-workflow cache
rm -rf ~/.claude/plugins/cache/jyyang-claude-marketplace/cw/

# Clear all cache (Warning: requires re-downloading all plugins)
rm -rf ~/.claude/plugins/cache/
```

After clearing the cache, restart Claude Code to load the latest version.

### Line Ending Handling
- Repositories should enforce LF via `.gitattributes`
- When writing text files in scripts, explicitly use `\n`

### Example: Cross-Platform Hook Script
```python
#!/usr/bin/env python3
# hooks/scripts/example.py
import os
import sys
from pathlib import Path

# Cross-platform path handling
plugin_root = Path(__file__).parent.parent.parent
config_file = plugin_root / "config" / "settings.json"

# Environment variable access
project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

print(f"Config: {config_file}")
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

> **📚 Official Documentation**: Always refer to the [Claude Code Plugins Documentation](https://code.claude.com/docs/en/plugins) and [Plugins Reference](https://code.claude.com/docs/en/plugins-reference.md) for the latest plugin development guidelines, API changes, and best practices.

### Plugin Types

1. **Markdown-only plugins** (codex-cli): Commands defined as `.md` files with YAML frontmatter
2. **MCP server plugins** (mssql): TypeScript MCP server + optional commands/skills
3. **Full-featured plugins** (context-aware-workflow): Agents, skills, hooks, and commands

### Required Structure

Every plugin must have:
- `.claude-plugin/plugin.json` - Plugin metadata (name, version, description)
- `README.md` - Usage documentation

### plugin.json Schema

> ⚠️ **Important**: plugin.json only allows **the 4 fields below**. Adding other fields will cause plugin load failure!

```json
{
  "name": "lowercase-with-hyphens",
  "version": "1.0.0",
  "description": "Plugin description",
  "mcpServers": { }
}
```

**Allowed fields only:**
| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Plugin name (lowercase and hyphens only) |
| `version` | ✅ | Semantic version (e.g., "1.0.0") |
| `description` | ✅ | Plugin description |
| `mcpServers` | ❌ | MCP server configuration (optional) |

**❌ Unsupported fields (never use):**
- `author` - Not supported
- `features` - Not supported
- `commands` - Not supported (commands are auto-detected from `commands/*.md` files)
- `agents` - Not supported (agents are auto-detected from `agents/*.md` files)
- `skills` - Not supported (skills are auto-detected from `skills/*/SKILL.md` files)
- `hooks` - Not supported (hooks are defined in `hooks/hooks.json` file)
- Other custom fields - All cause validation errors

### Component Patterns

**Commands** (`commands/*.md`):
> See the [official Slash Commands documentation](https://code.claude.com/docs/en/slash-commands.md) for the latest frontmatter options and features.

```yaml
---
description: Short description shown in help
argument-hint: "<arg_name>"        # Optional: hint shown during autocomplete
allowed-tools: ["Bash", "Read"]    # Optional: tool restrictions
context: fork                      # Optional: run in forked sub-agent context
agent: general-purpose             # Optional: agent type when context: fork
model: claude-sonnet-4-20250514    # Optional: specific model string
disable-model-invocation: false    # Optional: prevent Skill tool invocation
hooks:                             # Optional: command-scoped hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
          once: true               # Run only once per session
---
# Command instructions in markdown
```

**Agents** (`agents/*.md`):
> See the [official Sub-agents documentation](https://code.claude.com/docs/en/sub-agents.md) for the latest agent configuration options and best practices.

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
> See the [official Skills documentation](https://code.claude.com/docs/en/skills.md) for the latest configuration options and best practices.

```yaml
---
name: skill-name
description: What the skill does
allowed-tools: Read, Glob, Grep
context: fork                      # Runs in isolated context (replaces forked-context)
---
# Skill behavior instructions
```

**Hooks** (`hooks/hooks.json`):
> See the [official Hooks documentation](https://code.claude.com/docs/en/hooks.md) and [Hooks Guide](https://code.claude.com/docs/en/hooks-guide.md) for the latest hook events and configuration options.

```json
{
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "echo '...'" }] }],
    "PreToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "..." }] }],
    "PostToolUse": [...],
    "Notification": [...],
    "Stop": [{ "hooks": [{ "type": "prompt", "prompt": "..." }] }]
  }
}
```

**Hook Types**:
- `type: "command"` - Execute bash command (supported in all hook events)
- `type: "prompt"` - LLM-based evaluation (**only supported in `Stop` and `SubagentStop`**)

> ⚠️ **Note**: `type: "prompt"` can only be used in `Stop` and `SubagentStop` hooks.
> Using it in other events like SessionStart will cause a "hook error".

Available hook events: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `Notification`, `Stop`, `SubagentStop`, `PreCompact`, `Setup`, `SessionStart`, `SessionEnd`.

**Plugin Path Reference (`${CLAUDE_PLUGIN_ROOT}`)**:

> ⚠️ **Important**: `${CLAUDE_PLUGIN_ROOT}` is not an environment variable but a **special variable that Claude Code substitutes at runtime**.

```json
// ✅ Correct usage - use directly in command string
{
  "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/my_script.py\""
}

// ❌ Incorrect usage - accessing as environment variable in Python code
{
  "command": "python -c \"import os; os.environ.get('CLAUDE_PLUGIN_ROOT', '.')\""
}
```

| Variable | Usage Location | Description |
|----------|----------------|-------------|
| `${CLAUDE_PLUGIN_ROOT}` | command string | Plugin root path (runtime substitution) |
| `$CLAUDE_PROJECT_DIR` | command string | Project root path (environment variable) |

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

> See the [official plugins quickstart guide](https://code.claude.com/docs/en/plugins) for detailed instructions.

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
