import { z } from "zod";
import { FactorNameSchema, MarketSchema, DateStringSchema, TickerSchema } from "../lib/types.js";

export const FactorAnalyzeInputSchema = z.object({
  factors: z.array(FactorNameSchema).min(1),
  market: MarketSchema.optional().default("KOSPI"),
  date: DateStringSchema.optional(),
  topN: z.number().min(1).max(100).optional().default(20),
  ticker: TickerSchema.optional(),
  weights: z.record(z.number()).optional(),
});

export type FactorAnalyzeInput = z.infer<typeof FactorAnalyzeInputSchema>;
