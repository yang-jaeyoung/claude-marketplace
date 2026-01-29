import { z } from "zod";
import { DateStringSchema } from "../lib/types.js";
export const StockScreenInputSchema = z.object({
    conditions: z.array(z.string()).min(1),
    market: z.enum(["KOSPI", "KOSDAQ", "ALL"]).optional().default("KOSPI"),
    date: DateStringSchema.optional(),
    sortBy: z.string().optional(),
    sortOrder: z.enum(["asc", "desc"]).optional().default("desc"),
    limit: z.number().min(1).max(500).optional().default(100),
    save: z.string().optional(),
    load: z.string().optional(),
});
