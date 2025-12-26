import { SqlErrorCode, type SqlError } from '../types.js';

export function handleSqlError(error: unknown): SqlError {
  if (error instanceof Error) {
    const err = error as Error & { code?: string; number?: number; state?: number };

    // Connection errors
    if (err.code === 'ESOCKET' || err.code === 'ECONNREFUSED') {
      return {
        code: SqlErrorCode.CONNECTION_FAILED,
        message: 'Cannot connect to SQL Server',
        details: err.message,
        suggestion: 'Check if SQL Server is running and the server name is correct',
      };
    }

    if (err.code === 'ETIMEOUT') {
      return {
        code: SqlErrorCode.QUERY_TIMEOUT,
        message: 'Query execution timed out',
        details: err.message,
        suggestion: 'Optimize the query or increase timeout value',
      };
    }

    // SQL Server specific errors
    if (err.number) {
      // Permission denied
      if (err.number === 229 || err.number === 230) {
        return {
          code: SqlErrorCode.PERMISSION_DENIED,
          message: 'Permission denied',
          details: err.message,
          suggestion: 'Request appropriate permissions from database administrator',
        };
      }

      // Object not found
      if (err.number === 208) {
        return {
          code: SqlErrorCode.OBJECT_NOT_FOUND,
          message: 'Object not found',
          details: err.message,
          suggestion: 'Check the table/view name and schema',
        };
      }

      // Syntax error
      if (err.number === 102 || err.number === 156) {
        return {
          code: SqlErrorCode.SYNTAX_ERROR,
          message: 'SQL syntax error',
          details: err.message,
          suggestion: 'Review and correct the SQL syntax',
        };
      }
    }

    return {
      code: SqlErrorCode.UNKNOWN,
      message: err.message || 'Unknown error occurred',
      details: JSON.stringify({ name: err.name, code: err.code, number: err.number }),
    };
  }

  return {
    code: SqlErrorCode.UNKNOWN,
    message: 'Unknown error occurred',
    details: String(error),
  };
}

export function formatErrorResponse(error: SqlError): string {
  let response = `Error: ${error.message}`;
  if (error.details) {
    response += `\nDetails: ${error.details}`;
  }
  if (error.suggestion) {
    response += `\nSuggestion: ${error.suggestion}`;
  }
  return response;
}
