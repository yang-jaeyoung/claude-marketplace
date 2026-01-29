import { z } from "zod";
export declare const MarketSchema: z.ZodEnum<["KOSPI", "KOSDAQ"]>;
export type Market = z.infer<typeof MarketSchema>;
export declare const DateStringSchema: z.ZodString;
export declare const TickerSchema: z.ZodString;
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
export declare const FactorNameSchema: z.ZodEnum<["PER", "PBR", "PSR", "PCR", "EV_EBITDA", "MOM_1M", "MOM_3M", "MOM_6M", "MOM_12M", "ROE", "ROA", "GP_MARGIN", "OP_MARGIN", "SIZE", "SIZE_INV", "VOL_20D"]>;
export type FactorName = z.infer<typeof FactorNameSchema>;
export interface FactorScore {
    ticker: string;
    name: string;
    score: number;
    rawValue?: number;
}
export interface ScreenResult {
    ticker: string;
    name: string;
    values: Record<string, number | string>;
}
export declare const ScraperActionSchema: z.ZodEnum<["navigate", "snapshot", "extract_table", "extract_list", "evaluate", "close"]>;
export type ScraperAction = z.infer<typeof ScraperActionSchema>;
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
export declare const ErrorCodes: {
    readonly PYKRX_ERROR: 1001;
    readonly INVALID_TICKER: 1002;
    readonly INVALID_DATE: 1003;
    readonly NO_DATA: 1004;
    readonly INVALID_MARKET: 1101;
    readonly UNKNOWN_FACTOR: 1201;
    readonly DSL_PARSE_ERROR: 1301;
    readonly CACHE_ERROR: 1401;
    readonly BROWSER_ERROR: 1501;
    readonly NAVIGATION_ERROR: 1502;
    readonly EXTRACTION_ERROR: 1503;
    readonly SCRIPT_ERROR: 1504;
};
