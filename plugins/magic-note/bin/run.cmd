@echo off
REM Magic Note MCP Server Launcher for Windows
REM Detects available runtime and executes server
REM Priority: Bun > Node.js (native TS) > Node.js + tsx

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SERVER_PATH=%SCRIPT_DIR%..\src\mcp\server.ts"

REM Check if Bun is available
where bun >nul 2>&1
if %ERRORLEVEL% equ 0 (
    bun run "%SERVER_PATH%"
    exit /b %ERRORLEVEL%
)

REM Check if Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% equ 0 (
    REM Get Node.js version
    for /f "tokens=1 delims=v" %%a in ('node -v') do set "NODE_VERSION=%%a"
    for /f "tokens=1,2 delims=." %%a in ("!NODE_VERSION!") do (
        set "NODE_MAJOR=%%a"
        set "NODE_MINOR=%%b"
    )

    REM Node.js 23.6+ or 22.18+ supports native TypeScript
    if !NODE_MAJOR! geq 24 (
        node "%SERVER_PATH%"
        exit /b %ERRORLEVEL%
    )
    if !NODE_MAJOR! equ 23 if !NODE_MINOR! geq 6 (
        node "%SERVER_PATH%"
        exit /b %ERRORLEVEL%
    )
    if !NODE_MAJOR! equ 22 if !NODE_MINOR! geq 18 (
        node "%SERVER_PATH%"
        exit /b %ERRORLEVEL%
    )

    REM Try tsx as fallback
    where npx >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        npx tsx "%SERVER_PATH%"
        exit /b %ERRORLEVEL%
    )

    REM Final fallback: try node with experimental flag
    node --experimental-strip-types "%SERVER_PATH%"
    exit /b %ERRORLEVEL%
)

echo [magic-note] Error: No compatible runtime found. >&2
echo [magic-note] Please install one of: >&2
echo   - Bun: https://bun.sh/ >&2
echo   - Node.js 22.18+: https://nodejs.org/ >&2
exit /b 1
