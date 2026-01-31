# CLAUDE.min.md
<!-- AI-optimized compressed rules. Human-readable version: CLAUDE.md -->

## Core
- Monorepo: `plugins/*` installed via `claude plugins add github:jyyang/claude-marketplace`
- Registry: `.claude-plugin/marketplace.json`

## plugin.json
ONLY 4 fields allowed (others cause load failure):
```json
{"name":"lowercase-hyphens","version":"semver","description":"text","mcpServers":{}}
```
NEVER use: author,features,commands,agents,skills,hooks,keywords,category

## Cross-Platform (REQUIRED)
- Paths: Use `/` (auto-handled), `path.join()`, `os.path.join()`
- Commands: Use `python3` or `node` (NOT cat/rm/type/sh)
- Wrap paths: `"${CLAUDE_PLUGIN_ROOT}/path"`
- `${CLAUDE_PLUGIN_ROOT}`: runtime substitution, NOT env var

## Components (auto-detected)
| Type | Location | Key Fields |
|------|----------|------------|
| Commands | `commands/*.md` | description,allowed-tools,context,agent,model,hooks |
| Agents | `agents/*.md` | name,description,model(sonnet/opus/haiku),tools,mcp_servers |
| Skills | `skills/*/SKILL.md` | name,description,allowed-tools,context:fork |
| Hooks | `hooks/hooks.json` | PreToolUse,PostToolUse,Stop,Setup,SessionStart,etc |

## Agents Tiering
- Base: `<name>.md` (Sonnet)
- Fast: `<name>-haiku.md`
- Complex: `<name>-opus.md`

## Hooks
- `type:command` - all events
- `type:prompt` - ONLY Stop,SubagentStop

## MCP Server (REQUIRED)
Must have Setup hook for npm:
```json
{"hooks":{"Setup":[{"hooks":[{"type":"command","command":"cd \"${CLAUDE_PLUGIN_ROOT}\" && npm install --silent"}]}]}}
```

## Cache
Clear: `rm -rf ~/.claude/plugins/cache/<marketplace>/<plugin>/`

## Build
- mssql: `cd plugins/mssql/mcp-server && npm install && npm run build`
- tests: `cd plugins/context-aware-workflow && python -m pytest tests/`
