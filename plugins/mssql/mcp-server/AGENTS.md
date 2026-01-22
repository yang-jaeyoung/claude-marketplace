# Module Context

**Module:** MSSQL MCP Server
**Role:** TypeScript MCP server providing SQL Server tools to Claude.
**Tech Stack:** Node.js 20+, TypeScript 5.6, `@modelcontextprotocol/sdk`, `mssql`, Zod, Vitest.

## Dependencies

- `@modelcontextprotocol/sdk` — MCP protocol implementation
- `mssql` — SQL Server driver with Windows Auth support
- `zod` — Schema validation for tool inputs

---

# Operational Commands

```bash
# Install dependencies
npm install

# Build TypeScript to dist/
npm run build

# Development with watch mode
npm run dev

# Run tests
npm test
npm run test:watch
npm run test:coverage
```

---

# Implementation Patterns

## Source Structure

```
src/
  index.ts          # Entry point, server setup, tool registration
  connection.ts     # Connection pool management, testConnection()
  types.ts          # Shared TypeScript interfaces
  tools/
    query.ts        # mssql_query tool
    tables.ts       # mssql_list_tables tool
    schema.ts       # mssql_get_schema tool
    procedures.ts   # mssql_list_procedures tool
    execute-proc.ts # mssql_execute_procedure tool
  utils/
    sql-parser.ts   # SQL parsing utilities
    error-handler.ts # Error formatting
```

## Tool Registration Pattern

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

export function registerMyTool(server: McpServer) {
  server.tool(
    'tool_name',
    'Tool description',
    z.object({ param: z.string() }).shape,
    async (params) => {
      // Implementation
      return {
        content: [{ type: 'text', text: 'result' }],
      };
    }
  );
}
```

## Error Handling Pattern

```typescript
try {
  const result = await executeQuery(sql);
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} catch (error) {
  return {
    content: [{ type: 'text', text: formatError(error) }],
    isError: true,
  };
}
```

---

# Testing Strategy

- **Framework:** Vitest
- **Unit Tests:** `src/utils/*.test.ts`
- **Test Pattern:** Co-locate tests with source files using `.test.ts` suffix

```bash
# Run specific test file
npx vitest run src/utils/sql-parser.test.ts
```

---

# Local Golden Rules

## Do's

- **DO** use `McpServer` from `@modelcontextprotocol/sdk/server/mcp.js`.
- **DO** use `StdioServerTransport` for CLI communication.
- **DO** define tool parameters with `z.object().shape` (not raw Zod schema).
- **DO** return `{ content: [{ type: 'text', text: '...' }] }` from tools.
- **DO** set `isError: true` in tool response when operation fails.
- **DO** handle graceful shutdown with `SIGINT`/`SIGTERM`.

## Don'ts

- **DON'T** import from `@modelcontextprotocol/sdk` directly; use subpaths.
- **DON'T** use CommonJS; this is an ESM project (`"type": "module"`).
- **DON'T** return raw objects from tools; always wrap in content array.
- **DON'T** forget `.js` extensions in imports (required for ESM).
