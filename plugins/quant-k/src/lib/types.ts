import { z } from "zod";

// Common schemas
export const MarketSchema = z.enum(["KOSPI", "KOSDAQ"]);
export type Market = z.infer<typeof MarketSchema>;

export const DateStringSchema = z.string().regex(/^\d{8}$/, "Date must be YYYYMMDD format");
export const TickerSchema = z.string().regex(/^\d{6}$/, "Ticker must be 6 digits");

// KRX Data types
export interface TickerInfo {
  ticker: string;
  name: string;
  market: Market;
}

export interface OHLCVData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface FundamentalData {
  PER: number;
  PBR: number;
  DIV: number;
  EPS: number;
  BPS: number;
}

// Factor types
export const FactorNameSchema = z.enum([
  "PER", "PBR", "PSR", "PCR", "EV_EBITDA",
  "MOM_1M", "MOM_3M", "MOM_6M", "MOM_12M",
  "ROE", "ROA", "GP_MARGIN", "OP_MARGIN",
  "SIZE", "SIZE_INV", "VOL_20D"
]);
export type FactorName = z.infer<typeof FactorNameSchema>;

export interface FactorScore {
  ticker: string;
  name: string;
  score: number;
  rawValue?: number;
}

// Screening types
export interface ScreenResult {
  ticker: string;
  name: string;
  values: Record<string, number | string>;
}

// Scraper action types
export const ScraperActionSchema = z.enum([
  "navigate", "snapshot", "extract_table", "extract_list", "evaluate", "close"
]);
export type ScraperAction = z.infer<typeof ScraperActionSchema>;

// Scraper result types
export interface ScraperNavigateResult {
  title: string;
  url: string;
}

export interface ScraperSnapshotNode {
  role: string;
  name?: string;
  children?: ScraperSnapshotNode[];
}

export interface ScraperTableResult {
  headers: string[];
  rows: Record<string, string>[];
  rowCount: number;
}

export interface ScraperListResult {
  items: Record<string, string>[];
  count: number;
}

export interface ScraperEvaluateResult {
  result: unknown;
}

// Error codes
export const ErrorCodes = {
  PYKRX_ERROR: 1001,
  INVALID_TICKER: 1002,
  INVALID_DATE: 1003,
  NO_DATA: 1004,
  INVALID_MARKET: 1101,
  UNKNOWN_FACTOR: 1201,
  DSL_PARSE_ERROR: 1301,
  CACHE_ERROR: 1401,
  BROWSER_ERROR: 1501,
  NAVIGATION_ERROR: 1502,
  EXTRACTION_ERROR: 1503,
  SCRIPT_ERROR: 1504,
} as const;
