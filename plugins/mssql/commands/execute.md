---
description: Execute a stored procedure with parameters
argument-hint: "<procedure_name> [parameters]"
allowed-tools: ["mcp__mssql__mssql_execute_proc", "mcp__mssql__mssql_procedures"]
---

# MS SQL Execute Procedure

Execute a stored procedure with the specified parameters.

## Instructions

1. Parse procedure name from arguments
2. Parse parameters from remaining arguments
3. If procedure name is given but parameters are unclear:
   - Call `mssql_procedures` with the procedure name to get parameter definitions
   - Ask user for parameter values
4. Execute using `mssql_execute_proc` MCP tool with parsed parameters
5. Display results including result sets, output parameters, and return value

## Parameter Formats

Parameters can be specified in several formats:

### Named Parameters (Recommended)
```
/mssql:execute sp_GetOrders @CustomerId=123 @StartDate='2024-01-01'
```

### JSON Format
```
/mssql:execute sp_GetOrders {"CustomerId": 123, "StartDate": "2024-01-01"}
```

### Natural Language
```
/mssql:execute sp_GetOrders with customer id 123 starting from January 2024
```

## Usage Examples

```
/mssql:execute sp_GetCustomerOrders @CustomerId=123
/mssql:execute dbo.sp_UpdateStatus @Id=100 @Status='ACTIVE'
/mssql:execute sp_GenerateReport {"Year": 2024, "Quarter": 4}
/mssql:execute sp_GetTopProducts 10
```

## Output Format

```
Stored Procedure Executed: dbo.sp_GetOrders
==================================================

Parameters:
  @CustomerId = 123
  @StartDate = "2024-01-01"

Return Value: 0

Result Set 1 (5 rows):
------------------------------
OrderId | OrderDate  | Total
--------|------------|--------
1001    | 2024-01-05 | 150.00
1002    | 2024-01-12 | 275.50
...

Execution Time: 45ms
```

## Tips

- Use `@paramName=value` format for clarity
- Date values should be in ISO format: 'YYYY-MM-DD'
- String values should be quoted
- Check procedure parameters with `/mssql:procedures proc_name` first
