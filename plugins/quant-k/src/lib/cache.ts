import * as fs from "fs";
import * as path from "path";

const CACHE_BASE = ".omc/quant-k";

export function getCachePath(...segments: string[]): string {
  return path.join(process.cwd(), CACHE_BASE, ...segments);
}

export function ensureCacheDir(cachePath: string): void {
  const dir = path.dirname(cachePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

export function isCacheValid(cachePath: string, ttlHours: number): boolean {
  if (!fs.existsSync(cachePath)) {
    return false;
  }

  const stats = fs.statSync(cachePath);
  const ageHours = (Date.now() - stats.mtimeMs) / (1000 * 60 * 60);
  return ageHours < ttlHours;
}

export function readJsonCache<T>(cachePath: string): T | null {
  try {
    if (!fs.existsSync(cachePath)) {
      return null;
    }
    const content = fs.readFileSync(cachePath, "utf-8");
    return JSON.parse(content) as T;
  } catch {
    return null;
  }
}

export function writeJsonCache(cachePath: string, data: unknown): void {
  ensureCacheDir(cachePath);
  fs.writeFileSync(cachePath, JSON.stringify(data, null, 2));
}
