#!/usr/bin/env python3
"""
Check plan adherence for Edit/Write tool use.

This PreToolUse hook validates that file modifications align with the current
task plan and provides context about the current step.

Output format:
{
  "result": "approve",
  "additionalContext": "[CAW] Phase 1/3 | Step 2/8 | Expected files: src/auth.ts"
}
"""

import json
import sys

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def find_caw_root() -> Optional[Path]:
    """Find .caw directory starting from current working directory."""
    cwd = Path.cwd()

    # Check current directory and parents
    for path in [cwd, *cwd.parents]:
        caw_dir = path / ".caw"
        if caw_dir.is_dir():
            return caw_dir

    return None


def extract_current_step(content: str) -> Optional[Tuple[str, int, int]]:
    """
    Extract the current in-progress step from plan content.

    Returns: (step_description, step_number, total_steps) or None
    """
    lines = content.split("\n")
    completed_count = 0
    total_count = 0
    current_step = None
    current_step_num = None

    for line in lines:
        stripped = line.strip()

        # Count checkboxes
        if re.match(r"^-\s*\[[ xX]\]", stripped):
            total_count += 1

            # Check if completed
            if re.match(r"^-\s*\[[xX]\]", stripped):
                completed_count += 1
            elif current_step is None:
                # First uncompleted step is the current step
                current_step = re.sub(r"^-\s*\[ \]\s*", "", stripped)
                current_step_num = total_count

    if current_step:
        return (current_step, current_step_num, total_count)

    return None


def extract_phase_info(content: str) -> Optional[Tuple[int, int]]:
    """
    Extract phase information from plan content.

    Looks for patterns like "## Phase 1" or "### Phase 1:"
    Returns: (current_phase, total_phases) or None
    """
    phases = re.findall(r"^#{2,4}\s*Phase\s+(\d+)", content, re.MULTILINE | re.IGNORECASE)

    if not phases:
        return None

    total_phases = len(phases)

    # Find the phase containing first uncompleted step
    lines = content.split("\n")
    current_phase = 1
    in_phase = 0

    for line in lines:
        stripped = line.strip()

        # Check for phase header
        phase_match = re.match(r"^#{2,4}\s*Phase\s+(\d+)", stripped, re.IGNORECASE)
        if phase_match:
            in_phase = int(phase_match.group(1))

        # Check for first uncompleted step
        if re.match(r"^-\s*\[ \]", stripped):
            current_phase = in_phase if in_phase > 0 else 1
            break

    return (current_phase, total_phases)


def extract_expected_files(content: str) -> list[str]:
    """
    Extract expected files from the current step context.

    Looks for backticked file paths near the current step.
    """
    # Find files mentioned in backticks
    file_pattern = re.compile(r"`([^`]+\.(ts|tsx|js|jsx|py|rs|go|json|md|yaml|yml))`")
    matches = file_pattern.findall(content)

    # Return unique files, limited to 3 for brevity
    files = list(dict.fromkeys(m[0] for m in matches))
    return files[:3]


def truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def main():
    """Main entry point."""
    try:
        # Find .caw directory
        caw_root = find_caw_root()

        if not caw_root:
            # CAW not active - silently approve
            print(json.dumps({"result": "approve"}))
            return

        # Read task_plan.md
        plan_file = caw_root / "task_plan.md"
        if not plan_file.exists():
            print(json.dumps({"result": "approve"}))
            return

        content = plan_file.read_text(encoding="utf-8")

        if not content.strip():
            print(json.dumps({"result": "approve"}))
            return

        # Extract information
        step_info = extract_current_step(content)
        phase_info = extract_phase_info(content)
        expected_files = extract_expected_files(content)

        # Build additionalContext (max 200 chars)
        parts = ["[CAW]"]

        if phase_info:
            parts.append(f"Phase {phase_info[0]}/{phase_info[1]}")

        if step_info:
            step_desc, step_num, total_steps = step_info
            parts.append(f"Step {step_num}/{total_steps}")

            # Add truncated step description
            step_short = truncate(step_desc, 40)
            parts.append(f"Current: {step_short}")

        if expected_files:
            files_str = ", ".join(os.path.basename(f) for f in expected_files[:2])
            if len(expected_files) > 2:
                files_str += f" +{len(expected_files)-2}"
            parts.append(f"Files: {files_str}")

        # Join with " | " separator
        context = " | ".join(parts)

        # Ensure total length is under 200 chars
        context = truncate(context, 200)

        output = {
            "result": "approve",
            "additionalContext": context
        }

        print(json.dumps(output))

    except Exception:
        # Silent failure - approve by default
        print(json.dumps({"result": "approve"}))


if __name__ == "__main__":
    main()
