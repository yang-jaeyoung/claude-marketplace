import sql from 'mssql';
import type { ConnectionConfig } from './types.js';

let pool: sql.ConnectionPool | null = null;

export function getConnectionConfig(): ConnectionConfig {
  return {
    server: process.env.MSSQL_SERVER || 'localhost',
    database: process.env.MSSQL_DATABASE || 'master',
    options: {
      trustedConnection: true,
      trustServerCertificate: process.env.MSSQL_TRUST_CERT !== 'false',
      encrypt: process.env.MSSQL_ENCRYPT === 'true',
    },
    connectionTimeout: parseInt(process.env.MSSQL_CONNECTION_TIMEOUT || '30000', 10),
    requestTimeout: parseInt(process.env.MSSQL_QUERY_TIMEOUT || '60000', 10),
  };
}

export async function getConnection(): Promise<sql.ConnectionPool> {
  if (pool && pool.connected) {
    return pool;
  }

  const config = getConnectionConfig();

  const sqlConfig: sql.config = {
    server: config.server,
    database: config.database,
    options: {
      trustedConnection: config.options.trustedConnection,
      trustServerCertificate: config.options.trustServerCertificate,
      encrypt: config.options.encrypt,
    },
    connectionTimeout: config.connectionTimeout,
    requestTimeout: config.requestTimeout,
  };

  pool = await sql.connect(sqlConfig);
  return pool;
}

export async function closeConnection(): Promise<void> {
  if (pool) {
    await pool.close();
    pool = null;
  }
}

export async function testConnection(): Promise<{ success: boolean; message: string; serverVersion?: string }> {
  try {
    const connection = await getConnection();
    const result = await connection.request().query('SELECT @@VERSION as version, DB_NAME() as database_name');
    const row = result.recordset[0];
    return {
      success: true,
      message: `Connected to ${row.database_name}`,
      serverVersion: row.version.split('\n')[0],
    };
  } catch (error) {
    const err = error as Error;
    return {
      success: false,
      message: `Connection failed: ${err.message}`,
    };
  }
}

export async function executeQuery(query: string, maxRows?: number): Promise<sql.IResult<unknown>> {
  const connection = await getConnection();
  const request = connection.request();

  if (maxRows && maxRows > 0) {
    const upperQuery = query.trim().toUpperCase();
    if (upperQuery.startsWith('SELECT') && !upperQuery.includes('TOP ')) {
      query = query.replace(/^SELECT\s+/i, `SELECT TOP ${maxRows} `);
    }
  }

  return await request.query(query);
}

export async function executeProcedure(
  procedureName: string,
  params?: Record<string, unknown>
): Promise<sql.IProcedureResult<unknown>> {
  const connection = await getConnection();
  const request = connection.request();

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      request.input(key, value);
    }
  }

  return await request.execute(procedureName);
}
