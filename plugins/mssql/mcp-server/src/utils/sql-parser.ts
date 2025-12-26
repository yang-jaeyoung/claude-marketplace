import { QueryType, type QueryAnalysis } from '../types.js';

const BLOCKED_KEYWORDS = ['xp_cmdshell', 'sp_configure', 'OPENROWSET', 'OPENDATASOURCE', 'BULK INSERT'];
const MAX_QUERY_LENGTH = 50000;

export function analyzeQuery(sql: string): QueryAnalysis {
  const upperSql = sql.toUpperCase().trim();
  const tables = extractTableNames(sql);

  // Check for DDL operations
  const ddlPatterns: Array<{ pattern: RegExp; reason: string }> = [
    { pattern: /^DROP\s+(TABLE|DATABASE|INDEX|VIEW|PROCEDURE|FUNCTION|TRIGGER)/i, reason: 'DROP operation permanently deletes objects' },
    { pattern: /^TRUNCATE\s+TABLE/i, reason: 'TRUNCATE removes all data from table' },
    { pattern: /^ALTER\s+(TABLE|DATABASE)/i, reason: 'ALTER modifies schema structure' },
    { pattern: /^CREATE\s+(TABLE|DATABASE|INDEX|VIEW|PROCEDURE|FUNCTION|TRIGGER)/i, reason: 'CREATE adds new database objects' },
  ];

  for (const { pattern, reason } of ddlPatterns) {
    if (pattern.test(upperSql)) {
      return {
        type: QueryType.DDL,
        isDangerous: true,
        dangerReason: reason,
        requiresConfirmation: true,
        tables,
      };
    }
  }

  // Check for DELETE without WHERE
  if (/^DELETE\s+FROM\s+\w+/i.test(upperSql) && !/WHERE/i.test(upperSql)) {
    return {
      type: QueryType.DELETE,
      isDangerous: true,
      dangerReason: 'DELETE without WHERE clause will remove all rows',
      requiresConfirmation: true,
      tables,
    };
  }

  // Check for UPDATE without WHERE
  if (/^UPDATE\s+\w+\s+SET/i.test(upperSql) && !/WHERE/i.test(upperSql)) {
    return {
      type: QueryType.UPDATE,
      isDangerous: true,
      dangerReason: 'UPDATE without WHERE clause will modify all rows',
      requiresConfirmation: true,
      tables,
    };
  }

  // Determine query type
  const type = detectQueryType(upperSql);

  return {
    type,
    isDangerous: false,
    requiresConfirmation: false,
    tables,
  };
}

export function validateQuery(sql: string): { valid: boolean; error?: string } {
  // Check length
  if (sql.length > MAX_QUERY_LENGTH) {
    return { valid: false, error: `Query too long (max ${MAX_QUERY_LENGTH} characters)` };
  }

  // Check for blocked keywords
  const upperSql = sql.toUpperCase();
  for (const keyword of BLOCKED_KEYWORDS) {
    if (upperSql.includes(keyword.toUpperCase())) {
      return { valid: false, error: `'${keyword}' is blocked for security reasons` };
    }
  }

  // Check for empty query
  if (!sql.trim()) {
    return { valid: false, error: 'Query cannot be empty' };
  }

  return { valid: true };
}

function detectQueryType(upperSql: string): QueryType {
  if (upperSql.startsWith('SELECT')) return QueryType.SELECT;
  if (upperSql.startsWith('INSERT')) return QueryType.INSERT;
  if (upperSql.startsWith('UPDATE')) return QueryType.UPDATE;
  if (upperSql.startsWith('DELETE')) return QueryType.DELETE;
  if (upperSql.startsWith('EXEC')) return QueryType.EXEC;
  if (/^(CREATE|ALTER|DROP|TRUNCATE)/.test(upperSql)) return QueryType.DDL;
  return QueryType.OTHER;
}

function extractTableNames(sql: string): string[] {
  const tables: string[] = [];

  // Match table names after FROM, JOIN, INTO, UPDATE, TABLE
  const patterns = [
    /FROM\s+(\[?[\w.]+\]?)/gi,
    /JOIN\s+(\[?[\w.]+\]?)/gi,
    /INTO\s+(\[?[\w.]+\]?)/gi,
    /UPDATE\s+(\[?[\w.]+\]?)/gi,
    /TABLE\s+(\[?[\w.]+\]?)/gi,
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(sql)) !== null) {
      const tableName = match[1].replace(/\[|\]/g, '');
      if (!tables.includes(tableName)) {
        tables.push(tableName);
      }
    }
  }

  return tables;
}

export function formatQueryResult(
  rows: Record<string, unknown>[],
  columns?: string[]
): string {
  if (!rows || rows.length === 0) {
    return 'No results returned';
  }

  const cols = columns || Object.keys(rows[0]);

  // Calculate column widths
  const widths = cols.map(col => {
    const values = rows.map(row => String(row[col] ?? 'NULL'));
    return Math.max(col.length, ...values.map(v => v.length));
  });

  // Build header
  const header = cols.map((col, i) => col.padEnd(widths[i])).join(' | ');
  const separator = widths.map(w => '-'.repeat(w)).join('-+-');

  // Build rows
  const rowStrings = rows.map(row =>
    cols.map((col, i) => String(row[col] ?? 'NULL').padEnd(widths[i])).join(' | ')
  );

  return [header, separator, ...rowStrings].join('\n');
}
