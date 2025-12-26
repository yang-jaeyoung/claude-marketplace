import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { executeQuery } from '../connection.js';
import { handleSqlError, formatErrorResponse } from '../utils/error-handler.js';

const SchemaInputSchema = z.object({
  tableName: z.string().describe('Table name to get schema for (e.g., "Customers" or "dbo.Customers")'),
});

export function registerSchemaTool(server: McpServer): void {
  server.tool(
    'mssql_schema',
    'Get detailed schema information for a table including columns, primary keys, foreign keys, and indexes.',
    SchemaInputSchema.shape,
    async ({ tableName }) => {
      // Parse schema.table format
      let schemaName = 'dbo';
      let table = tableName;

      if (tableName.includes('.')) {
        const parts = tableName.split('.');
        schemaName = parts[0].replace(/\[|\]/g, '');
        table = parts[1].replace(/\[|\]/g, '');
      }

      try {
        // Get columns
        const columnsQuery = `
          SELECT
            c.name AS column_name,
            t.name AS data_type,
            c.max_length,
            c.precision,
            c.scale,
            c.is_nullable,
            c.is_identity,
            c.is_computed,
            OBJECT_DEFINITION(c.default_object_id) AS default_value
          FROM sys.columns c
          INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
          INNER JOIN sys.objects o ON c.object_id = o.object_id
          INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
          WHERE o.name = '${table.replace(/'/g, "''")}'
            AND s.name = '${schemaName.replace(/'/g, "''")}'
          ORDER BY c.column_id
        `;

        const columnsResult = await executeQuery(columnsQuery);

        if (!columnsResult.recordset || columnsResult.recordset.length === 0) {
          return {
            content: [{
              type: 'text',
              text: `Table '${schemaName}.${table}' not found.`,
            }],
            isError: true,
          };
        }

        // Get primary key
        const pkQuery = `
          SELECT
            i.name AS pk_name,
            STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS columns
          FROM sys.indexes i
          INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
          INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
          INNER JOIN sys.objects o ON i.object_id = o.object_id
          INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
          WHERE i.is_primary_key = 1
            AND o.name = '${table.replace(/'/g, "''")}'
            AND s.name = '${schemaName.replace(/'/g, "''")}'
          GROUP BY i.name
        `;

        const pkResult = await executeQuery(pkQuery);

        // Get foreign keys
        const fkQuery = `
          SELECT
            fk.name AS fk_name,
            STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY fkc.constraint_column_id) AS columns,
            OBJECT_SCHEMA_NAME(fk.referenced_object_id) + '.' + OBJECT_NAME(fk.referenced_object_id) AS referenced_table,
            STRING_AGG(rc.name, ', ') WITHIN GROUP (ORDER BY fkc.constraint_column_id) AS referenced_columns
          FROM sys.foreign_keys fk
          INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
          INNER JOIN sys.columns c ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
          INNER JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
          INNER JOIN sys.objects o ON fk.parent_object_id = o.object_id
          INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
          WHERE o.name = '${table.replace(/'/g, "''")}'
            AND s.name = '${schemaName.replace(/'/g, "''")}'
          GROUP BY fk.name, fk.referenced_object_id
        `;

        const fkResult = await executeQuery(fkQuery);

        // Get indexes
        const indexQuery = `
          SELECT
            i.name AS index_name,
            STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS columns,
            i.is_unique,
            i.is_primary_key,
            i.type_desc
          FROM sys.indexes i
          INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
          INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
          INNER JOIN sys.objects o ON i.object_id = o.object_id
          INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
          WHERE o.name = '${table.replace(/'/g, "''")}'
            AND s.name = '${schemaName.replace(/'/g, "''")}'
            AND i.name IS NOT NULL
          GROUP BY i.name, i.is_unique, i.is_primary_key, i.type_desc
          ORDER BY i.is_primary_key DESC, i.name
        `;

        const indexResult = await executeQuery(indexQuery);

        // Format output
        let output = `Schema for ${schemaName}.${table}\n`;
        output += '='.repeat(50) + '\n\n';

        // Columns
        output += 'COLUMNS:\n';
        output += '-'.repeat(30) + '\n';

        interface ColumnRow {
          column_name: string;
          data_type: string;
          max_length: number;
          precision: number;
          scale: number;
          is_nullable: boolean;
          is_identity: boolean;
          is_computed: boolean;
          default_value: string | null;
        }

        for (const col of columnsResult.recordset as ColumnRow[]) {
          let typeInfo = col.data_type;
          if (['varchar', 'nvarchar', 'char', 'nchar'].includes(col.data_type)) {
            typeInfo += `(${col.max_length === -1 ? 'MAX' : col.max_length})`;
          } else if (['decimal', 'numeric'].includes(col.data_type)) {
            typeInfo += `(${col.precision},${col.scale})`;
          }

          const flags = [];
          if (!col.is_nullable) flags.push('NOT NULL');
          if (col.is_identity) flags.push('IDENTITY');
          if (col.is_computed) flags.push('COMPUTED');
          if (col.default_value) flags.push(`DEFAULT ${col.default_value}`);

          output += `  ${col.column_name}: ${typeInfo}`;
          if (flags.length > 0) output += ` [${flags.join(', ')}]`;
          output += '\n';
        }

        // Primary Key
        if (pkResult.recordset && pkResult.recordset.length > 0) {
          output += '\nPRIMARY KEY:\n';
          output += '-'.repeat(30) + '\n';
          const pk = pkResult.recordset[0] as { pk_name: string; columns: string };
          output += `  ${pk.pk_name}: (${pk.columns})\n`;
        }

        // Foreign Keys
        if (fkResult.recordset && fkResult.recordset.length > 0) {
          output += '\nFOREIGN KEYS:\n';
          output += '-'.repeat(30) + '\n';
          for (const fk of fkResult.recordset as Array<{
            fk_name: string;
            columns: string;
            referenced_table: string;
            referenced_columns: string;
          }>) {
            output += `  ${fk.fk_name}: (${fk.columns}) -> ${fk.referenced_table}(${fk.referenced_columns})\n`;
          }
        }

        // Indexes
        if (indexResult.recordset && indexResult.recordset.length > 0) {
          output += '\nINDEXES:\n';
          output += '-'.repeat(30) + '\n';
          for (const idx of indexResult.recordset as Array<{
            index_name: string;
            columns: string;
            is_unique: boolean;
            is_primary_key: boolean;
            type_desc: string;
          }>) {
            const flags = [];
            if (idx.is_primary_key) flags.push('PK');
            if (idx.is_unique && !idx.is_primary_key) flags.push('UNIQUE');
            flags.push(idx.type_desc);
            output += `  ${idx.index_name}: (${idx.columns}) [${flags.join(', ')}]\n`;
          }
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
