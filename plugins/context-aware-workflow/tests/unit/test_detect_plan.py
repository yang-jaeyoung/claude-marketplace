#!/usr/bin/env python3
"""
Unit tests for detect_plan.py

Tests the plan detection and analysis functions.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "skills" / "context-manager" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from detect_plan import (
    extract_title,
    calculate_completion,
    extract_files_mentioned,
    count_steps,
    format_time_ago,
    is_recent,
)


class TestExtractTitle(unittest.TestCase):
    """Test title extraction from plan content."""

    def test_h1_header(self):
        """Extract title from H1 header."""
        content = "# My Plan Title\n\nSome content"
        self.assertEqual(extract_title(content), "My Plan Title")

    def test_h2_header(self):
        """Extract title from H2 header when no H1."""
        content = "## Secondary Title\n\nContent here"
        self.assertEqual(extract_title(content), "Secondary Title")

    def test_fallback_first_line(self):
        """Fall back to first non-empty line."""
        content = "Just some text\n\nMore content"
        self.assertEqual(extract_title(content), "Just some text")

    def test_empty_content(self):
        """Handle empty content."""
        content = ""
        self.assertEqual(extract_title(content), "Unknown Plan")

    def test_whitespace_only(self):
        """Handle whitespace-only content."""
        content = "   \n\n   \n"
        self.assertEqual(extract_title(content), "Unknown Plan")

    def test_truncates_long_first_line(self):
        """Truncate very long first lines."""
        content = "A" * 100 + "\n\nContent"
        result = extract_title(content)
        self.assertLessEqual(len(result), 50)


class TestCalculateCompletion(unittest.TestCase):
    """Test completion rate calculation."""

    def test_all_complete(self):
        """100% completion when all checked."""
        content = "- [x] Task 1\n- [X] Task 2\n- [x] Task 3"
        self.assertEqual(calculate_completion(content), 1.0)

    def test_all_incomplete(self):
        """0% completion when none checked."""
        content = "- [ ] Task 1\n- [ ] Task 2\n- [ ] Task 3"
        self.assertEqual(calculate_completion(content), 0.0)

    def test_partial_completion(self):
        """Correct percentage for partial completion."""
        content = "- [x] Done\n- [ ] Pending"
        self.assertEqual(calculate_completion(content), 0.5)

    def test_no_checkboxes(self):
        """0% when no checkboxes present."""
        content = "Just regular text\n- Regular list item"
        self.assertEqual(calculate_completion(content), 0.0)

    def test_mixed_case_x(self):
        """Handle both lowercase and uppercase X."""
        content = "- [x] lower\n- [X] upper\n- [ ] pending"
        self.assertAlmostEqual(calculate_completion(content), 0.67, places=2)


class TestExtractFilesMentioned(unittest.TestCase):
    """Test file path extraction from plan content."""

    def test_backtick_paths(self):
        """Extract paths in backticks."""
        content = "Edit `src/auth/jwt.ts` and `src/utils/helpers.py`"
        files = extract_files_mentioned(content)
        self.assertIn("src/auth/jwt.ts", files)
        self.assertIn("src/utils/helpers.py", files)

    def test_filters_non_files(self):
        """Filter out non-file backtick content."""
        content = "Use `npm install` and `git commit`"
        files = extract_files_mentioned(content)
        self.assertEqual(len(files), 0)

    def test_common_extensions(self):
        """Include files with common extensions."""
        content = "Files: `config.json`, `README.md`, `styles.yaml`"
        files = extract_files_mentioned(content)
        self.assertEqual(len(files), 3)

    def test_sorted_output(self):
        """Results should be sorted."""
        content = "`z.ts`, `a.ts`, `m.ts`"
        files = extract_files_mentioned(content)
        self.assertEqual(files, sorted(files))


class TestCountSteps(unittest.TestCase):
    """Test step counting."""

    def test_count_all_types(self):
        """Count completed, pending, and total."""
        content = """
        - [x] Done 1
        - [X] Done 2
        - [ ] Pending 1
        - [ ] Pending 2
        - [ ] Pending 3
        """
        counts = count_steps(content)
        self.assertEqual(counts["completed"], 2)
        self.assertEqual(counts["pending"], 3)
        self.assertEqual(counts["total"], 5)

    def test_empty_content(self):
        """Handle content with no steps."""
        content = "No checkboxes here"
        counts = count_steps(content)
        self.assertEqual(counts["total"], 0)


class TestFormatTimeAgo(unittest.TestCase):
    """Test time formatting."""

    def test_just_now(self):
        """Format recent time as 'just now'."""
        dt = datetime.now() - timedelta(seconds=30)
        self.assertEqual(format_time_ago(dt), "just now")

    def test_minutes(self):
        """Format minutes correctly."""
        dt = datetime.now() - timedelta(minutes=5)
        self.assertIn("5 minutes ago", format_time_ago(dt))

    def test_single_minute(self):
        """Handle singular 'minute'."""
        dt = datetime.now() - timedelta(minutes=1)
        self.assertIn("1 minute ago", format_time_ago(dt))

    def test_hours(self):
        """Format hours correctly."""
        dt = datetime.now() - timedelta(hours=3)
        self.assertIn("3 hours ago", format_time_ago(dt))

    def test_days(self):
        """Format days correctly."""
        dt = datetime.now() - timedelta(days=2)
        self.assertIn("2 days ago", format_time_ago(dt))


class TestIsRecent(unittest.TestCase):
    """Test recency checking."""

    def test_recent_plan(self):
        """Plan within max_age is recent."""
        plan_info = {
            "modified": (datetime.now() - timedelta(hours=2)).isoformat()
        }
        self.assertTrue(is_recent(plan_info, max_age_hours=24))

    def test_old_plan(self):
        """Plan older than max_age is not recent."""
        plan_info = {
            "modified": (datetime.now() - timedelta(hours=48)).isoformat()
        }
        self.assertFalse(is_recent(plan_info, max_age_hours=24))

    def test_missing_modified(self):
        """Handle missing modified field."""
        plan_info = {}
        self.assertFalse(is_recent(plan_info, max_age_hours=24))


if __name__ == "__main__":
    unittest.main()
