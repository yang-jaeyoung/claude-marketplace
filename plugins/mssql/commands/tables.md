---
description: List all tables in the database
argument-hint: "[schema_name]"
allowed-tools: ["mcp__mssql__mssql_tables"]
---

# MS SQL Tables

List all tables and views in the current database.

## Instructions

1. Call the `mssql_tables` MCP tool
2. If schema name is provided in arguments, pass it as the `schemaName` parameter
3. Display tables grouped by schema with row counts

## Usage Examples

```
/mssql:tables
/mssql:tables dbo
/mssql:tables Sales
```

## Output Format

Tables are displayed grouped by schema:

```
Schema: dbo
--------------------------------------------------
  [TABLE] Customers (15,432 rows)
  [TABLE] Orders (89,201 rows)
  [VIEW]  vw_ActiveCustomers

Schema: Sales
--------------------------------------------------
  [TABLE] Products (1,234 rows)
  [TABLE] OrderDetails (245,678 rows)
```

## Tips

- Use schema name filter to focus on specific schemas
- Views are included by default
- Row counts are approximate based on system statistics
