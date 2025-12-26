---
description: SQL Server query best practices and optimization guidelines. Use when writing, reviewing, or optimizing SQL queries for MS SQL Server.
---

# SQL Server Best Practices

This skill provides guidance on writing efficient and secure SQL queries for MS SQL Server.

## Query Optimization

### SELECT Statements
- Always specify column names instead of using `SELECT *`
- Use `TOP` clause to limit result sets: `SELECT TOP 100 * FROM Orders`
- Prefer `EXISTS` over `IN` for subqueries when checking existence
- Use `NOLOCK` hint only for reporting queries where dirty reads are acceptable

### JOIN Best Practices
- Always use explicit JOIN syntax: `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`
- Join on indexed columns when possible
- Consider join order for optimal performance (smaller tables first in INNER JOINs)
- Avoid CROSS JOINs unless specifically needed

### WHERE Clause Optimization
- Avoid functions on indexed columns:
  - Bad: `WHERE YEAR(OrderDate) = 2024`
  - Good: `WHERE OrderDate >= '2024-01-01' AND OrderDate < '2025-01-01'`
- Use parameterized queries to prevent SQL injection
- Use `BETWEEN` for range queries: `WHERE Price BETWEEN 10 AND 100`
- Place most restrictive conditions first

## Security Guidelines

### Dangerous Operations Checklist

Before executing any of these operations:

| Operation | Risk | Action Required |
|-----------|------|-----------------|
| DROP TABLE/DATABASE | Permanent deletion | Verify backup exists, confirm object name |
| TRUNCATE TABLE | All data deleted | Confirm no foreign key dependencies |
| DELETE without WHERE | All rows deleted | Always add WHERE clause or use TRUNCATE |
| UPDATE without WHERE | All rows modified | Always add WHERE clause |

### Security Best Practices
- Use transactions for multi-statement operations
- Always include error handling with TRY...CATCH
- Avoid dynamic SQL; use `sp_executesql` if necessary
- Never store sensitive data in plain text
- Use Windows Authentication when possible

## Performance Tips

### Indexing Guidelines
- Create indexes on frequently queried columns
- Consider covering indexes for common SELECT queries
- Avoid over-indexing write-heavy tables
- Use `INCLUDE` for non-key columns: `CREATE INDEX IX_Name ON Table(Col1) INCLUDE (Col2, Col3)`

### Common Query Patterns

```sql
-- Efficient pagination (SQL Server 2012+)
SELECT * FROM Orders
ORDER BY OrderDate DESC
OFFSET 0 ROWS FETCH NEXT 20 ROWS ONLY;

-- Batch delete (avoid lock escalation)
WHILE 1 = 1
BEGIN
    DELETE TOP (1000) FROM Logs
    WHERE CreatedAt < DATEADD(day, -30, GETDATE());
    IF @@ROWCOUNT = 0 BREAK;
END;

-- Upsert pattern (MERGE)
MERGE INTO TargetTable AS target
USING SourceTable AS source ON target.Id = source.Id
WHEN MATCHED THEN UPDATE SET target.Value = source.Value
WHEN NOT MATCHED THEN INSERT (Id, Value) VALUES (source.Id, source.Value);

-- Parameterized query
EXEC sp_executesql
    N'SELECT * FROM Users WHERE Id = @Id',
    N'@Id INT',
    @Id = 123;
```

### Transaction Guidelines

```sql
BEGIN TRY
    BEGIN TRANSACTION;

    -- Your operations here
    UPDATE Accounts SET Balance = Balance - 100 WHERE Id = 1;
    UPDATE Accounts SET Balance = Balance + 100 WHERE Id = 2;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;

    -- Log or rethrow error
    THROW;
END CATCH;
```

## Common Mistakes to Avoid

1. **SELECT \*** in production queries - always specify columns
2. **Missing indexes** on frequently filtered columns
3. **Cursor overuse** - use set-based operations instead
4. **Ignoring execution plans** - check with `SET STATISTICS IO ON`
5. **Not using appropriate data types** - use `INT` instead of `BIGINT` when possible
6. **Missing NULL handling** - use `ISNULL()` or `COALESCE()`
