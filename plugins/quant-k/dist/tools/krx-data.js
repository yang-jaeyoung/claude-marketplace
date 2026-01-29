import { z } from "zod";
import { MarketSchema, DateStringSchema, TickerSchema } from "../lib/types.js";
export const KrxCollectInputSchema = z.object({
    dataType: z.enum(["tickers", "ohlcv", "fundamental", "marketcap"]),
    market: MarketSchema.optional().default("KOSPI"),
    ticker: TickerSchema.optional(),
    startDate: DateStringSchema.optional(),
    endDate: DateStringSchema.optional(),
    refresh: z.boolean().optional().default(false),
});
export const KrxCollectOutputSchema = z.object({
    success: z.boolean(),
    dataType: z.string(),
    market: z.string().optional(),
    ticker: z.string().optional(),
    data: z.any(),
    cached: z.boolean(),
    count: z.number().optional(),
    error: z.string().optional(),
});
