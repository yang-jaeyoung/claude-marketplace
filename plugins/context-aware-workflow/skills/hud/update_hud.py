#!/usr/bin/env python3
"""
HUD (Heads-Up Display) update script for CAW workflow.

Updates real-time metrics display after each tool use.
Called via PostToolUse hook.

Environment:
    CAW_HUD=enabled|disabled|minimal
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


# Model pricing (per 1M tokens)
PRICING = {
    "haiku": {"input": 0.25, "output": 1.25},
    "sonnet": {"input": 3.00, "output": 15.00},
    "opus": {"input": 15.00, "output": 75.00}
}


def find_caw_root() -> Optional[Path]:
    """Find .caw directory starting from current working directory."""
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        caw_dir = path / ".caw"
        if caw_dir.is_dir():
            return caw_dir
    return None


def load_json_safe(path: Path) -> dict:
    """Load JSON file safely, returning empty dict on failure."""
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def calculate_cost(tokens_in: int, tokens_out: int, model: str) -> float:
    """Calculate cost based on token usage and model."""
    pricing = PRICING.get(model.lower(), PRICING["sonnet"])
    cost = (tokens_in * pricing["input"] + tokens_out * pricing["output"]) / 1_000_000
    return round(cost, 4)


def render_progress_bar(percentage: float, width: int = 12) -> str:
    """Render a text-based progress bar."""
    percentage = max(0, min(100, percentage))
    filled = int(width * percentage / 100)
    empty = width - filled
    return "\u2588" * filled + "\u2591" * empty


def format_tokens(count: int) -> str:
    """Format token count with K suffix for readability."""
    if count >= 1000:
        return f"{count / 1000:.1f}k"
    return str(count)


def format_time(seconds: int) -> str:
    """Format elapsed time as Xm Ys."""
    minutes = seconds // 60
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def get_hud_mode() -> str:
    """Get HUD display mode from environment."""
    mode = os.environ.get("CAW_HUD", "disabled").lower()
    if mode in ("enabled", "true", "1", "full"):
        return "full"
    elif mode == "minimal":
        return "minimal"
    return "disabled"


def update_hud(caw_root: Path) -> dict:
    """Update HUD state from workflow files."""
    # Load workflow state files
    manifest = load_json_safe(caw_root / "manifest.json")
    mode_state = load_json_safe(caw_root / "mode.json")
    metrics = load_json_safe(caw_root / "metrics.json")
    hud_state = load_json_safe(caw_root / "hud.json")

    # Extract phase/step from manifest
    phases = manifest.get("phases", [])
    total_phases = len(phases)
    current_phase = manifest.get("current_phase", 1)

    # Find current step
    current_step = 1
    total_steps = 0
    if phases and current_phase <= total_phases:
        phase_data = phases[current_phase - 1] if isinstance(phases[current_phase - 1], dict) else {}
        steps = phase_data.get("steps", [])
        total_steps = len(steps)
        current_step = phase_data.get("current_step", 1)

    # Calculate progress
    if total_phases > 0 and total_steps > 0:
        phase_progress = (current_phase - 1) / total_phases
        step_progress = (current_step / total_steps) / total_phases
        progress_pct = int((phase_progress + step_progress) * 100)
    else:
        progress_pct = 0

    # Extract metrics
    tokens_in = metrics.get("tokens_in", 0)
    tokens_out = metrics.get("tokens_out", 0)

    # Get model tier
    model_tier = mode_state.get("preferred_tier", "sonnet").lower()
    if mode_state.get("eco_mode"):
        model_tier = "haiku"

    # Calculate cost
    estimated_cost = calculate_cost(tokens_in, tokens_out, model_tier)

    # Calculate elapsed time
    started_at = manifest.get("started_at") or mode_state.get("activated_at")
    elapsed_seconds = 0
    if started_at:
        try:
            start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            elapsed_seconds = int((datetime.now(start_time.tzinfo) - start_time).total_seconds())
        except (ValueError, TypeError):
            pass

    # Build HUD metrics
    hud_metrics = {
        "phase": current_phase,
        "total_phases": total_phases,
        "step": current_step,
        "total_steps": total_steps,
        "progress_pct": progress_pct,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "estimated_cost": estimated_cost,
        "model_tier": model_tier,
        "active_mode": mode_state.get("active_mode", "NORMAL"),
        "eco_mode": mode_state.get("eco_mode", False),
        "elapsed_seconds": elapsed_seconds
    }

    # Update HUD state
    hud_state.update({
        "enabled": get_hud_mode() != "disabled",
        "last_update": datetime.utcnow().isoformat() + "Z",
        "display_mode": get_hud_mode(),
        "metrics": hud_metrics
    })

    # Save HUD state
    try:
        (caw_root / "hud.json").write_text(
            json.dumps(hud_state, indent=2),
            encoding='utf-8'
        )
    except OSError:
        pass

    return hud_metrics


def render_full_hud(metrics: dict) -> str:
    """Render full HUD display."""
    phase = metrics.get("phase", 0)
    total_phases = metrics.get("total_phases", 0)
    step = metrics.get("step", 0)
    total_steps = metrics.get("total_steps", 0)
    progress = metrics.get("progress_pct", 0)
    tokens_in = metrics.get("tokens_in", 0)
    tokens_out = metrics.get("tokens_out", 0)
    cost = metrics.get("estimated_cost", 0)
    model = metrics.get("model_tier", "sonnet").capitalize()
    mode = metrics.get("active_mode", "NORMAL")
    elapsed = metrics.get("elapsed_seconds", 0)

    progress_bar = render_progress_bar(progress)
    tokens_display = format_tokens(tokens_in + tokens_out)
    time_display = format_time(elapsed)

    lines = [
        "\u2501" * 48,
        f" Phase {phase}/{total_phases} \u2502 Step {step}/{total_steps} \u2502 {progress_bar} {progress}%",
        f" Tokens: {tokens_display} \u2502 Cost: ${cost:.2f} \u2502 Model: {model}",
        f" Mode: {mode} \u2502 Time: {time_display}",
        "\u2501" * 48
    ]

    return "\n".join(lines)


def render_minimal_hud(metrics: dict) -> str:
    """Render minimal HUD display."""
    phase = metrics.get("phase", 0)
    total_phases = metrics.get("total_phases", 0)
    progress = metrics.get("progress_pct", 0)
    model = metrics.get("model_tier", "sonnet").capitalize()

    return f"[{progress}%] Phase {phase}/{total_phases} \u2502 {model}"


def main():
    """Main entry point."""
    caw_root = find_caw_root()
    if not caw_root:
        # CAW not active, silent exit
        return

    hud_mode = get_hud_mode()
    if hud_mode == "disabled":
        return

    # Update HUD metrics
    metrics = update_hud(caw_root)

    # Render and output HUD
    if hud_mode == "full":
        output = render_full_hud(metrics)
    else:
        output = render_minimal_hud(metrics)

    # Output to stderr for display (stdout may be captured)
    print(output, file=sys.stderr)


if __name__ == "__main__":
    main()
