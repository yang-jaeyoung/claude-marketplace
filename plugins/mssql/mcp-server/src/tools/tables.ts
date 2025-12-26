import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { executeQuery } from '../connection.js';
import { handleSqlError, formatErrorResponse } from '../utils/error-handler.js';
import type { TableInfo } from '../types.js';

const TablesInputSchema = z.object({
  schemaName: z.string().optional().describe('Filter by schema name (e.g., "dbo")'),
  includeViews: z.boolean().optional().default(true).describe('Include views in the result (default: true)'),
});

export function registerTablesTool(server: McpServer): void {
  server.tool(
    'mssql_tables',
    'List all tables and views in the current database. Optionally filter by schema.',
    TablesInputSchema.shape,
    async ({ schemaName, includeViews }) => {
      const typeFilter = includeViews ? "('U', 'V')" : "('U')";
      const schemaFilter = schemaName ? `AND s.name = '${schemaName.replace(/'/g, "''")}'` : '';

      const query = `
        SELECT
          s.name AS schema_name,
          t.name AS table_name,
          CASE t.type
            WHEN 'U' THEN 'TABLE'
            WHEN 'V' THEN 'VIEW'
          END AS table_type,
          ISNULL(p.rows, 0) AS row_count
        FROM sys.objects t
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0, 1)
        WHERE t.type IN ${typeFilter}
          ${schemaFilter}
        ORDER BY s.name, t.name
      `;

      try {
        const result = await executeQuery(query);
        const tables: TableInfo[] = (result.recordset as Array<{
          schema_name: string;
          table_name: string;
          table_type: 'TABLE' | 'VIEW';
          row_count: number;
        }>).map(row => ({
          schema: row.schema_name,
          name: row.table_name,
          type: row.table_type,
          rowCount: row.row_count,
        }));

        if (tables.length === 0) {
          return {
            content: [{
              type: 'text',
              text: schemaName
                ? `No tables found in schema '${schemaName}'.`
                : 'No tables found in the database.',
            }],
          };
        }

        // Group by schema
        const bySchema = tables.reduce((acc, table) => {
          if (!acc[table.schema]) acc[table.schema] = [];
          acc[table.schema].push(table);
          return acc;
        }, {} as Record<string, TableInfo[]>);

        let output = `Found ${tables.length} objects:\n\n`;

        for (const [schema, schemaTables] of Object.entries(bySchema)) {
          output += `Schema: ${schema}\n`;
          output += '-'.repeat(50) + '\n';

          for (const table of schemaTables) {
            const rowInfo = table.type === 'TABLE' ? ` (${table.rowCount?.toLocaleString()} rows)` : '';
            output += `  [${table.type}] ${table.name}${rowInfo}\n`;
          }
          output += '\n';
        }

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
