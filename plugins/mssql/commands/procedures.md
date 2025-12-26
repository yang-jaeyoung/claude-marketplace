---
description: List stored procedures with their parameters
argument-hint: "[schema_name or procedure_name]"
allowed-tools: ["mcp__mssql__mssql_procedures"]
---

# MS SQL Procedures

List stored procedures and their parameter definitions.

## Instructions

1. Parse the argument to determine if it's a schema name or procedure name
2. If argument looks like a procedure name (contains "sp_", "usp_", or is a full path like "dbo.MyProc"):
   - Call `mssql_procedures` with `procedureName` parameter for detailed view
3. If argument is a schema name or empty:
   - Call `mssql_procedures` with optional `schemaName` parameter to list procedures

## Usage Examples

```
/mssql:procedures
/mssql:procedures dbo
/mssql:procedures sp_GetCustomerOrders
/mssql:procedures dbo.usp_UpdateInventory
```

## Output Format

### List View
```
Schema: dbo
--------------------------------------------------
  sp_GetOrders(@CustomerId int, @StartDate date)
  sp_UpdateStatus(@Id int, @Status varchar OUTPUT)
```

### Detail View (when specific procedure is specified)
```
Stored Procedure: dbo.sp_GetOrders
==================================================

Created: 2024-01-15
Modified: 2024-06-20

PARAMETERS:
------------------------------
  @CustomerId: int [INPUT]
  @StartDate: date [INPUT]
  @EndDate: date [INPUT] = NULL

DEFINITION (preview):
------------------------------
CREATE PROCEDURE [dbo].[sp_GetOrders]
  @CustomerId INT,
  @StartDate DATE,
  @EndDate DATE = NULL
AS
BEGIN
  ...
```

## Tips

- Use detail view to see parameter types and default values
- OUTPUT parameters are clearly marked
- Definition preview shows first 1000 characters
