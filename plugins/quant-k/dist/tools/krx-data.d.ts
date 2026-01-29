import { z } from "zod";
export declare const KrxCollectInputSchema: z.ZodObject<{
    dataType: z.ZodEnum<["tickers", "ohlcv", "fundamental", "marketcap"]>;
    market: z.ZodDefault<z.ZodOptional<z.ZodEnum<["KOSPI", "KOSDAQ"]>>>;
    ticker: z.ZodOptional<z.ZodString>;
    startDate: z.ZodOptional<z.ZodString>;
    endDate: z.ZodOptional<z.ZodString>;
    refresh: z.ZodDefault<z.ZodOptional<z.ZodBoolean>>;
}, "strip", z.ZodTypeAny, {
    market: "KOSPI" | "KOSDAQ";
    dataType: "tickers" | "ohlcv" | "fundamental" | "marketcap";
    refresh: boolean;
    ticker?: string | undefined;
    startDate?: string | undefined;
    endDate?: string | undefined;
}, {
    dataType: "tickers" | "ohlcv" | "fundamental" | "marketcap";
    market?: "KOSPI" | "KOSDAQ" | undefined;
    ticker?: string | undefined;
    startDate?: string | undefined;
    endDate?: string | undefined;
    refresh?: boolean | undefined;
}>;
export type KrxCollectInput = z.infer<typeof KrxCollectInputSchema>;
export declare const KrxCollectOutputSchema: z.ZodObject<{
    success: z.ZodBoolean;
    dataType: z.ZodString;
    market: z.ZodOptional<z.ZodString>;
    ticker: z.ZodOptional<z.ZodString>;
    data: z.ZodAny;
    cached: z.ZodBoolean;
    count: z.ZodOptional<z.ZodNumber>;
    error: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    dataType: string;
    success: boolean;
    cached: boolean;
    error?: string | undefined;
    data?: any;
    market?: string | undefined;
    ticker?: string | undefined;
    count?: number | undefined;
}, {
    dataType: string;
    success: boolean;
    cached: boolean;
    error?: string | undefined;
    data?: any;
    market?: string | undefined;
    ticker?: string | undefined;
    count?: number | undefined;
}>;
export type KrxCollectOutput = z.infer<typeof KrxCollectOutputSchema>;
