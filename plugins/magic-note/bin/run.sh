#!/bin/bash
#
# Magic Note MCP Server Launcher
# Detects available runtime and executes server
#
# Priority: Bun > Node.js (native TS) > Node.js + tsx
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PATH="$SCRIPT_DIR/../src/mcp/server.ts"

# Check if Bun is available
if command -v bun &> /dev/null; then
    exec bun run "$SERVER_PATH"
fi

# Check Node.js version for native TypeScript support
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | cut -d'v' -f2)
    NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d'.' -f1)
    NODE_MINOR=$(echo "$NODE_VERSION" | cut -d'.' -f2)

    # Node.js 23.6+ or 22.18+ supports native TypeScript
    if [ "$NODE_MAJOR" -ge 24 ] || \
       [ "$NODE_MAJOR" -eq 23 -a "$NODE_MINOR" -ge 6 ] || \
       [ "$NODE_MAJOR" -eq 22 -a "$NODE_MINOR" -ge 18 ]; then
        exec node "$SERVER_PATH"
    fi

    # Try tsx as fallback
    if command -v npx &> /dev/null; then
        exec npx tsx "$SERVER_PATH"
    fi

    # Final fallback: try node with experimental flag
    exec node --experimental-strip-types "$SERVER_PATH"
fi

echo "[magic-note] Error: No compatible runtime found." >&2
echo "[magic-note] Please install one of:" >&2
echo "  - Bun: https://bun.sh/" >&2
echo "  - Node.js 22.18+: https://nodejs.org/" >&2
exit 1
