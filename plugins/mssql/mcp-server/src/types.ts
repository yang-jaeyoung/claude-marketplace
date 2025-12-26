export interface ConnectionConfig {
  server: string;
  database: string;
  options: {
    trustedConnection: boolean;
    trustServerCertificate: boolean;
    encrypt: boolean;
  };
  connectionTimeout: number;
  requestTimeout: number;
}

export interface QueryResult {
  columns: ColumnInfo[];
  rows: Record<string, unknown>[];
  rowCount: number;
  affectedRows?: number;
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  maxLength?: number;
  precision?: number;
  scale?: number;
}

export interface TableInfo {
  schema: string;
  name: string;
  type: 'TABLE' | 'VIEW';
  rowCount?: number;
}

export interface SchemaInfo {
  tableName: string;
  schemaName: string;
  columns: ColumnDetail[];
  primaryKey?: PrimaryKeyInfo;
  foreignKeys: ForeignKeyInfo[];
  indexes: IndexInfo[];
}

export interface ColumnDetail {
  name: string;
  dataType: string;
  maxLength: number | null;
  precision: number | null;
  scale: number | null;
  isNullable: boolean;
  defaultValue: string | null;
  isIdentity: boolean;
  isComputed: boolean;
}

export interface PrimaryKeyInfo {
  name: string;
  columns: string[];
}

export interface ForeignKeyInfo {
  name: string;
  columns: string[];
  referencedTable: string;
  referencedColumns: string[];
}

export interface IndexInfo {
  name: string;
  columns: string[];
  isUnique: boolean;
  isPrimaryKey: boolean;
  type: string;
}

export interface ProcedureInfo {
  schema: string;
  name: string;
  parameters: ParameterInfo[];
  createDate: string;
  modifyDate: string;
}

export interface ParameterInfo {
  name: string;
  dataType: string;
  maxLength: number | null;
  isOutput: boolean;
  hasDefault: boolean;
  defaultValue: string | null;
}

export interface ProcedureExecutionResult {
  resultSets: Record<string, unknown>[][];
  outputParameters: Record<string, unknown>;
  returnValue?: number;
  executionTime: number;
}

export enum QueryType {
  SELECT = 'SELECT',
  INSERT = 'INSERT',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  DDL = 'DDL',
  EXEC = 'EXEC',
  OTHER = 'OTHER'
}

export interface QueryAnalysis {
  type: QueryType;
  isDangerous: boolean;
  dangerReason?: string;
  requiresConfirmation: boolean;
  tables: string[];
}

export enum SqlErrorCode {
  CONNECTION_FAILED = 'CONNECTION_FAILED',
  QUERY_TIMEOUT = 'QUERY_TIMEOUT',
  SYNTAX_ERROR = 'SYNTAX_ERROR',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  OBJECT_NOT_FOUND = 'OBJECT_NOT_FOUND',
  DDL_BLOCKED = 'DDL_BLOCKED',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNKNOWN = 'UNKNOWN'
}

export interface SqlError {
  code: SqlErrorCode;
  message: string;
  details?: string;
  suggestion?: string;
}
