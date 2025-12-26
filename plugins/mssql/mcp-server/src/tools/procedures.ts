import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { executeQuery } from '../connection.js';
import { handleSqlError, formatErrorResponse } from '../utils/error-handler.js';

const ProceduresInputSchema = z.object({
  schemaName: z.string().optional().describe('Filter by schema name (e.g., "dbo")'),
  procedureName: z.string().optional().describe('Get details for a specific procedure'),
});

export function registerProceduresTool(server: McpServer): void {
  server.tool(
    'mssql_procedures',
    'List stored procedures with their parameters. Optionally filter by schema or get details for a specific procedure.',
    ProceduresInputSchema.shape,
    async ({ schemaName, procedureName }) => {
      try {
        if (procedureName) {
          // Get details for a specific procedure
          let procSchema = 'dbo';
          let procName = procedureName;

          if (procedureName.includes('.')) {
            const parts = procedureName.split('.');
            procSchema = parts[0].replace(/\[|\]/g, '');
            procName = parts[1].replace(/\[|\]/g, '');
          }

          const detailQuery = `
            SELECT
              p.name AS procedure_name,
              s.name AS schema_name,
              p.create_date,
              p.modify_date,
              m.definition
            FROM sys.procedures p
            INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
            INNER JOIN sys.sql_modules m ON p.object_id = m.object_id
            WHERE p.name = '${procName.replace(/'/g, "''")}'
              AND s.name = '${procSchema.replace(/'/g, "''")}'
          `;

          const detailResult = await executeQuery(detailQuery);

          if (!detailResult.recordset || detailResult.recordset.length === 0) {
            return {
              content: [{
                type: 'text',
                text: `Stored procedure '${procSchema}.${procName}' not found.`,
              }],
              isError: true,
            };
          }

          const proc = detailResult.recordset[0] as {
            procedure_name: string;
            schema_name: string;
            create_date: Date;
            modify_date: Date;
            definition: string;
          };

          // Get parameters
          const paramsQuery = `
            SELECT
              p.name AS param_name,
              t.name AS data_type,
              p.max_length,
              p.precision,
              p.scale,
              p.is_output,
              p.has_default_value,
              p.default_value
            FROM sys.parameters p
            INNER JOIN sys.types t ON p.user_type_id = t.user_type_id
            INNER JOIN sys.procedures pr ON p.object_id = pr.object_id
            INNER JOIN sys.schemas s ON pr.schema_id = s.schema_id
            WHERE pr.name = '${procName.replace(/'/g, "''")}'
              AND s.name = '${procSchema.replace(/'/g, "''")}'
            ORDER BY p.parameter_id
          `;

          const paramsResult = await executeQuery(paramsQuery);

          let output = `Stored Procedure: ${proc.schema_name}.${proc.procedure_name}\n`;
          output += '='.repeat(50) + '\n\n';
          output += `Created: ${proc.create_date}\n`;
          output += `Modified: ${proc.modify_date}\n\n`;

          output += 'PARAMETERS:\n';
          output += '-'.repeat(30) + '\n';

          if (paramsResult.recordset && paramsResult.recordset.length > 0) {
            for (const param of paramsResult.recordset as Array<{
              param_name: string;
              data_type: string;
              max_length: number;
              precision: number;
              scale: number;
              is_output: boolean;
              has_default_value: boolean;
              default_value: unknown;
            }>) {
              let typeInfo = param.data_type;
              if (['varchar', 'nvarchar', 'char', 'nchar'].includes(param.data_type)) {
                typeInfo += `(${param.max_length === -1 ? 'MAX' : param.max_length})`;
              } else if (['decimal', 'numeric'].includes(param.data_type)) {
                typeInfo += `(${param.precision},${param.scale})`;
              }

              const direction = param.is_output ? 'OUTPUT' : 'INPUT';
              const defaultInfo = param.has_default_value ? ` = ${param.default_value ?? 'NULL'}` : '';

              output += `  ${param.param_name}: ${typeInfo} [${direction}]${defaultInfo}\n`;
            }
          } else {
            output += '  (no parameters)\n';
          }

          // Show first 1000 chars of definition
          output += '\nDEFINITION (preview):\n';
          output += '-'.repeat(30) + '\n';
          const preview = proc.definition?.substring(0, 1000) || '(definition not available)';
          output += preview;
          if (proc.definition && proc.definition.length > 1000) {
            output += '\n... (truncated)';
          }

          return {
            content: [{ type: 'text', text: output }],
          };
        }

        // List all procedures
        const schemaFilter = schemaName ? `AND s.name = '${schemaName.replace(/'/g, "''")}'` : '';

        const listQuery = `
          SELECT
            s.name AS schema_name,
            p.name AS procedure_name,
            (
              SELECT STRING_AGG(
                par.name + ' ' + t.name +
                CASE par.is_output WHEN 1 THEN ' OUTPUT' ELSE '' END,
                ', '
              ) WITHIN GROUP (ORDER BY par.parameter_id)
              FROM sys.parameters par
              INNER JOIN sys.types t ON par.user_type_id = t.user_type_id
              WHERE par.object_id = p.object_id
            ) AS parameters,
            p.create_date,
            p.modify_date
          FROM sys.procedures p
          INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
          WHERE p.type = 'P'
            ${schemaFilter}
          ORDER BY s.name, p.name
        `;

        const result = await executeQuery(listQuery);

        if (!result.recordset || result.recordset.length === 0) {
          return {
            content: [{
              type: 'text',
              text: schemaName
                ? `No stored procedures found in schema '${schemaName}'.`
                : 'No stored procedures found in the database.',
            }],
          };
        }

        // Group by schema
        interface ProcRow {
          schema_name: string;
          procedure_name: string;
          parameters: string | null;
          create_date: Date;
          modify_date: Date;
        }

        const procedures = result.recordset as ProcRow[];
        const bySchema = procedures.reduce((acc, proc) => {
          if (!acc[proc.schema_name]) acc[proc.schema_name] = [];
          acc[proc.schema_name].push(proc);
          return acc;
        }, {} as Record<string, ProcRow[]>);

        let output = `Found ${procedures.length} stored procedures:\n\n`;

        for (const [schema, procs] of Object.entries(bySchema)) {
          output += `Schema: ${schema}\n`;
          output += '-'.repeat(50) + '\n';

          for (const proc of procs) {
            output += `  ${proc.procedure_name}`;
            if (proc.parameters) {
              output += `(${proc.parameters})`;
            } else {
              output += '()';
            }
            output += '\n';
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
