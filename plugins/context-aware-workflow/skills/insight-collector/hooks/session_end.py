#!/usr/bin/env python3
"""
Session End Hook for Insight Collector

Cleans up session state and optionally triggers analysis when session ends.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

def get_project_dir() -> Path:
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))

def get_caw_dir() -> Path:
    return get_project_dir() / '.caw'

def cleanup_session():
    """Clean up session-specific files."""
    session_file = get_caw_dir() / 'observations' / '.session_id'
    if session_file.exists():
        try:
            session_file.unlink()
        except IOError:
            pass

def check_auto_analyze():
    """Check if auto-analysis should be triggered."""
    obs_file = get_caw_dir() / 'observations' / 'observations.jsonl'
    if not obs_file.exists():
        return False

    # Trigger analysis if observations > 100 lines
    try:
        with open(obs_file, 'r') as f:
            line_count = sum(1 for _ in f)
        return line_count >= 100
    except IOError:
        return False

def main():
    cleanup_session()

    if check_auto_analyze():
        print("Session ended. Run 'python3 scripts/instinct-cli.py analyze' to generate instincts from observations.", file=sys.stderr)

    sys.exit(0)

if __name__ == '__main__':
    main()
