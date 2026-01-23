#!/usr/bin/env python3
"""
OMC (Oh-My-ClaudeCode) Resolver for CAW Integration.

Detects OMC availability and resolves agent requests with graceful fallback.

Usage:
    python omc_resolver.py                    # Output detection info as JSON
    python omc_resolver.py resolve <agent>    # Resolve agent name

Environment Variables:
    OMC_ENABLED=true     Force OMC detection as enabled
    OMC_DEBUG=enabled    Enable debug logging

Detection Methods (in priority order):
    1. OMC_ENABLED environment variable
    2. Plugin directory (~/.claude/plugins/oh-my-claudecode/)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Module-level cache
_omc_detection_cache: Optional[Dict[str, Any]] = None

# OMC Agent to CAW Fallback Mapping
FALLBACK_MAP: Dict[str, str] = {
    # Architecture & Design
    "omc:architect": "cw:architect",
    "omc:architect-low": "cw:architect",
    "omc:architect-medium": "cw:architect",
    "omc:designer": "cw:designer",
    "omc:designer-high": "cw:designer",
    "omc:designer-low": "cw:designer",

    # Research & Analysis
    "omc:researcher": "cw:Planner",
    "omc:researcher-low": "cw:planner-haiku",
    "omc:scientist": "cw:Builder",
    "omc:scientist-high": "cw:Builder",
    "omc:scientist-low": "cw:builder-haiku",
    "omc:analyst": "cw:planner-opus",

    # Exploration
    "omc:explore": "Explore",
    "omc:explore-medium": "Explore",

    # Execution & Building
    "omc:executor": "cw:Builder",
    "omc:executor-high": "cw:Builder",
    "omc:executor-low": "cw:builder-haiku",
    "omc:build-fixer": "cw:Fixer",
    "omc:build-fixer-low": "cw:fixer-haiku",

    # Quality & Review
    "omc:qa-tester": "cw:Reviewer",
    "omc:critic": "cw:reviewer-opus",
    "omc:code-reviewer": "cw:reviewer-opus",
    "omc:code-reviewer-low": "cw:reviewer-haiku",
    "omc:security-reviewer": "cw:reviewer-opus",
    "omc:security-reviewer-low": "cw:reviewer-haiku",

    # TDD & Testing
    "omc:tdd-guide": "cw:Builder",
    "omc:tdd-guide-low": "cw:builder-haiku",

    # Planning
    "omc:planner": "cw:Planner",

    # Content & Documentation
    "omc:writer": "general-purpose",
    "omc:vision": "general-purpose",
}

# Features degraded when OMC is not available
DEGRADED_FEATURES: List[str] = [
    "ultraqa:advanced_diagnosis",
    "research:specialized_agents",
    "qaloop:intelligent_fix",
    "autopilot:orchestration",
    "ralph:verification",
]


def debug_log(message: str) -> None:
    """Log debug message to stderr if OMC_DEBUG is enabled."""
    if os.environ.get("OMC_DEBUG", "").lower() in ("enabled", "true", "1"):
        print(f"[OMC Debug] {message}", file=sys.stderr)


def get_omc_plugin_paths() -> List[Path]:
    """Get possible OMC plugin installation paths."""
    home = Path.home()
    paths = [
        home / ".claude" / "plugins" / "oh-my-claudecode",
        home / ".config" / "claude" / "plugins" / "oh-my-claudecode",
    ]

    # Windows-specific paths
    if sys.platform == 'win32':
        appdata = os.environ.get("APPDATA", "")
        localappdata = os.environ.get("LOCALAPPDATA", "")
        programfiles = os.environ.get("PROGRAMFILES", "")
        programfiles_x86 = os.environ.get("PROGRAMFILES(X86)", "")

        if appdata:
            paths.append(Path(appdata) / "Claude" / "plugins" / "oh-my-claudecode")
        if localappdata:
            paths.append(Path(localappdata) / "Claude" / "plugins" / "oh-my-claudecode")
        if programfiles:
            paths.append(Path(programfiles) / "Claude" / "plugins" / "oh-my-claudecode")
        if programfiles_x86:
            paths.append(Path(programfiles_x86) / "Claude" / "plugins" / "oh-my-claudecode")

    return paths


def detect_omc() -> Dict[str, Any]:
    """
    Detect OMC availability with full metadata.

    Returns:
        Dict with detection results including:
        - omc_available: bool
        - omc_version: str or None
        - detection_method: str
        - fallback_mode: bool
        - degraded_features: list
        - detected_at: ISO8601 timestamp
    """
    global _omc_detection_cache

    # Return cached result if available
    if _omc_detection_cache is not None:
        debug_log("Using cached OMC detection result")
        return _omc_detection_cache

    result: Dict[str, Any] = {
        "omc_available": False,
        "omc_version": None,
        "detection_method": "not_found",
        "fallback_mode": True,
        "degraded_features": DEGRADED_FEATURES.copy(),
        "detected_at": datetime.now().isoformat(),
    }

    # Method 1: Environment variable (highest priority)
    env_value = os.environ.get("OMC_ENABLED", "").lower()
    if env_value in ("true", "1", "enabled"):
        debug_log("OMC detected via OMC_ENABLED environment variable")
        result["omc_available"] = True
        result["detection_method"] = "env_variable"
        result["fallback_mode"] = False
        result["degraded_features"] = []
        _omc_detection_cache = result
        return result

    # Method 2: Plugin directory check
    for plugin_path in get_omc_plugin_paths():
        if plugin_path.is_dir():
            debug_log(f"OMC detected at: {plugin_path}")
            result["omc_available"] = True
            result["detection_method"] = "plugin_directory"
            result["fallback_mode"] = False
            result["degraded_features"] = []

            # Try to get version from plugin.json
            plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
            if plugin_json.exists():
                try:
                    with open(plugin_json, "r", encoding="utf-8") as f:
                        plugin_data = json.load(f)
                        result["omc_version"] = plugin_data.get("version")
                        debug_log(f"OMC version: {result['omc_version']}")
                except (json.JSONDecodeError, IOError) as e:
                    debug_log(f"Failed to read OMC version: {e}")

            _omc_detection_cache = result
            return result

    debug_log("OMC not detected")
    _omc_detection_cache = result
    return result


def is_omc_available() -> bool:
    """
    Check if OMC is available (cached).

    Returns:
        True if OMC plugin is detected, False otherwise.
    """
    return detect_omc()["omc_available"]


def resolve_agent(requested_agent: str) -> Tuple[str, bool, Optional[str]]:
    """
    Resolve agent request with fallback if needed.

    Args:
        requested_agent: Agent identifier (e.g., "omc:architect", "cw:Builder")

    Returns:
        Tuple of (resolved_agent, is_fallback, warning_message)
    """
    if not requested_agent:
        return ("general-purpose", False, None)

    # Parse namespace
    if ":" in requested_agent:
        namespace, agent_name = requested_agent.split(":", 1)
    else:
        # Bare agent name - assume as-is
        return (requested_agent, False, None)

    # CAW agents pass through
    if namespace == "cw":
        debug_log(f"CAW agent, no resolution needed: {requested_agent}")
        return (requested_agent, False, None)

    # OMC agents need resolution
    if namespace == "omc":
        if is_omc_available():
            debug_log(f"OMC available, using original: {requested_agent}")
            return (requested_agent, False, None)
        else:
            fallback = FALLBACK_MAP.get(requested_agent)
            if fallback:
                warning = f"OMC not available, using CAW fallback: {fallback}"
                debug_log(warning)
                return (fallback, True, warning)
            else:
                # Unknown OMC agent - fall back to general-purpose
                warning = f"Unknown OMC agent '{requested_agent}', using general-purpose"
                debug_log(warning)
                return ("general-purpose", True, warning)

    # Unknown namespace - return as-is
    debug_log(f"Unknown namespace '{namespace}', passing through: {requested_agent}")
    return (requested_agent, False, None)


def get_fallback_map() -> Dict[str, str]:
    """
    Get the complete OMC to CAW fallback mapping.

    Returns:
        Dict mapping OMC agent IDs to CAW fallback agents.
    """
    return FALLBACK_MAP.copy()


def update_manifest_environment(manifest_path: Path) -> bool:
    """
    Update context manifest with environment detection info.

    Args:
        manifest_path: Path to context_manifest.json

    Returns:
        True if update successful, False otherwise.
    """
    detection = detect_omc()

    try:
        manifest_data: Dict[str, Any] = {}

        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

        manifest_data["environment"] = detection

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        debug_log(f"Updated manifest environment: {manifest_path}")
        return True

    except (json.JSONDecodeError, IOError) as e:
        debug_log(f"Failed to update manifest: {e}")
        return False


def find_caw_root() -> Optional[Path]:
    """Find .caw directory starting from current working directory."""
    cwd = Path.cwd()

    for path in [cwd, *cwd.parents]:
        caw_dir = path / ".caw"
        if caw_dir.is_dir():
            return caw_dir

    return None


def main() -> None:
    """CLI entry point."""
    args = sys.argv[1:]

    if not args:
        # Default: output detection info as JSON
        detection = detect_omc()
        print(json.dumps(detection, indent=2, ensure_ascii=False))
        return

    command = args[0].lower()

    if command == "resolve" and len(args) > 1:
        agent = args[1]
        resolved, is_fallback, warning = resolve_agent(agent)
        result = {
            "requested": agent,
            "resolved": resolved,
            "is_fallback": is_fallback,
            "warning": warning,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "fallbacks":
        print(json.dumps(get_fallback_map(), indent=2, ensure_ascii=False))

    elif command == "update-manifest":
        caw_root = find_caw_root()
        if caw_root:
            manifest_path = caw_root / "context_manifest.json"
            success = update_manifest_environment(manifest_path)
            print(json.dumps({"success": success, "path": str(manifest_path)}))
        else:
            print(json.dumps({"success": False, "error": "CAW root not found"}))

    elif command == "help" or command == "--help" or command == "-h":
        print(__doc__)
        print("\nCommands:")
        print("  (none)            Output OMC detection info as JSON")
        print("  resolve <agent>   Resolve agent with fallback")
        print("  fallbacks         Show all fallback mappings")
        print("  update-manifest   Update context_manifest.json with environment info")
        print("  help              Show this help message")

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Use 'help' for usage information", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
