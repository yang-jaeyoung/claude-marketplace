/**
 * Runtime Abstraction Layer
 * Provides unified file I/O APIs that work with both Bun and Node.js
 *
 * Detection: Uses globalThis.Bun to check if running in Bun runtime
 * Fallback: Node.js fs/promises APIs when Bun is not available
 */

import { readFile, writeFile, appendFile, access, stat, constants } from 'node:fs/promises';

// Runtime detection
export const isBun = typeof globalThis.Bun !== 'undefined';
export const runtime = isBun ? 'bun' : 'node';

/**
 * Check if a file exists at the given path
 * - Bun: Uses Bun.file().exists()
 * - Node.js: Uses fs.access() with F_OK constant
 */
export async function fileExists(path: string): Promise<boolean> {
  if (isBun) {
    return await Bun.file(path).exists();
  }

  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if a path exists (file or directory)
 * Uses fs.access which works for both files and directories
 */
export async function pathExists(path: string): Promise<boolean> {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if a directory exists at the given path
 */
export async function dirExists(path: string): Promise<boolean> {
  try {
    const stats = await stat(path);
    return stats.isDirectory();
  } catch {
    return false;
  }
}

/**
 * Read file content as text (UTF-8)
 * - Bun: Uses Bun.file().text()
 * - Node.js: Uses fs.readFile() with utf-8 encoding
 */
export async function readText(path: string): Promise<string> {
  if (isBun) {
    return await Bun.file(path).text();
  }

  return await readFile(path, 'utf-8');
}

/**
 * Read file content as text, returns null if file doesn't exist
 * Combines existence check with read for convenience
 */
export async function readTextSafe(path: string): Promise<string | null> {
  if (!(await fileExists(path))) {
    return null;
  }
  return await readText(path);
}

/**
 * Write text content to file (UTF-8)
 * - Bun: Uses Bun.write()
 * - Node.js: Uses fs.writeFile() with utf-8 encoding
 */
export async function writeText(path: string, content: string): Promise<void> {
  if (isBun) {
    await Bun.write(path, content);
    return;
  }

  await writeFile(path, content, 'utf-8');
}

/**
 * Append text content to file (UTF-8)
 * Uses fs.appendFile() for both runtimes to ensure atomic append operations.
 * This prevents race conditions when multiple processes append concurrently.
 *
 * Creates the file if it doesn't exist.
 */
export async function appendText(path: string, content: string): Promise<void> {
  // Use Node.js appendFile for both runtimes - it's atomic and prevents race conditions
  // The previous Bun implementation (read + write) was not safe for concurrent appends
  await appendFile(path, content, 'utf-8');
}

/**
 * Log runtime info (useful for debugging)
 */
export function logRuntimeInfo(): void {
  console.error(`[magic-note] Runtime: ${runtime}`);
  if (isBun) {
    console.error(`[magic-note] Bun version: ${Bun.version}`);
  } else {
    console.error(`[magic-note] Node.js version: ${process.version}`);
  }
}
