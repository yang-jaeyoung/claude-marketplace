import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { registerQueryTool } from './tools/query.js';
import { registerTablesTool } from './tools/tables.js';
import { registerSchemaTool } from './tools/schema.js';
import { registerProceduresTool } from './tools/procedures.js';
import { registerExecuteProcTool } from './tools/execute-proc.js';
import { testConnection, closeConnection } from './connection.js';

const server = new McpServer({
  name: 'mssql-server',
  version: '1.0.0',
});

// Register all tools
registerQueryTool(server);
registerTablesTool(server);
registerSchemaTool(server);
registerProceduresTool(server);
registerExecuteProcTool(server);

// Connection test tool
server.tool(
  'mssql_connect',
  'Test connection to MS SQL Server and get server information.',
  {},
  async () => {
    const result = await testConnection();

    if (result.success) {
      return {
        content: [{
          type: 'text',
          text: `✓ ${result.message}\nServer: ${result.serverVersion}`,
        }],
      };
    } else {
      return {
        content: [{ type: 'text', text: `✗ ${result.message}` }],
        isError: true,
      };
    }
  }
);

// Graceful shutdown
process.on('SIGINT', async () => {
  await closeConnection();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await closeConnection();
  process.exit(0);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MSSQL MCP Server started');
}

main().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
