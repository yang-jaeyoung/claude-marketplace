import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { executeProcedure } from '../connection.js';
import { handleSqlError, formatErrorResponse } from '../utils/error-handler.js';
import { formatQueryResult } from '../utils/sql-parser.js';

const ExecuteProcInputSchema = z.object({
  procedureName: z.string().describe('Stored procedure name (e.g., "sp_GetCustomers" or "dbo.sp_GetCustomers")'),
  params: z.record(z.unknown()).optional().describe('Parameters as key-value pairs (e.g., {"CustomerId": 123, "StartDate": "2024-01-01"})'),
});

export function registerExecuteProcTool(server: McpServer): void {
  server.tool(
    'mssql_execute_proc',
    'Execute a stored procedure with optional parameters. Returns result sets and output parameters.',
    ExecuteProcInputSchema.shape,
    async ({ procedureName, params }) => {
      try {
        // Parse schema.procedure format
        let fullProcName = procedureName;
        if (!procedureName.includes('.')) {
          fullProcName = `dbo.${procedureName}`;
        }

        const startTime = Date.now();
        const result = await executeProcedure(fullProcName, params);
        const executionTime = Date.now() - startTime;

        let output = `Stored Procedure Executed: ${fullProcName}\n`;
        output += '='.repeat(50) + '\n\n';

        // Show parameters used
        if (params && Object.keys(params).length > 0) {
          output += 'Parameters:\n';
          for (const [key, value] of Object.entries(params)) {
            output += `  @${key} = ${JSON.stringify(value)}\n`;
          }
          output += '\n';
        }

        // Return value
        if (result.returnValue !== undefined) {
          output += `Return Value: ${result.returnValue}\n\n`;
        }

        // Result sets
        if (result.recordsets && result.recordsets.length > 0) {
          for (let i = 0; i < result.recordsets.length; i++) {
            const recordset = result.recordsets[i];
            output += `Result Set ${i + 1} (${recordset.length} rows):\n`;
            output += '-'.repeat(30) + '\n';

            if (recordset.length > 0) {
              output += formatQueryResult(recordset as Record<string, unknown>[]);
            } else {
              output += '(empty result set)';
            }
            output += '\n\n';
          }
        } else if (result.recordset && result.recordset.length > 0) {
          output += `Result (${result.recordset.length} rows):\n`;
          output += '-'.repeat(30) + '\n';
          output += formatQueryResult(result.recordset as Record<string, unknown>[]);
          output += '\n\n';
        }

        // Rows affected
        if (result.rowsAffected && result.rowsAffected.length > 0) {
          const totalAffected = result.rowsAffected.reduce((sum, n) => sum + n, 0);
          if (totalAffected > 0) {
            output += `Rows Affected: ${totalAffected}\n`;
          }
        }

        output += `Execution Time: ${executionTime}ms\n`;

        return {
          content: [{ type: 'text', text: output }],
        };
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
