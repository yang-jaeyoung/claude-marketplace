#!/usr/bin/env node
/**
 * Magic Note MCP Server Launcher
 * Cross-platform runtime detection and execution
 *
 * Priority:
 * 1. Bun (fastest, recommended)
 * 2. Node.js 22.18+/23.6+ (native TypeScript)
 * 3. Node.js + tsx (fallback)
 */

import { spawn, execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { existsSync } from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const SERVER_PATH = join(__dirname, '..', 'src', 'mcp', 'server.ts');

/**
 * Check if a command exists in PATH
 * Uses 'where' on Windows, 'which' on Unix-like systems
 */
function commandExists(cmd) {
  try {
    const whichCmd = process.platform === 'win32' ? 'where' : 'which';
    execFileSync(whichCmd, [cmd], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Get Node.js version as [major, minor, patch]
 */
function getNodeVersion() {
  const version = process.version.slice(1); // Remove 'v' prefix
  return version.split('.').map(Number);
}

/**
 * Check if Node.js supports native TypeScript (22.18+ or 23.6+)
 */
function supportsNativeTypeScript() {
  const [major, minor] = getNodeVersion();
  return (
    major >= 24 ||
    (major === 23 && minor >= 6) ||
    (major === 22 && minor >= 18)
  );
}

/**
 * Execute server with the best available runtime
 */
async function main() {
  // Check if server file exists
  if (!existsSync(SERVER_PATH)) {
    console.error(`[magic-note] Error: Server file not found: ${SERVER_PATH}`);
    process.exit(1);
  }

  // Priority 1: Bun
  if (commandExists('bun')) {
    console.error('[magic-note] Using Bun runtime');
    const child = spawn('bun', ['run', SERVER_PATH], {
      stdio: 'inherit',
      shell: process.platform === 'win32',
    });
    child.on('exit', (code) => process.exit(code ?? 0));
    return;
  }

  // Priority 2: Node.js with native TypeScript support
  if (supportsNativeTypeScript()) {
    console.error('[magic-note] Using Node.js native TypeScript');
    const child = spawn(process.execPath, [SERVER_PATH], {
      stdio: 'inherit',
    });
    child.on('exit', (code) => process.exit(code ?? 0));
    return;
  }

  // Priority 3: Node.js with tsx
  if (commandExists('npx')) {
    console.error('[magic-note] Using Node.js + tsx');
    const child = spawn('npx', ['tsx', SERVER_PATH], {
      stdio: 'inherit',
      shell: process.platform === 'win32',
    });
    child.on('exit', (code) => process.exit(code ?? 0));
    return;
  }

  // Priority 4: Node.js with experimental flag (older versions)
  console.error('[magic-note] Using Node.js experimental TypeScript support');
  const child = spawn(process.execPath, ['--experimental-strip-types', SERVER_PATH], {
    stdio: 'inherit',
  });
  child.on('exit', (code) => process.exit(code ?? 0));
}

main().catch((error) => {
  console.error('[magic-note] Launcher error:', error.message);
  process.exit(1);
});
