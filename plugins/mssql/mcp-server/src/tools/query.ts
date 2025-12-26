import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { executeQuery } from '../connection.js';
import { analyzeQuery, validateQuery, formatQueryResult } from '../utils/sql-parser.js';
import { handleSqlError, formatErrorResponse } from '../utils/error-handler.js';

const QueryInputSchema = z.object({
  query: z.string().describe('SQL query to execute'),
  maxRows: z.number().optional().default(1000).describe('Maximum number of rows to return (default: 1000)'),
});

export function registerQueryTool(server: McpServer): void {
  server.tool(
    'mssql_query',
    'Execute a SQL query against MS SQL Server. Supports SELECT, INSERT, UPDATE, DELETE, and DDL operations.',
    QueryInputSchema.shape,
    async ({ query, maxRows }) => {
      // Validate query
      const validation = validateQuery(query);
      if (!validation.valid) {
        return {
          content: [{ type: 'text', text: `Validation Error: ${validation.error}` }],
          isError: true,
        };
      }

      // Analyze query for dangerous operations
      const analysis = analyzeQuery(query);
      if (analysis.requiresConfirmation) {
        return {
          content: [{
            type: 'text',
            text: `⚠️ WARNING: ${analysis.dangerReason}\n\nQuery: ${query}\nAffected tables: ${analysis.tables.join(', ')}\n\nThis query requires explicit user confirmation before execution. Please confirm by calling this tool again with the same query after user approval.`,
          }],
        };
      }

      try {
        const result = await executeQuery(query, maxRows);
        const recordset = result.recordset || [];
        const rowsAffected = result.rowsAffected?.[0] ?? 0;

        if (recordset.length > 0) {
          // SELECT query with results
          const formattedResult = formatQueryResult(recordset as Record<string, unknown>[]);
          return {
            content: [{
              type: 'text',
              text: `Query executed successfully.\nRows returned: ${recordset.length}\n\n${formattedResult}`,
            }],
          };
        } else if (rowsAffected > 0) {
          // INSERT, UPDATE, DELETE
          return {
            content: [{
              type: 'text',
              text: `Query executed successfully.\nRows affected: ${rowsAffected}`,
            }],
          };
        } else {
          // DDL or other
          return {
            content: [{
              type: 'text',
              text: 'Query executed successfully.',
            }],
          };
        }
      } catch (error) {
        const sqlError = handleSqlError(error);
        return {
          content: [{ type: 'text', text: formatErrorResponse(sqlError) }],
          isError: true,
        };
      }
    }
  );
}
