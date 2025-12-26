---
description: View table schema and column information
argument-hint: "[table_name]"
allowed-tools: ["mcp__mssql__mssql_schema", "mcp__mssql__mssql_tables"]
---

# MS SQL Schema

View detailed schema information for database tables.

## Instructions

1. If table name is provided in arguments, call `mssql_schema` with that table name
2. If no table name is provided, first call `mssql_tables` to list available tables, then ask user which table to inspect
3. Display the schema information including:
   - Column names, data types, and constraints
   - Primary key information
   - Foreign key relationships
   - Index information

## Table Name Format

Table names can be specified as:
- Simple: `Customers`
- With schema: `dbo.Customers`
- With brackets: `[dbo].[Customers]`

## Usage Examples

```
/mssql:schema
/mssql:schema Customers
/mssql:schema dbo.Orders
/mssql:schema [Sales].[OrderDetails]
```

## Output Information

The schema information includes:
- **Columns**: Name, data type, nullable, default value, identity, computed
- **Primary Key**: Key name and columns
- **Foreign Keys**: Key name, local columns, referenced table and columns
- **Indexes**: Index name, columns, unique flag, type
