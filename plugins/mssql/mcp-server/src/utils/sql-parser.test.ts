import { describe, it, expect } from 'vitest';
import { analyzeQuery, validateQuery, formatQueryResult } from './sql-parser.js';
import { QueryType } from '../types.js';

describe('sql-parser', () => {
  describe('analyzeQuery', () => {
    describe('SELECT queries', () => {
      it('should identify simple SELECT as safe', () => {
        const result = analyzeQuery('SELECT * FROM users');
        expect(result.type).toBe(QueryType.SELECT);
        expect(result.isDangerous).toBe(false);
        expect(result.requiresConfirmation).toBe(false);
      });

      it('should extract table names from SELECT', () => {
        const result = analyzeQuery('SELECT id, name FROM users WHERE active = 1');
        expect(result.tables).toContain('users');
      });

      it('should extract multiple tables from JOINs', () => {
        const result = analyzeQuery(`
          SELECT u.id, o.total
          FROM users u
          JOIN orders o ON u.id = o.user_id
          LEFT JOIN products p ON o.product_id = p.id
        `);
        expect(result.tables).toContain('users');
        expect(result.tables).toContain('orders');
        expect(result.tables).toContain('products');
      });

      it('should handle bracket-quoted table names', () => {
        const result = analyzeQuery('SELECT * FROM [dbo].[users]');
        // Parser extracts table references, brackets are removed
        expect(result.tables.length).toBeGreaterThan(0);
        // Should contain at least one table reference with dbo or users
        const hasTableRef = result.tables.some(t => t.includes('dbo') || t.includes('users'));
        expect(hasTableRef).toBe(true);
      });
    });

    describe('INSERT queries', () => {
      it('should identify INSERT as INSERT type', () => {
        const result = analyzeQuery("INSERT INTO users (name) VALUES ('John')");
        expect(result.type).toBe(QueryType.INSERT);
        expect(result.isDangerous).toBe(false);
      });

      it('should extract table from INSERT INTO', () => {
        const result = analyzeQuery("INSERT INTO customers (name) VALUES ('Jane')");
        expect(result.tables).toContain('customers');
      });
    });

    describe('UPDATE queries', () => {
      it('should identify UPDATE with WHERE as safe', () => {
        const result = analyzeQuery("UPDATE users SET name = 'John' WHERE id = 1");
        expect(result.type).toBe(QueryType.UPDATE);
        expect(result.isDangerous).toBe(false);
      });

      it('should flag UPDATE without WHERE as dangerous', () => {
        const result = analyzeQuery("UPDATE users SET active = 0");
        expect(result.type).toBe(QueryType.UPDATE);
        expect(result.isDangerous).toBe(true);
        expect(result.dangerReason).toContain('without WHERE');
        expect(result.requiresConfirmation).toBe(true);
      });

      it('should extract table from UPDATE', () => {
        const result = analyzeQuery("UPDATE products SET price = 100 WHERE id = 5");
        expect(result.tables).toContain('products');
      });
    });

    describe('DELETE queries', () => {
      it('should identify DELETE with WHERE as safe', () => {
        const result = analyzeQuery('DELETE FROM users WHERE id = 1');
        expect(result.type).toBe(QueryType.DELETE);
        expect(result.isDangerous).toBe(false);
      });

      it('should flag DELETE without WHERE as dangerous', () => {
        const result = analyzeQuery('DELETE FROM users');
        expect(result.type).toBe(QueryType.DELETE);
        expect(result.isDangerous).toBe(true);
        expect(result.dangerReason).toContain('without WHERE');
        expect(result.requiresConfirmation).toBe(true);
      });
    });

    describe('DDL queries', () => {
      it('should flag DROP TABLE as dangerous DDL', () => {
        const result = analyzeQuery('DROP TABLE users');
        expect(result.type).toBe(QueryType.DDL);
        expect(result.isDangerous).toBe(true);
        expect(result.dangerReason).toContain('DROP');
        expect(result.requiresConfirmation).toBe(true);
      });

      it('should flag DROP DATABASE as dangerous DDL', () => {
        const result = analyzeQuery('DROP DATABASE mydb');
        expect(result.type).toBe(QueryType.DDL);
        expect(result.isDangerous).toBe(true);
      });

      it('should flag TRUNCATE TABLE as dangerous DDL', () => {
        const result = analyzeQuery('TRUNCATE TABLE logs');
        expect(result.type).toBe(QueryType.DDL);
        expect(result.isDangerous).toBe(true);
        expect(result.dangerReason).toContain('TRUNCATE');
      });

      it('should flag ALTER TABLE as dangerous DDL', () => {
        const result = analyzeQuery('ALTER TABLE users ADD COLUMN email VARCHAR(255)');
        expect(result.type).toBe(QueryType.DDL);
        expect(result.isDangerous).toBe(true);
      });

      it('should flag CREATE TABLE as DDL requiring confirmation', () => {
        const result = analyzeQuery('CREATE TABLE temp (id INT)');
        expect(result.type).toBe(QueryType.DDL);
        expect(result.requiresConfirmation).toBe(true);
      });
    });

    describe('EXEC queries', () => {
      it('should identify stored procedure execution', () => {
        const result = analyzeQuery('EXEC sp_GetUsers @id = 1');
        expect(result.type).toBe(QueryType.EXEC);
      });
    });

    describe('case sensitivity', () => {
      it('should handle lowercase queries', () => {
        const result = analyzeQuery('select * from users where id = 1');
        expect(result.type).toBe(QueryType.SELECT);
      });

      it('should handle mixed case queries', () => {
        const result = analyzeQuery('Select * From Users Where Id = 1');
        expect(result.type).toBe(QueryType.SELECT);
      });
    });
  });

  describe('validateQuery', () => {
    it('should accept valid SELECT query', () => {
      const result = validateQuery('SELECT * FROM users');
      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should reject empty query', () => {
      const result = validateQuery('');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('empty');
    });

    it('should reject whitespace-only query', () => {
      const result = validateQuery('   \n\t  ');
      expect(result.valid).toBe(false);
      expect(result.error).toContain('empty');
    });

    it('should reject query with xp_cmdshell', () => {
      const result = validateQuery("EXEC xp_cmdshell 'dir'");
      expect(result.valid).toBe(false);
      expect(result.error).toContain('xp_cmdshell');
      expect(result.error).toContain('blocked');
    });

    it('should reject query with sp_configure', () => {
      const result = validateQuery("EXEC sp_configure 'show advanced options', 1");
      expect(result.valid).toBe(false);
      expect(result.error).toContain('sp_configure');
    });

    it('should reject query with OPENROWSET', () => {
      const result = validateQuery("SELECT * FROM OPENROWSET('SQLOLEDB', 'server')");
      expect(result.valid).toBe(false);
      expect(result.error).toContain('OPENROWSET');
    });

    it('should reject query with OPENDATASOURCE', () => {
      const result = validateQuery("SELECT * FROM OPENDATASOURCE('SQLOLEDB', 'server')");
      expect(result.valid).toBe(false);
      expect(result.error).toContain('OPENDATASOURCE');
    });

    it('should reject query with BULK INSERT', () => {
      const result = validateQuery("BULK INSERT users FROM 'file.csv'");
      expect(result.valid).toBe(false);
      expect(result.error).toContain('BULK INSERT');
    });

    it('should reject overly long queries', () => {
      const longQuery = 'SELECT ' + 'a'.repeat(50001);
      const result = validateQuery(longQuery);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('too long');
    });

    it('should accept query at max length', () => {
      const query = 'SELECT ' + 'a'.repeat(49990);
      const result = validateQuery(query);
      expect(result.valid).toBe(true);
    });
  });

  describe('formatQueryResult', () => {
    it('should return "No results" for empty rows', () => {
      const result = formatQueryResult([]);
      expect(result).toBe('No results returned');
    });

    it('should return "No results" for undefined rows', () => {
      const result = formatQueryResult(undefined as unknown as Record<string, unknown>[]);
      expect(result).toBe('No results returned');
    });

    it('should format single row correctly', () => {
      const rows = [{ id: 1, name: 'John' }];
      const result = formatQueryResult(rows);

      expect(result).toContain('id');
      expect(result).toContain('name');
      expect(result).toContain('1');
      expect(result).toContain('John');
    });

    it('should format multiple rows correctly', () => {
      const rows = [
        { id: 1, name: 'John' },
        { id: 2, name: 'Jane' },
      ];
      const result = formatQueryResult(rows);

      expect(result).toContain('John');
      expect(result).toContain('Jane');
      expect(result.split('\n').length).toBeGreaterThanOrEqual(4); // header + separator + 2 rows
    });

    it('should handle NULL values', () => {
      const rows = [{ id: 1, name: null }];
      const result = formatQueryResult(rows);

      expect(result).toContain('NULL');
    });

    it('should handle undefined values', () => {
      const rows = [{ id: 1, name: undefined }];
      const result = formatQueryResult(rows);

      expect(result).toContain('NULL');
    });

    it('should use provided column order', () => {
      const rows = [{ id: 1, name: 'John', email: 'john@example.com' }];
      const result = formatQueryResult(rows, ['name', 'email']);

      const lines = result.split('\n');
      const header = lines[0];
      // name should come before email in the output
      expect(header.indexOf('name')).toBeLessThan(header.indexOf('email'));
      // id should not be in the output when columns are specified
      expect(header).not.toContain('id');
    });

    it('should pad columns for alignment', () => {
      const rows = [
        { id: 1, name: 'A' },
        { id: 100, name: 'Bob' },
      ];
      const result = formatQueryResult(rows);
      const lines = result.split('\n');

      // All data rows should have same length due to padding
      const dataLines = lines.slice(2);
      const lengths = dataLines.map(l => l.length);
      expect(lengths[0]).toBe(lengths[1]);
    });
  });
});
