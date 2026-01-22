# Module Context

**Module:** MSSQL Plugin
**Role:** SQL Server connectivity for Claude Code via MCP protocol.
**Tech Stack:** TypeScript, Node.js, `@modelcontextprotocol/sdk`, `mssql`, Zod.

## Dependencies

- MCP Server: `./mcp-server/` (TypeScript)
- Commands: `./commands/*.md` (Markdown)
- Skills: `./skills/` (Optional)

---

# Operational Commands

```bash
cd mcp-server

# Install dependencies
npm install

# Build TypeScript
npm run build

# Development mode (watch)
npm run dev

# Run tests
npm test
```

---

# Implementation Patterns

## Plugin Structure

```
mssql/
  .claude-plugin/plugin.json  # MCP server configuration
  README.md                   # Usage documentation
  commands/                   # Slash commands
    query.md                  # /mssql:query
    tables.md                 # /mssql:tables
    schema.md                 # /mssql:schema
    procedures.md             # /mssql:procedures
    execute.md                # /mssql:execute
  mcp-server/                 # TypeScript MCP server
    src/
      index.ts                # Entry point
      connection.ts           # Connection pool management
      types.ts                # Type definitions
      tools/                  # MCP tool implementations
      utils/                  # Shared utilities
```

## Environment Variables

Required in plugin.json `mcpServers.mssql.env`:
- `MSSQL_SERVER` — Server hostname
- `MSSQL_DATABASE` — Database name
- `MSSQL_TRUST_CERT` — Trust server certificate (optional)
- `MSSQL_QUERY_TIMEOUT` — Query timeout in ms (optional)

---

# Local Golden Rules

## Do's

- **DO** validate all SQL inputs using Zod schemas.
- **DO** handle connection errors gracefully with meaningful messages.
- **DO** use parameterized queries to prevent SQL injection.
- **DO** implement connection pooling for performance.
- **DO** return structured JSON results for model consumption.

## Don'ts

- **DON'T** hardcode database credentials; use environment variables.
- **DON'T** expose destructive operations (DROP, TRUNCATE) without confirmation.
- **DON'T** allow arbitrary SQL execution without input validation.
- **DON'T** log sensitive query parameters or results.

---

# Context Map

- **[MCP Server Implementation](./mcp-server/AGENTS.md)** — TypeScript source code and patterns.
