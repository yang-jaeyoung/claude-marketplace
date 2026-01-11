# Module Context

**Module:** MSSQL MCP Server
**Role:** Provides Database connectivity and query capabilities to Claude via Model Context Protocol.
**Tech Stack:** Node.js, TypeScript, MCP SDK (`@modelcontextprotocol/sdk`), Zod.

# Operational Commands

## Build & Run
-   `npm install` — Install dependencies.
-   `npm run build` — Compile TypeScript to `dist/`.
-   `npm run dev` — Run in watch mode with `tsx`.

# Implementation Patterns

## MCP Server Structure
-   Use `McpServer` class from the SDK.
-   Define tools using `server.tool()` with `z.object()` schemas.
-   Keep tool implementations purely functional; avoid heavy state where possible.

## File Naming
-   `index.ts`: Entry point.
-   `*.ts`: Lowercase with underscores or hyphens preferred for internal modules.

# Local Golden Rules

## Do's
-   **DO** validate all inputs using Zod schemas.
-   **DO** handle SQL connection errors gracefully and return meaningful error messages to the model.
-   **DO** use `StdioServerTransport` for local communication.

## Don'ts
-   **DON'T** hardcode database credentials. Use environment variables.
-   **DON'T** expose destructive SQL commands (DROP, DELETE) without explicit confirmation or safety flags if possible.
