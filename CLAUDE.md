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

> ⚠️ **중요**: plugin.json은 **아래 4개 필드만** 허용됩니다. 다른 필드 추가 시 플러그인 로드 실패!

```json
{
  "name": "lowercase-with-hyphens",
  "version": "1.0.0",
  "description": "Plugin description",
  "mcpServers": { }
}
```

**허용되는 필드 (Allowed fields only):**
| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | ✅ | 플러그인 이름 (소문자, 하이픈만 허용) |
| `version` | ✅ | 시맨틱 버전 (예: "1.0.0") |
| `description` | ✅ | 플러그인 설명 |
| `mcpServers` | ❌ | MCP 서버 설정 (선택) |

**❌ 지원되지 않는 필드 (절대 사용 금지):**
- `author` - 지원 안 됨
- `features` - 지원 안 됨
- `commands` - 지원 안 됨 (commands는 `commands/*.md` 파일로 자동 인식)
- `agents` - 지원 안 됨 (agents는 `agents/*.md` 파일로 자동 인식)
- `skills` - 지원 안 됨 (skills는 `skills/*/SKILL.md` 파일로 자동 인식)
- `hooks` - 지원 안 됨 (hooks는 `hooks/hooks.json` 파일로 정의)
- 기타 커스텀 필드 - 모두 validation error 발생

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
- `type: "command"` - Bash 명령 실행 (모든 hook event에서 지원)
- `type: "prompt"` - LLM 기반 평가 (**`Stop`과 `SubagentStop`에서만 지원**)

> ⚠️ **주의**: `type: "prompt"`는 `Stop`과 `SubagentStop` hook에서만 사용 가능합니다.
> SessionStart 등 다른 이벤트에서 사용하면 "hook error"가 발생합니다.

Available hook events: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `Notification`, `Stop`, `SubagentStop`, `PreCompact`, `Setup`, `SessionStart`, `SessionEnd`.

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
