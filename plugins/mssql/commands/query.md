---
description: Execute SQL query against MS SQL Server
argument-hint: "<sql_query>"
allowed-tools: ["mcp__mssql__mssql_query", "mcp__mssql__mssql_connect"]
---

# MS SQL Query

Execute SQL queries against the connected MS SQL Server database.

## Instructions

1. Parse the user's SQL query from arguments
2. If no query is provided, ask the user what query they want to execute
3. For DDL operations (CREATE, ALTER, DROP, TRUNCATE), the MCP tool will return a warning - display it and ask for confirmation before re-executing
4. Execute the query using the `mssql_query` MCP tool
5. Format and display the results

## Safety Notes

The MCP tool will detect and warn about dangerous operations:
- DROP TABLE/DATABASE - Requires explicit confirmation
- TRUNCATE TABLE - Requires explicit confirmation
- DELETE without WHERE - Warns about full table deletion
- UPDATE without WHERE - Warns about full table update

## Usage Examples

```
/mssql:query SELECT TOP 10 * FROM Customers
/mssql:query SELECT COUNT(*) FROM Orders WHERE OrderDate > '2024-01-01'
/mssql:query INSERT INTO Logs (Message, CreatedAt) VALUES ('Test', GETDATE())
```

## Tips

- Use TOP clause to limit large result sets
- For complex queries, consider using stored procedures
- Always include WHERE clause for UPDATE/DELETE operations
