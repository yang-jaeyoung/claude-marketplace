import { z } from "zod";
export declare const StockScreenInputSchema: z.ZodObject<{
    conditions: z.ZodArray<z.ZodString, "many">;
    market: z.ZodDefault<z.ZodOptional<z.ZodEnum<["KOSPI", "KOSDAQ", "ALL"]>>>;
    date: z.ZodOptional<z.ZodString>;
    sortBy: z.ZodOptional<z.ZodString>;
    sortOrder: z.ZodDefault<z.ZodOptional<z.ZodEnum<["asc", "desc"]>>>;
    limit: z.ZodDefault<z.ZodOptional<z.ZodNumber>>;
    save: z.ZodOptional<z.ZodString>;
    load: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    market: "KOSPI" | "KOSDAQ" | "ALL";
    conditions: string[];
    sortOrder: "asc" | "desc";
    limit: number;
    date?: string | undefined;
    sortBy?: string | undefined;
    save?: string | undefined;
    load?: string | undefined;
}, {
    conditions: string[];
    date?: string | undefined;
    market?: "KOSPI" | "KOSDAQ" | "ALL" | undefined;
    sortBy?: string | undefined;
    sortOrder?: "asc" | "desc" | undefined;
    limit?: number | undefined;
    save?: string | undefined;
    load?: string | undefined;
}>;
export type StockScreenInput = z.infer<typeof StockScreenInputSchema>;
