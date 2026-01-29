import { z } from "zod";
export declare const FactorAnalyzeInputSchema: z.ZodObject<{
    factors: z.ZodArray<z.ZodEnum<["PER", "PBR", "PSR", "PCR", "EV_EBITDA", "MOM_1M", "MOM_3M", "MOM_6M", "MOM_12M", "ROE", "ROA", "GP_MARGIN", "OP_MARGIN", "SIZE", "SIZE_INV", "VOL_20D"]>, "many">;
    market: z.ZodDefault<z.ZodOptional<z.ZodEnum<["KOSPI", "KOSDAQ"]>>>;
    date: z.ZodOptional<z.ZodString>;
    topN: z.ZodDefault<z.ZodOptional<z.ZodNumber>>;
    ticker: z.ZodOptional<z.ZodString>;
    weights: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodNumber>>;
}, "strip", z.ZodTypeAny, {
    market: "KOSPI" | "KOSDAQ";
    factors: ("PER" | "PBR" | "PSR" | "PCR" | "EV_EBITDA" | "MOM_1M" | "MOM_3M" | "MOM_6M" | "MOM_12M" | "ROE" | "ROA" | "GP_MARGIN" | "OP_MARGIN" | "SIZE" | "SIZE_INV" | "VOL_20D")[];
    topN: number;
    date?: string | undefined;
    ticker?: string | undefined;
    weights?: Record<string, number> | undefined;
}, {
    factors: ("PER" | "PBR" | "PSR" | "PCR" | "EV_EBITDA" | "MOM_1M" | "MOM_3M" | "MOM_6M" | "MOM_12M" | "ROE" | "ROA" | "GP_MARGIN" | "OP_MARGIN" | "SIZE" | "SIZE_INV" | "VOL_20D")[];
    date?: string | undefined;
    market?: "KOSPI" | "KOSDAQ" | undefined;
    ticker?: string | undefined;
    topN?: number | undefined;
    weights?: Record<string, number> | undefined;
}>;
export type FactorAnalyzeInput = z.infer<typeof FactorAnalyzeInputSchema>;
