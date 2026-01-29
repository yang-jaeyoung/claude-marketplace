import * as fs from "fs";
import * as path from "path";
const CACHE_BASE = ".omc/quant-k";
export function getCachePath(...segments) {
    return path.join(process.cwd(), CACHE_BASE, ...segments);
}
export function ensureCacheDir(cachePath) {
    const dir = path.dirname(cachePath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}
export function isCacheValid(cachePath, ttlHours) {
    if (!fs.existsSync(cachePath)) {
        return false;
    }
    const stats = fs.statSync(cachePath);
    const ageHours = (Date.now() - stats.mtimeMs) / (1000 * 60 * 60);
    return ageHours < ttlHours;
}
export function readJsonCache(cachePath) {
    try {
        if (!fs.existsSync(cachePath)) {
            return null;
        }
        const content = fs.readFileSync(cachePath, "utf-8");
        return JSON.parse(content);
    }
    catch {
        return null;
    }
}
export function writeJsonCache(cachePath, data) {
    ensureCacheDir(cachePath);
    fs.writeFileSync(cachePath, JSON.stringify(data, null, 2));
}
