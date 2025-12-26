# MS SQL Server Plugin for Claude Code

Execute SQL queries, explore database schemas, and manage stored procedures directly from Claude Code.

## Features

- **Query Execution**: Run SQL queries with safety checks for dangerous operations
- **Schema Explorer**: View table structures, columns, keys, and indexes
- **Table Browser**: List all tables and views in the database
- **Stored Procedures**: List, inspect, and execute stored procedures
- **Windows Authentication**: Secure connection using Windows credentials

## Prerequisites

- Node.js 20.0.0 or higher
- MS SQL Server (local or remote)
- Windows Authentication enabled on SQL Server

## Installation

### 1. Install the plugin

```bash
# From the marketplace
claude plugins add github:jyyang/claude-marketplace
claude plugins install mssql
```

### 2. Build the MCP server

```bash
cd plugins/mssql/mcp-server
npm install
npm run build
```

### 3. Configure environment

Create or update your `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "mssql": {
      "command": "node",
      "args": ["./plugins/mssql/mcp-server/dist/index.js"],
      "env": {
        "MSSQL_SERVER": "localhost",
        "MSSQL_DATABASE": "YourDatabase"
      }
    }
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MSSQL_SERVER` | SQL Server hostname or IP | localhost |
| `MSSQL_DATABASE` | Default database name | master |
| `MSSQL_TRUST_CERT` | Trust self-signed certificates | true |
| `MSSQL_QUERY_TIMEOUT` | Query timeout in milliseconds | 60000 |
| `MSSQL_CONNECTION_TIMEOUT` | Connection timeout in milliseconds | 30000 |

## Commands

### `/mssql:query <sql>`
Execute a SQL query against the database.

```
/mssql:query SELECT TOP 10 * FROM Customers
/mssql:query INSERT INTO Logs (Message) VALUES ('Test')
```

### `/mssql:tables [schema]`
List all tables and views in the database.

```
/mssql:tables
/mssql:tables dbo
```

### `/mssql:schema <table>`
View detailed schema information for a table.

```
/mssql:schema Customers
/mssql:schema dbo.Orders
```

### `/mssql:procedures [name]`
List stored procedures or get details for a specific procedure.

```
/mssql:procedures
/mssql:procedures sp_GetCustomerOrders
```

### `/mssql:execute <procedure> [params]`
Execute a stored procedure with parameters.

```
/mssql:execute sp_GetOrders @CustomerId=123
/mssql:execute sp_Report {"Year": 2024}
```

## MCP Tools

The plugin exposes these MCP tools for direct use:

| Tool | Description |
|------|-------------|
| `mssql_connect` | Test database connection |
| `mssql_query` | Execute SQL queries |
| `mssql_tables` | List tables and views |
| `mssql_schema` | Get table schema details |
| `mssql_procedures` | List stored procedures |
| `mssql_execute_proc` | Execute stored procedures |

## Security

### Blocked Keywords
The following SQL keywords are blocked for security:
- `xp_cmdshell`
- `sp_configure`
- `OPENROWSET`
- `OPENDATASOURCE`
- `BULK INSERT`

### Dangerous Operation Warnings
The plugin warns and requires confirmation for:
- `DROP TABLE/DATABASE`
- `TRUNCATE TABLE`
- `DELETE` without `WHERE` clause
- `UPDATE` without `WHERE` clause

## Troubleshooting

### Connection Issues

1. **Verify SQL Server is running**
   ```cmd
   sc query MSSQLSERVER
   ```

2. **Check Windows Authentication**
   - Ensure SQL Server is configured for Windows Authentication
   - The current Windows user must have access to the database

3. **Trust Certificate**
   - For local development with self-signed certs, set `MSSQL_TRUST_CERT=true`

### Common Errors

| Error | Solution |
|-------|----------|
| Connection refused | Check SQL Server is running and listening |
| Login failed | Verify Windows user has database access |
| Object not found | Check table/procedure name and schema |
| Permission denied | Request appropriate permissions from DBA |

## License

MIT
