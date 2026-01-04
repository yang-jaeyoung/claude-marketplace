#!/usr/bin/env python3
"""
Unit tests for prune_context.py

Tests the context pruning analysis functions.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "skills" / "context-manager" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from prune_context import (
    is_referenced_in_plan,
    calculate_staleness,
    analyze_files,
)


class TestIsReferencedInPlan(unittest.TestCase):
    """Test plan reference checking."""

    def test_direct_path_reference(self):
        """Detect direct path references."""
        plan = "Edit `src/auth/jwt.ts` to add token validation"
        self.assertTrue(is_referenced_in_plan("src/auth/jwt.ts", plan))

    def test_filename_reference(self):
        """Detect filename-only references."""
        plan = "Modify jwt.ts for the new feature"
        self.assertTrue(is_referenced_in_plan("src/auth/jwt.ts", plan))

    def test_no_reference(self):
        """Return False when file not mentioned."""
        plan = "Work on the database module"
        self.assertFalse(is_referenced_in_plan("src/auth/jwt.ts", plan))

    def test_empty_plan(self):
        """Handle empty plan content."""
        self.assertFalse(is_referenced_in_plan("file.ts", ""))

    def test_none_plan(self):
        """Handle None plan content."""
        self.assertFalse(is_referenced_in_plan("file.ts", None))


class TestCalculateStaleness(unittest.TestCase):
    """Test staleness calculation."""

    def test_recent_file(self):
        """Calculate staleness for recent file."""
        now = datetime.now()
        file_info = {
            "last_accessed": (now - timedelta(hours=2)).isoformat()
        }
        staleness = calculate_staleness(file_info, now)
        self.assertEqual(staleness, 2)

    def test_old_file(self):
        """Calculate staleness for old file."""
        now = datetime.now()
        file_info = {
            "last_accessed": (now - timedelta(hours=48)).isoformat()
        }
        staleness = calculate_staleness(file_info, now)
        self.assertEqual(staleness, 48)

    def test_uses_added_if_no_last_accessed(self):
        """Fall back to 'added' timestamp."""
        now = datetime.now()
        file_info = {
            "added": (now - timedelta(hours=10)).isoformat()
        }
        staleness = calculate_staleness(file_info, now)
        self.assertEqual(staleness, 10)

    def test_no_timestamp(self):
        """Return 0 when no timestamp available."""
        file_info = {"path": "file.ts"}
        staleness = calculate_staleness(file_info, datetime.now())
        self.assertEqual(staleness, 0)

    def test_invalid_timestamp(self):
        """Handle invalid timestamp format."""
        file_info = {"last_accessed": "not-a-date"}
        staleness = calculate_staleness(file_info, datetime.now())
        self.assertEqual(staleness, 0)


class TestAnalyzeFiles(unittest.TestCase):
    """Test file analysis and categorization."""

    def create_manifest(self, files):
        """Helper to create manifest with file info."""
        return {
            "files": {
                "active": files
            }
        }

    def test_keep_referenced_files(self):
        """Keep files referenced in plan."""
        now = datetime.now()
        manifest = self.create_manifest([{
            "path": "src/auth/jwt.ts",
            "last_accessed": (now - timedelta(hours=100)).isoformat()
        }])
        plan = "Edit src/auth/jwt.ts for auth"

        results = analyze_files(manifest, plan, threshold_hours=5)

        self.assertEqual(len(results["keep"]), 1)
        self.assertEqual(len(results["prune"]), 0)
        self.assertIn("referenced in task plan", results["keep"][0]["recommendation"])

    def test_prune_stale_unreferenced(self):
        """Prune stale files not in plan."""
        now = datetime.now()
        manifest = self.create_manifest([{
            "path": "src/old/deprecated.ts",
            "last_accessed": (now - timedelta(hours=100)).isoformat()
        }])
        plan = "Work on new features"

        results = analyze_files(manifest, plan, threshold_hours=5)

        self.assertEqual(len(results["prune"]), 1)
        self.assertIn("Prune", results["prune"][0]["recommendation"])

    def test_pack_moderately_stale(self):
        """Suggest packing for moderately stale files."""
        now = datetime.now()
        # threshold=10, so half is 5. File at 6 hours should be pack candidate
        manifest = self.create_manifest([{
            "path": "src/utils/helpers.ts",
            "last_accessed": (now - timedelta(hours=6)).isoformat()
        }])
        plan = "Different work"

        results = analyze_files(manifest, plan, threshold_hours=10)

        self.assertEqual(len(results["pack"]), 1)
        self.assertIn("Pack", results["pack"][0]["recommendation"])

    def test_keep_recent_files(self):
        """Keep recently accessed files."""
        now = datetime.now()
        manifest = self.create_manifest([{
            "path": "src/current/active.ts",
            "last_accessed": (now - timedelta(hours=1)).isoformat()
        }])
        plan = ""

        results = analyze_files(manifest, plan, threshold_hours=10)

        self.assertEqual(len(results["keep"]), 1)
        self.assertIn("recently accessed", results["keep"][0]["recommendation"])

    def test_multiple_files_categorization(self):
        """Correctly categorize multiple files."""
        now = datetime.now()
        manifest = self.create_manifest([
            {
                "path": "src/keep-in-plan.ts",
                "last_accessed": (now - timedelta(hours=100)).isoformat()
            },
            {
                "path": "src/keep-recent.ts",
                "last_accessed": (now - timedelta(hours=1)).isoformat()
            },
            {
                "path": "src/prune-old.ts",
                "last_accessed": (now - timedelta(hours=100)).isoformat()
            },
        ])
        plan = "Work on src/keep-in-plan.ts"

        results = analyze_files(manifest, plan, threshold_hours=5)

        # One kept (in plan), one kept (recent), one pruned
        self.assertEqual(len(results["keep"]), 2)
        self.assertEqual(len(results["prune"]), 1)

        pruned_paths = [f["path"] for f in results["prune"]]
        self.assertIn("src/prune-old.ts", pruned_paths)


class TestAnalyzeFilesEdgeCases(unittest.TestCase):
    """Test edge cases in file analysis."""

    def test_empty_manifest(self):
        """Handle empty manifest."""
        manifest = {"files": {"active": []}}
        results = analyze_files(manifest, "", threshold_hours=5)

        self.assertEqual(len(results["keep"]), 0)
        self.assertEqual(len(results["prune"]), 0)
        self.assertEqual(len(results["pack"]), 0)

    def test_missing_files_key(self):
        """Handle manifest without files key."""
        manifest = {}
        results = analyze_files(manifest, "", threshold_hours=5)

        self.assertEqual(len(results["keep"]), 0)

    def test_missing_active_key(self):
        """Handle manifest without active files."""
        manifest = {"files": {}}
        results = analyze_files(manifest, "", threshold_hours=5)

        self.assertEqual(len(results["keep"]), 0)


if __name__ == "__main__":
    unittest.main()
