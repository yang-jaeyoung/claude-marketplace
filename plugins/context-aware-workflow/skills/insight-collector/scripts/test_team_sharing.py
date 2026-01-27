#!/usr/bin/env python3
"""
Unit tests for team sharing features in instinct-cli.py
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import functions to test
try:
    from instinct_cli import (
        detect_conflicts,
        resolve_conflict,
        generate_merge_report,
        generate_diff_report,
    )
except ImportError:
    # Try loading directly from the file
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "instinct_cli",
        Path(__file__).parent / "instinct-cli.py"
    )
    instinct_cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instinct_cli)

    detect_conflicts = instinct_cli.detect_conflicts
    resolve_conflict = instinct_cli.resolve_conflict
    generate_merge_report = instinct_cli.generate_merge_report
    generate_diff_report = instinct_cli.generate_diff_report


class TestTeamSharing(unittest.TestCase):
    """Test team collaboration features."""

    def setUp(self):
        """Set up test fixtures."""
        self.local_instincts = [
            {
                'id': 'instinct-1',
                'trigger': 'when performing Read',
                'confidence': 0.85,
                'evidence_count': 12,
                'domain': 'workflow',
            },
            {
                'id': 'instinct-2',
                'trigger': 'when editing .ts files',
                'confidence': 0.72,
                'evidence_count': 8,
                'domain': 'user-correction',
            },
            {
                'id': 'instinct-3',
                'trigger': 'when performing Grep',
                'confidence': 0.60,
                'evidence_count': 5,
                'domain': 'preference',
            },
        ]

        self.remote_instincts = [
            {
                'id': 'instinct-1',  # Same ID, different confidence
                'trigger': 'when performing Read',
                'confidence': 0.90,  # Higher
                'evidence_count': 15,
                'domain': 'workflow',
            },
            {
                'id': 'instinct-2',  # Same ID, lower confidence
                'trigger': 'when editing .ts files',
                'confidence': 0.68,  # Lower
                'evidence_count': 7,
                'domain': 'user-correction',
            },
            {
                'id': 'instinct-4',  # New instinct
                'trigger': 'when using Write',
                'confidence': 0.75,
                'evidence_count': 10,
                'domain': 'preference',
            },
        ]

    def test_detect_conflicts(self):
        """Test conflict detection."""
        result = detect_conflicts(self.local_instincts, self.remote_instincts)

        # Check structure
        self.assertIn('only_local', result)
        self.assertIn('only_remote', result)
        self.assertIn('conflicts', result)
        self.assertIn('identical', result)

        # Check only_local (instinct-3)
        self.assertEqual(len(result['only_local']), 1)
        self.assertEqual(result['only_local'][0]['id'], 'instinct-3')

        # Check only_remote (instinct-4)
        self.assertEqual(len(result['only_remote']), 1)
        self.assertEqual(result['only_remote'][0]['id'], 'instinct-4')

        # Check conflicts (instinct-1 and instinct-2)
        self.assertEqual(len(result['conflicts']), 2)
        conflict_ids = {c['id'] for c in result['conflicts']}
        self.assertIn('instinct-1', conflict_ids)
        self.assertIn('instinct-2', conflict_ids)

        # Verify conflict details
        inst1_conflict = next(c for c in result['conflicts'] if c['id'] == 'instinct-1')
        self.assertIn('confidence', inst1_conflict['diff_fields'])
        self.assertEqual(inst1_conflict['local']['confidence'], 0.85)
        self.assertEqual(inst1_conflict['remote']['confidence'], 0.90)

    def test_resolve_conflict_keep_local(self):
        """Test resolve_conflict with keep-local strategy."""
        local = self.local_instincts[0]
        remote = self.remote_instincts[0]

        result = resolve_conflict(local, remote, 'keep-local')
        self.assertEqual(result, local)

    def test_resolve_conflict_keep_remote(self):
        """Test resolve_conflict with keep-remote strategy."""
        local = self.local_instincts[0]
        remote = self.remote_instincts[0]

        result = resolve_conflict(local, remote, 'keep-remote')
        self.assertEqual(result, remote)

    def test_resolve_conflict_keep_higher(self):
        """Test resolve_conflict with keep-higher strategy."""
        # instinct-1: remote has higher confidence (0.90 > 0.85)
        local = self.local_instincts[0]
        remote = self.remote_instincts[0]

        result = resolve_conflict(local, remote, 'keep-higher')
        self.assertEqual(result, remote)

        # instinct-2: local has higher confidence (0.72 > 0.68)
        local2 = self.local_instincts[1]
        remote2 = self.remote_instincts[1]

        result2 = resolve_conflict(local2, remote2, 'keep-higher')
        self.assertEqual(result2, local2)

    def test_generate_diff_report(self):
        """Test diff report generation."""
        conflicts_data = detect_conflicts(self.local_instincts, self.remote_instincts)
        report = generate_diff_report(conflicts_data, summary_only=False)

        # Check report contains expected sections
        self.assertIn('INSTINCT DIFF', report)
        self.assertIn('Only in LOCAL', report)
        self.assertIn('Only in REMOTE', report)
        self.assertIn('CONFLICTS', report)
        self.assertIn('instinct-3', report)  # only local
        self.assertIn('instinct-4', report)  # only remote

    def test_generate_diff_report_summary(self):
        """Test diff report generation with summary mode."""
        conflicts_data = detect_conflicts(self.local_instincts, self.remote_instincts)
        report = generate_diff_report(conflicts_data, summary_only=True)

        # Check report is summary (no detailed IDs)
        self.assertIn('Only in LOCAL (1):', report)
        self.assertIn('Only in REMOTE (1):', report)
        self.assertNotIn('instinct-3', report)  # IDs should not appear in summary

    def test_generate_merge_report(self):
        """Test merge report generation."""
        conflicts_data = detect_conflicts(self.local_instincts, self.remote_instincts)
        resolved = {
            'instinct-1': 'remote',
            'instinct-2': 'local',
        }

        report = generate_merge_report(conflicts_data, resolved, 'keep-higher')

        # Check report contains expected sections
        self.assertIn('MERGE REPORT', report)
        self.assertIn('Strategy: keep-higher', report)
        self.assertIn('Added from remote', report)
        self.assertIn('Conflicts resolved', report)
        self.assertIn('instinct-4', report)  # added from remote

    def test_invalid_strategy(self):
        """Test that invalid strategy raises error."""
        local = self.local_instincts[0]
        remote = self.remote_instincts[0]

        with self.assertRaises(ValueError):
            resolve_conflict(local, remote, 'invalid-strategy')


if __name__ == '__main__':
    unittest.main()
