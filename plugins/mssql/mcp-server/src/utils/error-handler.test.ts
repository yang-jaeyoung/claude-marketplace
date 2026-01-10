import { describe, it, expect } from 'vitest';
import { handleSqlError, formatErrorResponse } from './error-handler.js';
import { SqlErrorCode } from '../types.js';

describe('error-handler', () => {
  describe('handleSqlError', () => {
    describe('connection errors', () => {
      it('should handle ESOCKET error', () => {
        const error = new Error('Connection failed');
        (error as Error & { code?: string }).code = 'ESOCKET';

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.CONNECTION_FAILED);
        expect(result.message).toContain('Cannot connect');
        expect(result.suggestion).toContain('running');
      });

      it('should handle ECONNREFUSED error', () => {
        const error = new Error('Connection refused');
        (error as Error & { code?: string }).code = 'ECONNREFUSED';

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.CONNECTION_FAILED);
        expect(result.suggestion).toBeDefined();
      });
    });

    describe('timeout errors', () => {
      it('should handle ETIMEOUT error', () => {
        const error = new Error('Query timed out');
        (error as Error & { code?: string }).code = 'ETIMEOUT';

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.QUERY_TIMEOUT);
        expect(result.message).toContain('timed out');
        expect(result.suggestion).toContain('Optimize');
      });
    });

    describe('SQL Server specific errors', () => {
      it('should handle permission denied (error 229)', () => {
        const error = new Error('The SELECT permission was denied');
        (error as Error & { number?: number }).number = 229;

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.PERMISSION_DENIED);
        expect(result.message).toContain('Permission denied');
        expect(result.suggestion).toContain('permissions');
      });

      it('should handle permission denied (error 230)', () => {
        const error = new Error('The EXECUTE permission was denied');
        (error as Error & { number?: number }).number = 230;

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.PERMISSION_DENIED);
      });

      it('should handle object not found (error 208)', () => {
        const error = new Error("Invalid object name 'users'");
        (error as Error & { number?: number }).number = 208;

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.OBJECT_NOT_FOUND);
        expect(result.message).toContain('not found');
        expect(result.suggestion).toContain('table');
      });

      it('should handle syntax error (error 102)', () => {
        const error = new Error("Incorrect syntax near 'FROM'");
        (error as Error & { number?: number }).number = 102;

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.SYNTAX_ERROR);
        expect(result.message).toContain('syntax');
        expect(result.suggestion).toContain('correct');
      });

      it('should handle syntax error (error 156)', () => {
        const error = new Error("Incorrect syntax near keyword");
        (error as Error & { number?: number }).number = 156;

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.SYNTAX_ERROR);
      });
    });

    describe('unknown errors', () => {
      it('should handle generic Error object', () => {
        const error = new Error('Something went wrong');

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.UNKNOWN);
        expect(result.message).toBe('Something went wrong');
      });

      it('should handle Error with no message', () => {
        const error = new Error();

        const result = handleSqlError(error);

        expect(result.code).toBe(SqlErrorCode.UNKNOWN);
        expect(result.message).toContain('Unknown');
      });

      it('should handle string error', () => {
        const result = handleSqlError('String error message');

        expect(result.code).toBe(SqlErrorCode.UNKNOWN);
        expect(result.details).toBe('String error message');
      });

      it('should handle null error', () => {
        const result = handleSqlError(null);

        expect(result.code).toBe(SqlErrorCode.UNKNOWN);
        expect(result.message).toContain('Unknown');
      });

      it('should handle undefined error', () => {
        const result = handleSqlError(undefined);

        expect(result.code).toBe(SqlErrorCode.UNKNOWN);
      });

      it('should handle number error', () => {
        const result = handleSqlError(42);

        expect(result.code).toBe(SqlErrorCode.UNKNOWN);
        expect(result.details).toBe('42');
      });

      it('should handle object error', () => {
        const result = handleSqlError({ custom: 'error' });

        expect(result.code).toBe(SqlErrorCode.UNKNOWN);
      });
    });

    describe('error details', () => {
      it('should include error name in details for unknown errors', () => {
        const error = new Error('Test error');
        error.name = 'CustomError';

        const result = handleSqlError(error);

        expect(result.details).toContain('CustomError');
      });

      it('should include error code in details for unknown errors', () => {
        const error = new Error('Test error');
        (error as Error & { code?: string }).code = 'CUSTOM_CODE';

        const result = handleSqlError(error);

        expect(result.details).toContain('CUSTOM_CODE');
      });

      it('should include error number in details for unknown errors', () => {
        const error = new Error('Test error');
        (error as Error & { number?: number }).number = 999;

        const result = handleSqlError(error);

        expect(result.details).toContain('999');
      });
    });
  });

  describe('formatErrorResponse', () => {
    it('should format error with message only', () => {
      const error = {
        code: SqlErrorCode.UNKNOWN,
        message: 'Something went wrong',
      };

      const result = formatErrorResponse(error);

      expect(result).toBe('Error: Something went wrong');
    });

    it('should include details when present', () => {
      const error = {
        code: SqlErrorCode.SYNTAX_ERROR,
        message: 'SQL syntax error',
        details: "Incorrect syntax near 'SELECT'",
      };

      const result = formatErrorResponse(error);

      expect(result).toContain('Error: SQL syntax error');
      expect(result).toContain('Details:');
      expect(result).toContain("Incorrect syntax near 'SELECT'");
    });

    it('should include suggestion when present', () => {
      const error = {
        code: SqlErrorCode.CONNECTION_FAILED,
        message: 'Cannot connect to SQL Server',
        suggestion: 'Check if the server is running',
      };

      const result = formatErrorResponse(error);

      expect(result).toContain('Error: Cannot connect');
      expect(result).toContain('Suggestion:');
      expect(result).toContain('Check if the server is running');
    });

    it('should format complete error with all fields', () => {
      const error = {
        code: SqlErrorCode.PERMISSION_DENIED,
        message: 'Permission denied',
        details: 'SELECT permission denied on object Users',
        suggestion: 'Request SELECT permission from DBA',
      };

      const result = formatErrorResponse(error);

      expect(result).toContain('Error: Permission denied');
      expect(result).toContain('Details:');
      expect(result).toContain('Suggestion:');
      expect(result.split('\n').length).toBe(3);
    });

    it('should handle empty details and suggestion', () => {
      const error = {
        code: SqlErrorCode.UNKNOWN,
        message: 'Error occurred',
        details: '',
        suggestion: '',
      };

      const result = formatErrorResponse(error);

      // Empty strings are falsy, so they should not be included
      expect(result).toBe('Error: Error occurred');
    });
  });
});
