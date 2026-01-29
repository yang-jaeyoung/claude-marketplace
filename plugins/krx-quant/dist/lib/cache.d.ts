export declare function getCachePath(...segments: string[]): string;
export declare function ensureCacheDir(cachePath: string): void;
export declare function isCacheValid(cachePath: string, ttlHours: number): boolean;
export declare function readJsonCache<T>(cachePath: string): T | null;
export declare function writeJsonCache(cachePath: string, data: unknown): void;
