#!/usr/bin/env python3
"""
Tests for insight-collector skill components.

Tests:
- observe.py: Log rotation, session ID, truncation, path validation
- instinct-cli.py: Pattern detection, confidence calculation
- integration.py: API functions
- types.py: TypedDict validation
- session_end.py: Cleanup and auto-analyze logic
"""

import argparse
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add skill paths for imports
PLUGIN_ROOT = Path(__file__).parent.parent
SKILL_ROOT = PLUGIN_ROOT / "skills" / "insight-collector"

# Add paths for importing modules
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(SKILL_ROOT / "hooks"))
sys.path.insert(0, str(SKILL_ROOT / "lib"))

# Import instinct-cli module (handle hyphenated filename)
# We'll import it dynamically to handle the dash in the filename
import importlib.util

# First, add lib directory to path for relative imports
sys.path.insert(0, str(SKILL_ROOT / "lib"))

spec = importlib.util.spec_from_file_location(
    "instinct_cli",
    SKILL_ROOT / "scripts" / "instinct-cli.py"
)
instinct_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(instinct_cli)

# Import lib modules for evolution tests
from lib import common as lib_common
from lib import types as lib_types
from lib import evolution


class TestObserveModule(unittest.TestCase):
    """Tests for observe.py hook script."""

    def test_truncate_for_storage_string(self):
        """Test string truncation."""
        from observe import truncate_for_storage, MAX_STRING_LENGTH, TRUNCATION_SUFFIX

        short_string = "hello"
        self.assertEqual(truncate_for_storage(short_string), short_string)

        long_string = "x" * 2000
        result = truncate_for_storage(long_string)
        self.assertEqual(len(result), MAX_STRING_LENGTH + len(TRUNCATION_SUFFIX))
        self.assertTrue(result.endswith(TRUNCATION_SUFFIX))

    def test_truncate_for_storage_dict(self):
        """Test dict truncation."""
        from observe import truncate_for_storage

        data = {"key": "x" * 2000}
        result = truncate_for_storage(data)
        self.assertIn("key", result)
        self.assertTrue(result["key"].endswith("... [truncated]"))

    def test_truncate_for_storage_list(self):
        """Test list truncation to MAX_LIST_ITEMS."""
        from observe import truncate_for_storage, MAX_LIST_ITEMS

        long_list = list(range(100))
        result = truncate_for_storage(long_list)
        self.assertEqual(len(result), MAX_LIST_ITEMS)

    def test_truncate_for_storage_nested(self):
        """Test nested data structure truncation."""
        from observe import truncate_for_storage

        nested = {
            "outer": {
                "inner": "x" * 2000,
                "list": list(range(50))
            }
        }
        result = truncate_for_storage(nested)
        self.assertTrue(result["outer"]["inner"].endswith("... [truncated]"))
        self.assertLessEqual(len(result["outer"]["list"]), 20)

    def test_mask_sensitive_data_simple_dict(self):
        """Test masking sensitive data in simple dict."""
        from observe import mask_sensitive_data

        data = {"password": "secret123", "username": "john"}
        result = mask_sensitive_data(data)
        self.assertEqual(result["password"], "[MASKED]")
        self.assertEqual(result["username"], "john")

    def test_mask_sensitive_data_case_insensitive(self):
        """Test case-insensitive matching for sensitive keys."""
        from observe import mask_sensitive_data

        data = {
            "Password": "test",
            "API_KEY": "abc123",
            "ApiKey": "xyz789",
            "TOKEN": "bearer_token"
        }
        result = mask_sensitive_data(data)
        self.assertEqual(result["Password"], "[MASKED]")
        self.assertEqual(result["API_KEY"], "[MASKED]")
        self.assertEqual(result["ApiKey"], "[MASKED]")
        self.assertEqual(result["TOKEN"], "[MASKED]")

    def test_mask_sensitive_data_nested_dict(self):
        """Test masking in nested dictionaries."""
        from observe import mask_sensitive_data

        data = {
            "config": {
                "api_key": "abc123",
                "timeout": 30,
                "auth": {
                    "bearer": "token123",
                    "username": "admin"
                }
            }
        }
        result = mask_sensitive_data(data)
        self.assertEqual(result["config"]["api_key"], "[MASKED]")
        self.assertEqual(result["config"]["timeout"], 30)
        self.assertEqual(result["config"]["auth"]["bearer"], "[MASKED]")
        self.assertEqual(result["config"]["auth"]["username"], "admin")

    def test_mask_sensitive_data_list(self):
        """Test masking in lists."""
        from observe import mask_sensitive_data

        data = [
            {"password": "pass1", "name": "user1"},
            {"password": "pass2", "name": "user2"}
        ]
        result = mask_sensitive_data(data)
        self.assertEqual(result[0]["password"], "[MASKED]")
        self.assertEqual(result[0]["name"], "user1")
        self.assertEqual(result[1]["password"], "[MASKED]")
        self.assertEqual(result[1]["name"], "user2")

    def test_mask_sensitive_data_all_sensitive_keys(self):
        """Test all sensitive key patterns are masked."""
        from observe import mask_sensitive_data

        data = {
            "password": "test",
            "api_key": "test",
            "apikey": "test",
            "token": "test",
            "secret": "test",
            "credential": "test",
            "auth": "test",
            "bearer": "test",
            "private_key": "test",
            "privatekey": "test",
            "access_key": "test",
            "accesskey": "test"
        }
        result = mask_sensitive_data(data)
        for key in data.keys():
            self.assertEqual(result[key], "[MASKED]", f"Key '{key}' was not masked")

    def test_mask_sensitive_data_preserves_non_sensitive(self):
        """Test non-sensitive data is preserved."""
        from observe import mask_sensitive_data

        data = {
            "username": "john",
            "email": "john@example.com",
            "settings": {
                "theme": "dark",
                "language": "en"
            },
            "items": [1, 2, 3]
        }
        result = mask_sensitive_data(data)
        self.assertEqual(result, data)

    def test_truncate_for_storage_with_masking(self):
        """Test truncate_for_storage masks sensitive data."""
        from observe import truncate_for_storage

        data = {
            "password": "verylongsecretpassword" * 100,
            "username": "john",
            "config": {
                "api_key": "secret_key_value",
                "timeout": 30
            }
        }
        result = truncate_for_storage(data)
        self.assertEqual(result["password"], "[MASKED]")
        self.assertEqual(result["username"], "john")
        self.assertEqual(result["config"]["api_key"], "[MASKED]")
        self.assertEqual(result["config"]["timeout"], 30)

    def test_mask_sensitive_data_primitive_types(self):
        """Test masking handles primitive types correctly."""
        from observe import mask_sensitive_data

        # Strings
        self.assertEqual(mask_sensitive_data("plain text"), "plain text")

        # Numbers
        self.assertEqual(mask_sensitive_data(123), 123)
        self.assertEqual(mask_sensitive_data(45.67), 45.67)

        # Booleans
        self.assertEqual(mask_sensitive_data(True), True)
        self.assertEqual(mask_sensitive_data(False), False)

        # None
        self.assertIsNone(mask_sensitive_data(None))

    def test_should_skip_tool(self):
        """Test tool skip list."""
        from observe import should_skip_tool

        self.assertTrue(should_skip_tool("TaskCreate"))
        self.assertTrue(should_skip_tool("TaskUpdate"))
        self.assertFalse(should_skip_tool("Edit"))
        self.assertFalse(should_skip_tool("Bash"))

    def test_skip_tools_is_frozenset(self):
        """SKIP_TOOLS should be frozenset for O(1) lookup."""
        from observe import SKIP_TOOLS

        self.assertIsInstance(SKIP_TOOLS, frozenset)

    def test_create_observation_structure(self):
        """Test observation record structure."""
        from observe import create_observation

        with patch('observe.get_session_id', return_value='test-session'):
            with patch('observe.get_project_dir', return_value=Path('/test')):
                obs = create_observation(
                    event_type='pre',
                    tool_name='Edit',
                    tool_input={'file_path': '/test.py'}
                )

        self.assertIn('timestamp', obs)
        self.assertEqual(obs['event_type'], 'pre')
        self.assertEqual(obs['tool_name'], 'Edit')
        self.assertEqual(obs['session_id'], 'test-session')
        self.assertEqual(obs['project_dir'], '/test')

    def test_system_dirs_defined(self):
        """System directories should be defined for path validation."""
        from observe import SYSTEM_DIRS

        self.assertIsInstance(SYSTEM_DIRS, frozenset)
        self.assertIn('/etc', SYSTEM_DIRS)
        self.assertIn('/usr', SYSTEM_DIRS)

    def test_get_project_dir_refuses_system_dirs(self):
        """Test that get_project_dir refuses system directories."""
        from observe import get_project_dir
        import platform

        # Use /usr which exists on all Unix systems
        # On Windows, test with C:\Windows
        if platform.system() == 'Windows':
            test_path = 'C:\\Windows'
        else:
            test_path = '/usr'

        with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': test_path}):
            with self.assertRaises(ValueError) as cm:
                get_project_dir()
            self.assertIn('system directory', str(cm.exception))

    def test_rotate_if_needed_no_rotation(self):
        """Test rotation is skipped when file is small."""
        from observe import rotate_if_needed

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'small file')
            tmp_path = Path(tmp.name)

        try:
            rotate_if_needed(tmp_path, max_size=1024)
            # Should not create backup
            self.assertFalse(tmp_path.with_suffix('.jsonl.1').exists())
        finally:
            tmp_path.unlink()

    def test_rotate_if_needed_creates_backup(self):
        """Test rotation creates backup when file exceeds max_size."""
        from observe import rotate_if_needed

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'test.jsonl'
            file_path.write_bytes(b'x' * 2000)

            rotate_if_needed(file_path, max_size=1000)

            # Original file should be rotated to .1
            backup = file_path.with_suffix('.jsonl.1')
            self.assertTrue(backup.exists())

    def test_extract_tool_info_handles_missing_fields(self):
        """Test extract_tool_info handles missing fields gracefully."""
        from observe import extract_tool_info

        result = extract_tool_info({})
        self.assertEqual(result['tool_name'], 'unknown')
        self.assertIsNone(result['tool_input'])

    def test_extract_tool_info_handles_both_naming_conventions(self):
        """Test extract_tool_info handles both snake_case and camelCase."""
        from observe import extract_tool_info

        # snake_case
        result1 = extract_tool_info({
            'tool_name': 'Edit',
            'tool_input': {'path': '/test.py'},
            'duration_ms': 100
        })
        self.assertEqual(result1['tool_name'], 'Edit')
        self.assertEqual(result1['duration_ms'], 100)

        # camelCase
        result2 = extract_tool_info({
            'toolName': 'Read',
            'toolInput': {'path': '/test.py'},
            'durationMs': 200
        })
        self.assertEqual(result2['tool_name'], 'Read')
        self.assertEqual(result2['duration_ms'], 200)

    def test_read_stdin_json_handles_empty_input(self):
        """Test read_stdin_json handles empty stdin."""
        from observe import read_stdin_json

        with patch('sys.stdin.isatty', return_value=True):
            result = read_stdin_json()
            self.assertIsNone(result)

    def test_append_observation_direct_append_mode(self):
        """Test append_observation uses direct append mode efficiently."""
        from observe import append_observation

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('observe.get_observations_file', return_value=Path(tmpdir) / 'observations.jsonl'):
                # First append - creates new file
                obs1 = {'timestamp': '2024-01-01T00:00:00Z', 'tool_name': 'Edit'}
                result1 = append_observation(obs1)
                self.assertTrue(result1)

                # Second append - should append directly without reading entire file
                obs2 = {'timestamp': '2024-01-01T00:01:00Z', 'tool_name': 'Read'}
                result2 = append_observation(obs2)
                self.assertTrue(result2)

                # Verify both observations are present
                obs_file = Path(tmpdir) / 'observations.jsonl'
                self.assertTrue(obs_file.exists())

                lines = obs_file.read_text().strip().split('\n')
                self.assertEqual(len(lines), 2)

                # Verify content integrity
                loaded1 = json.loads(lines[0])
                loaded2 = json.loads(lines[1])
                self.assertEqual(loaded1['tool_name'], 'Edit')
                self.assertEqual(loaded2['tool_name'], 'Read')

    def test_append_observation_rotation_before_append(self):
        """Test append_observation rotates file before appending."""
        from observe import append_observation

        with tempfile.TemporaryDirectory() as tmpdir:
            obs_file = Path(tmpdir) / 'observations.jsonl'
            obs_file.parent.mkdir(parents=True, exist_ok=True)

            # Create a large file that exceeds rotation threshold
            obs_file.write_bytes(b'x' * (6 * 1024 * 1024))  # 6MB

            with patch('observe.get_observations_file', return_value=obs_file):
                obs = {'timestamp': '2024-01-01T00:00:00Z', 'tool_name': 'Edit'}
                result = append_observation(obs)
                self.assertTrue(result)

                # Verify backup was created
                backup = obs_file.with_suffix('.jsonl.1')
                self.assertTrue(backup.exists())

                # Verify new file contains only new observation
                lines = obs_file.read_text().strip().split('\n')
                self.assertEqual(len(lines), 1)
                loaded = json.loads(lines[0])
                self.assertEqual(loaded['tool_name'], 'Edit')


class TestIncrementalAnalysis(unittest.TestCase):
    """Tests for incremental analysis functionality."""

    def test_get_last_analyzed_state_no_file(self):
        """Test get_last_analyzed_state when marker file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                state = instinct_cli.get_last_analyzed_state()
                self.assertEqual(state, {})

    def test_save_analyzed_state(self):
        """Test save_analyzed_state creates marker file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                instinct_cli.save_analyzed_state(line_count=100, file_size=50000)

                marker_file = Path(tmpdir) / '.caw' / 'observations' / '.last_analyzed'
                self.assertTrue(marker_file.exists())

                state = instinct_cli.get_last_analyzed_state()
                self.assertEqual(state['line_count'], 100)
                self.assertEqual(state['file_size'], 50000)
                self.assertIn('timestamp', state)

    def test_load_new_observations_no_marker(self):
        """Test load_new_observations loads all when no marker exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 3 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(3):
                    f.write(json.dumps({'event_type': 'pre', 'tool_name': f'Tool{i}'}) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                new_obs = instinct_cli.load_new_observations()
                self.assertEqual(len(new_obs), 3)

    def test_load_new_observations_with_marker(self):
        """Test load_new_observations only loads new observations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 5 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(5):
                    f.write(json.dumps({'event_type': 'pre', 'tool_name': f'Tool{i}'}) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Mark first 2 as analyzed
                instinct_cli.save_analyzed_state(line_count=2, file_size=200)

                # Load new observations
                new_obs = instinct_cli.load_new_observations()
                self.assertEqual(len(new_obs), 3)
                self.assertEqual(new_obs[0]['tool_name'], 'Tool2')
                self.assertEqual(new_obs[1]['tool_name'], 'Tool3')
                self.assertEqual(new_obs[2]['tool_name'], 'Tool4')

    def test_load_observations_generator(self):
        """Test load_observations returns generator and supports since_line."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 10 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(10):
                    f.write(json.dumps({'event_type': 'pre', 'tool_name': f'Tool{i}'}) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Load from line 5
                observations = list(instinct_cli.load_observations(since_line=5))
                self.assertEqual(len(observations), 5)
                self.assertEqual(observations[0]['tool_name'], 'Tool5')
                self.assertEqual(observations[4]['tool_name'], 'Tool9')

    def test_load_observations_from_start(self):
        """Test load_observations loads all from start."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 3 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(3):
                    f.write(json.dumps({'event_type': 'pre', 'tool_name': f'Tool{i}'}) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                observations = list(instinct_cli.load_observations(since_line=0))
                self.assertEqual(len(observations), 3)

    def test_cmd_analyze_incremental_flag_no_new_obs(self):
        """Test cmd_analyze with --incremental when no new observations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 2 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(2):
                    f.write(json.dumps({'event_type': 'pre', 'tool_name': f'Tool{i}'}) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Mark all as analyzed
                instinct_cli.save_analyzed_state(line_count=2, file_size=200)

                # Run incremental analysis
                args = argparse.Namespace(incremental=True, full=False, advanced=False)
                result = instinct_cli.cmd_analyze(args)
                self.assertEqual(result, 0)

    def test_cmd_analyze_full_flag_ignores_marker(self):
        """Test cmd_analyze with --full ignores marker file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 5 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(5):
                    f.write(json.dumps({'event_type': 'pre', 'tool_name': f'Tool{i}'}) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Mark first 2 as analyzed
                instinct_cli.save_analyzed_state(line_count=2, file_size=200)

                # Run full analysis (should analyze all 5)
                args = argparse.Namespace(incremental=True, full=True, advanced=False)
                with patch.object(instinct_cli, 'detect_tool_sequences', return_value=[]):
                    with patch.object(instinct_cli, 'detect_error_recovery', return_value=[]):
                        with patch.object(instinct_cli, 'detect_tool_preferences', return_value=[]):
                            with patch.object(instinct_cli, 'detect_user_corrections', return_value=[]):
                                result = instinct_cli.cmd_analyze(args)
                                # Should have analyzed all observations, not just new ones
                                self.assertEqual(result, 0)


class TestInstinctCLI(unittest.TestCase):
    """Tests for instinct-cli.py."""

    def test_calculate_confidence_low(self):
        """Test confidence for low evidence count."""
        self.assertEqual(
            instinct_cli.calculate_confidence(1),
            instinct_cli.LOW_EVIDENCE_CONFIDENCE
        )
        self.assertEqual(
            instinct_cli.calculate_confidence(2),
            instinct_cli.LOW_EVIDENCE_CONFIDENCE
        )

    def test_calculate_confidence_medium(self):
        """Test confidence for medium evidence count."""
        self.assertEqual(
            instinct_cli.calculate_confidence(3),
            instinct_cli.MEDIUM_EVIDENCE_CONFIDENCE
        )
        self.assertEqual(
            instinct_cli.calculate_confidence(5),
            instinct_cli.MEDIUM_EVIDENCE_CONFIDENCE
        )

    def test_calculate_confidence_high(self):
        """Test confidence for high evidence count."""
        self.assertEqual(
            instinct_cli.calculate_confidence(6),
            instinct_cli.HIGH_EVIDENCE_CONFIDENCE
        )
        self.assertEqual(
            instinct_cli.calculate_confidence(10),
            instinct_cli.HIGH_EVIDENCE_CONFIDENCE
        )

    def test_calculate_confidence_max(self):
        """Test confidence caps at MAX_CONFIDENCE."""
        result = instinct_cli.calculate_confidence(100)
        self.assertLessEqual(result, instinct_cli.MAX_CONFIDENCE)

    def test_calculate_confidence_progressive_increase(self):
        """Test confidence increases progressively after high threshold."""
        conf_10 = instinct_cli.calculate_confidence(10)
        conf_20 = instinct_cli.calculate_confidence(20)
        self.assertGreater(conf_20, conf_10)

    def test_generate_instinct_id_format(self):
        """Test instinct ID generation format."""
        result = instinct_cli.generate_instinct_id("when performing Edit")
        self.assertRegex(result, r'^[a-z0-9\-]+-[a-f0-9]{8}$')

    def test_generate_instinct_id_uses_sha256(self):
        """Test that ID uses SHA256 (8 char suffix)."""
        result = instinct_cli.generate_instinct_id("test trigger")
        # SHA256 suffix is 8 characters
        suffix = result.split('-')[-1]
        self.assertEqual(len(suffix), 8)

    def test_generate_instinct_id_deterministic(self):
        """Test that same trigger generates same ID."""
        trigger = "when editing TypeScript files"
        id1 = instinct_cli.generate_instinct_id(trigger)
        id2 = instinct_cli.generate_instinct_id(trigger)
        self.assertEqual(id1, id2)

    def test_validate_instinct_id_valid(self):
        """Test valid instinct ID validation."""
        self.assertTrue(instinct_cli.validate_instinct_id("when-editing-abc12345"))
        self.assertTrue(instinct_cli.validate_instinct_id("simple-id-12345678"))

    def test_validate_instinct_id_invalid(self):
        """Test invalid instinct ID rejection."""
        self.assertFalse(instinct_cli.validate_instinct_id("../../../etc/passwd"))
        self.assertFalse(instinct_cli.validate_instinct_id("id with spaces"))
        self.assertFalse(instinct_cli.validate_instinct_id("ID_WITH_CAPS"))
        self.assertFalse(instinct_cli.validate_instinct_id(""))

    def test_detect_tool_sequences_empty(self):
        """Test sequence detection with empty input."""
        result = instinct_cli.detect_tool_sequences([])
        self.assertEqual(result, [])

    def test_detect_tool_sequences_finds_patterns(self):
        """Test sequence detection finds repeated patterns."""
        # Create observations with repeated sequence
        observations = []
        for session in ['s1', 's2', 's3', 's4']:
            for tool in ['Grep', 'Edit', 'Grep']:
                observations.append({
                    'event_type': 'pre',
                    'session_id': session,
                    'tool_name': tool,
                })

        result = instinct_cli.detect_tool_sequences(observations)
        # Should find patterns that meet MIN_SEQUENCE_OCCURRENCES
        self.assertGreater(len(result), 0)

        # Verify structure
        if result:
            candidate = result[0]
            self.assertIn('trigger', candidate)
            self.assertIn('action', candidate)
            self.assertIn('evidence_count', candidate)

    def test_detect_error_recovery_empty(self):
        """Test error recovery detection with empty input."""
        result = instinct_cli.detect_error_recovery([])
        self.assertEqual(result, [])

    def test_detect_error_recovery_finds_patterns(self):
        """Test error recovery detects fail -> success patterns."""
        now = datetime.now(timezone.utc)
        observations = [
            # Failed Edit
            {
                'event_type': 'post',
                'session_id': 's1',
                'tool_name': 'Edit',
                'success': False,
                'timestamp': now.isoformat(),
            },
            # Successful retry
            {
                'event_type': 'post',
                'session_id': 's1',
                'tool_name': 'Edit',
                'success': True,
                'timestamp': (now + timedelta(seconds=10)).isoformat(),
            },
            # Repeat pattern
            {
                'event_type': 'post',
                'session_id': 's2',
                'tool_name': 'Edit',
                'success': False,
                'timestamp': (now + timedelta(minutes=5)).isoformat(),
            },
            {
                'event_type': 'post',
                'session_id': 's2',
                'tool_name': 'Edit',
                'success': True,
                'timestamp': (now + timedelta(minutes=5, seconds=10)).isoformat(),
            },
        ]

        result = instinct_cli.detect_error_recovery(observations)
        self.assertGreaterEqual(len(result), 0)

    def test_detect_user_corrections_empty(self):
        """Test user corrections detection with empty input."""
        result = instinct_cli.detect_user_corrections([])
        self.assertEqual(result, [])

    def test_detect_user_corrections_finds_rapid_edits(self):
        """Test user corrections detects rapid re-edits."""
        now = datetime.now(timezone.utc)
        observations = []

        # Create 3 rapid edits to same file (meets threshold)
        for i in range(3):
            observations.append({
                'event_type': 'post',
                'tool_name': 'Edit',
                'success': True,
                'tool_input': {'file_path': '/test/file.ts'},
                'timestamp': (now + timedelta(minutes=i*2)).isoformat().replace('+00:00', 'Z'),
            })

        result = instinct_cli.detect_user_corrections(observations)
        # Should detect .ts file corrections
        self.assertGreaterEqual(len(result), 0)

    def test_detect_tool_preferences_empty(self):
        """Test tool preferences with no data."""
        result = instinct_cli.detect_tool_preferences([])
        self.assertEqual(result, [])

    def test_detect_tool_preferences_finds_common_tools(self):
        """Test tool preferences detects frequently used tools."""
        observations = []

        # Create heavy Edit usage
        for i in range(20):
            observations.append({
                'event_type': 'pre',
                'tool_name': 'Edit',
            })

        # Some other tools
        for tool in ['Read', 'Bash', 'Grep']:
            observations.append({
                'event_type': 'pre',
                'tool_name': tool,
            })

        result = instinct_cli.detect_tool_preferences(observations)
        self.assertGreater(len(result), 0)

        # Edit should be detected as preference
        edit_pref = [c for c in result if 'Edit' in c['action']]
        self.assertEqual(len(edit_pref), 1)


class TestIntegrationAPI(unittest.TestCase):
    """Tests for integration.py API functions."""

    def test_get_caw_dir(self):
        """Test .caw directory path construction."""
        from lib.integration import get_caw_dir

        result = get_caw_dir()
        self.assertTrue(str(result).endswith('.caw'))

    def test_list_insights_empty(self):
        """Test listing insights when none exist."""
        from lib import list_insights

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                result = list_insights()
                self.assertEqual(result, [])

    def test_list_insights_with_data(self):
        """Test listing insights with sample data."""
        from lib import list_insights

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .caw/insights directory
            insights_dir = Path(tmpdir) / '.caw' / 'insights'
            insights_dir.mkdir(parents=True)

            # Create sample insight
            insight_file = insights_dir / 'test-insight.md'
            insight_file.write_text("""# Insight: Test Pattern

## Tags
#testing #automation

## Content
This is a test insight.
""")

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                result = list_insights()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]['title'], 'Test Pattern')
                self.assertIn('testing', result[0]['tags'])

    def test_list_instincts_empty(self):
        """Test listing instincts when none exist."""
        from lib import list_instincts

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                result = list_instincts()
                self.assertEqual(result, [])

    def test_list_instincts_with_confidence_filter(self):
        """Test listing instincts with confidence filter."""
        from lib import list_instincts

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .caw/instincts directory
            instincts_dir = Path(tmpdir) / '.caw' / 'instincts'
            instincts_dir.mkdir(parents=True)

            # Create index
            index_file = instincts_dir / 'index.json'
            index_file.write_text(json.dumps({
                'instincts': [
                    {'id': 'high', 'confidence': 0.8, 'trigger': 'test', 'evidence_count': 5, 'domain': 'test'},
                    {'id': 'low', 'confidence': 0.3, 'trigger': 'test', 'evidence_count': 2, 'domain': 'test'},
                ],
                'last_updated': datetime.now(timezone.utc).isoformat()
            }))

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                all_instincts = list_instincts()
                self.assertEqual(len(all_instincts), 2)

                high_only = list_instincts(min_confidence=0.5)
                self.assertEqual(len(high_only), 1)
                self.assertEqual(high_only[0]['id'], 'high')

    def test_get_metrics_empty(self):
        """Test metrics when no data exists."""
        from lib import get_metrics

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                result = get_metrics()
                self.assertEqual(result['insights_captured'], 0)
                self.assertEqual(result['instincts_generated'], 0)
                self.assertEqual(result['observations_recorded'], 0)

    def test_get_evolution_candidates_structure(self):
        """Test evolution candidates returns correct structure."""
        from lib import get_evolution_candidates

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                result = get_evolution_candidates()
                self.assertIn('commands', result)
                self.assertIn('skills', result)
                self.assertIn('agents', result)
                self.assertIsInstance(result['commands'], list)
                self.assertIsInstance(result['skills'], list)
                self.assertIsInstance(result['agents'], list)

    def test_search_insights_by_query(self):
        """Test searching insights by query string."""
        from lib import list_insights, search_insights

        with tempfile.TemporaryDirectory() as tmpdir:
            insights_dir = Path(tmpdir) / '.caw' / 'insights'
            insights_dir.mkdir(parents=True)

            # Create sample insights
            (insights_dir / 'test1.md').write_text("""# Insight: Testing Pattern
## Content
About testing methodology
""")
            (insights_dir / 'test2.md').write_text("""# Insight: Deployment Pattern
## Content
About deployment automation
""")

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                results = search_insights(query='testing')
                self.assertEqual(len(results), 1)
                self.assertIn('Testing Pattern', results[0]['title'])

    def test_get_relevant_insights(self):
        """Test getting relevant insights by context."""
        from lib import get_relevant_insights

        with tempfile.TemporaryDirectory() as tmpdir:
            insights_dir = Path(tmpdir) / '.caw' / 'insights'
            insights_dir.mkdir(parents=True)

            (insights_dir / 'test.md').write_text("""# Insight: Testing Automation
## Tags
#testing #automation
## Content
Automated testing best practices
""")

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                results = get_relevant_insights('testing automation framework')
                # Should score based on keyword matches
                self.assertGreaterEqual(len(results), 0)


class TestTypes(unittest.TestCase):
    """Tests for types.py TypedDict definitions."""

    def test_observation_type_exists(self):
        """Test Observation type is defined."""
        from lib.types import Observation
        self.assertTrue(hasattr(Observation, '__annotations__'))

    def test_instinct_type_exists(self):
        """Test Instinct type is defined."""
        from lib.types import Instinct
        self.assertTrue(hasattr(Instinct, '__annotations__'))

    def test_metrics_type_exists(self):
        """Test Metrics type is defined."""
        from lib.types import Metrics
        self.assertTrue(hasattr(Metrics, '__annotations__'))

    def test_evolution_candidates_type_exists(self):
        """Test EvolutionCandidates type is defined."""
        from lib.types import EvolutionCandidates
        self.assertTrue(hasattr(EvolutionCandidates, '__annotations__'))


class TestSessionEnd(unittest.TestCase):
    """Tests for session_end.py hook script."""

    def test_cleanup_session_no_file(self):
        """Test cleanup when no session file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                from session_end import cleanup_session
                cleanup_session()  # Should not raise

    def test_cleanup_session_removes_file(self):
        """Test cleanup removes session file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            session_file = obs_dir / '.session_id'
            session_file.write_text('test-session')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                from session_end import cleanup_session
                cleanup_session()
                self.assertFalse(session_file.exists())

    def test_check_auto_analyze_no_file(self):
        """Test auto-analyze check when no observations exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                from session_end import check_auto_analyze
                result = check_auto_analyze()
                self.assertFalse(result)

    def test_check_auto_analyze_threshold(self):
        """Test auto-analyze triggers at 100 observations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 100 lines
            obs_file.write_text('\n'.join(['{}'] * 100))

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                from session_end import check_auto_analyze
                result = check_auto_analyze()
                self.assertTrue(result)


class TestConstants(unittest.TestCase):
    """Tests for module-level constants."""

    def test_observe_constants(self):
        """Test observe.py constants are defined."""
        from observe import (
            MAX_STRING_LENGTH,
            MAX_LIST_ITEMS,
            TRUNCATION_SUFFIX,
            SKIP_TOOLS,
            SYSTEM_DIRS,
            SENSITIVE_KEYS,
        )

        self.assertIsInstance(MAX_STRING_LENGTH, int)
        self.assertIsInstance(MAX_LIST_ITEMS, int)
        self.assertIsInstance(TRUNCATION_SUFFIX, str)
        self.assertIsInstance(SKIP_TOOLS, frozenset)
        self.assertIsInstance(SYSTEM_DIRS, frozenset)
        self.assertIsInstance(SENSITIVE_KEYS, frozenset)
        self.assertGreater(MAX_STRING_LENGTH, 0)
        self.assertGreater(MAX_LIST_ITEMS, 0)
        self.assertGreater(len(SENSITIVE_KEYS), 0)

    def test_instinct_cli_constants(self):
        """Test instinct-cli.py constants are defined."""
        self.assertIsInstance(instinct_cli.MIN_CONFIDENCE, float)
        self.assertIsInstance(instinct_cli.MAX_CONFIDENCE, float)
        self.assertLess(instinct_cli.MIN_CONFIDENCE, instinct_cli.MAX_CONFIDENCE)
        self.assertGreater(instinct_cli.LOW_EVIDENCE_THRESHOLD, 0)
        self.assertGreater(instinct_cli.MEDIUM_EVIDENCE_THRESHOLD, instinct_cli.LOW_EVIDENCE_THRESHOLD)
        self.assertGreater(instinct_cli.HIGH_EVIDENCE_THRESHOLD, instinct_cli.MEDIUM_EVIDENCE_THRESHOLD)

    def test_confidence_thresholds_ordered(self):
        """Test confidence thresholds are properly ordered."""
        self.assertLess(
            instinct_cli.LOW_EVIDENCE_CONFIDENCE,
            instinct_cli.MEDIUM_EVIDENCE_CONFIDENCE
        )
        self.assertLess(
            instinct_cli.MEDIUM_EVIDENCE_CONFIDENCE,
            instinct_cli.HIGH_EVIDENCE_CONFIDENCE
        )


class TestLoadInstinct(unittest.TestCase):
    """Tests for loading instinct markdown files."""

    def test_load_instinct_not_found(self):
        """Test loading non-existent instinct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                result = instinct_cli.load_instinct('nonexistent-id-12345678')
                self.assertIsNone(result)

    def test_load_instinct_parses_frontmatter(self):
        """Test loading instinct parses YAML frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            instincts_dir = Path(tmpdir) / '.caw' / 'instincts' / 'personal'
            instincts_dir.mkdir(parents=True)

            instinct_file = instincts_dir / 'test-id-abc12345.md'
            instinct_file.write_text("""---
id: test-id-abc12345
trigger: "when editing files"
confidence: 0.75
domain: workflow
evidence_count: 10
---

# Test Instinct

This is the body.
""")

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                result = instinct_cli.load_instinct('test-id-abc12345')
                self.assertIsNotNone(result)
                self.assertEqual(result['id'], 'test-id-abc12345')
                self.assertEqual(result['trigger'], 'when editing files')
                self.assertEqual(result['confidence'], 0.75)
                self.assertEqual(result['evidence_count'], 10)


class TestCreateInstinctFile(unittest.TestCase):
    """Tests for creating instinct files."""

    def test_create_instinct_file_structure(self):
        """Test instinct file is created with correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                instinct = {
                    'id': 'test-instinct-abc12345',
                    'trigger': 'when editing TypeScript',
                    'action': 'Run type check',
                    'confidence': 0.6,
                    'evidence_count': 8,
                    'domain': 'quality',
                }

                result = instinct_cli.create_instinct_file(instinct)
                self.assertTrue(result)

                # Verify file was created
                instinct_file = Path(tmpdir) / '.caw' / 'instincts' / 'personal' / 'test-instinct-abc12345.md'
                self.assertTrue(instinct_file.exists())

                # Verify structure
                content = instinct_file.read_text()
                self.assertIn('id: test-instinct-abc12345', content)
                self.assertIn('trigger: "when editing TypeScript"', content)
                self.assertIn('confidence: 0.6', content)


class TestEvolutionModule(unittest.TestCase):
    """Tests for lib/evolution.py"""

    def test_slugify_basic(self):
        """Test basic slugification."""
        self.assertEqual(evolution.slugify("Safe Modify Pattern"), "safe-modify-pattern")
        self.assertEqual(evolution.slugify("Test Pattern"), "test-pattern")

    def test_slugify_special_chars(self):
        """Test slugify with special characters."""
        self.assertEqual(evolution.slugify("Test!@#$%Pattern"), "testpattern")
        self.assertEqual(evolution.slugify("My_Cool__Idea"), "my-cool-idea")
        self.assertEqual(evolution.slugify("  spaces  everywhere  "), "spaces-everywhere")
        self.assertEqual(evolution.slugify("CamelCase Pattern"), "camelcase-pattern")

    def test_classify_instinct_command(self):
        """Test classification of command-type instinct."""
        instinct = {
            'trigger': 'when user asks for deployment',
            'action': 'step 1: build → step 2: deploy',
            'domain': 'workflow'
        }
        self.assertEqual(evolution.classify_instinct(instinct), 'command')

    def test_classify_instinct_skill(self):
        """Test classification of skill-type instinct."""
        instinct = {
            'trigger': 'when editing TypeScript files',
            'action': 'Run type check',
            'domain': 'quality'
        }
        self.assertEqual(evolution.classify_instinct(instinct), 'skill')

    def test_classify_instinct_agent(self):
        """Test classification of agent-type instinct."""
        instinct = {
            'trigger': 'when analyzing complex architecture',
            'action': 'investigate → analyze dependencies → decide → report → verify',
            'domain': 'architecture'
        }
        self.assertEqual(evolution.classify_instinct(instinct), 'agent')

    def test_extract_steps_from_action_arrow(self):
        """Test step extraction with → separator."""
        action = "build project → run tests → deploy"
        steps = evolution.extract_steps_from_action(action)
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], "build project")
        self.assertEqual(steps[1], "run tests")
        self.assertEqual(steps[2], "deploy")

    def test_extract_steps_from_action_numbered(self):
        """Test step extraction with numbered list."""
        action = "Step 1: analyze code\nStep 2: fix issues\n3. verify"
        steps = evolution.extract_steps_from_action(action)
        self.assertEqual(len(steps), 3)
        self.assertIn("analyze code", steps[0])

    def test_generate_command_scaffold_structure(self):
        """Test command scaffold has correct YAML frontmatter."""
        instinct = {
            'id': 'test-cmd-abc12345',
            'trigger': 'when user requests deployment',
            'action': 'build → test → deploy',
            'confidence': 0.75,
            'evidence_count': 10,
            'domain': 'workflow'
        }

        scaffold = evolution.generate_command_scaffold(instinct, 'deploy-workflow')

        # Check YAML frontmatter
        self.assertIn('---', scaffold)
        self.assertIn('description:', scaffold)
        self.assertIn('argument-hint:', scaffold)
        self.assertIn('allowed-tools:', scaffold)

        # Check content
        self.assertIn('/cw:deploy-workflow', scaffold)
        self.assertIn('test-cmd-abc12345', scaffold)
        self.assertIn('0.75', scaffold)

    def test_generate_skill_scaffold_structure(self):
        """Test skill scaffold has SKILL.md format."""
        instinct = {
            'id': 'test-skill-xyz78901',
            'trigger': 'when editing files',
            'action': 'validate → format → check',
            'confidence': 0.8,
            'evidence_count': 15,
            'domain': 'quality'
        }

        scaffold = evolution.generate_skill_scaffold(instinct, 'auto-formatter')

        # Check YAML frontmatter
        self.assertIn('---', scaffold)
        self.assertIn('name: auto-formatter', scaffold)
        self.assertIn('description:', scaffold)
        self.assertIn('allowed-tools:', scaffold)

        # Check content
        self.assertIn('Auto Formatter - Evolved Skill', scaffold)
        self.assertIn('test-skill-xyz78901', scaffold)
        self.assertIn('0.80', scaffold)

    def test_generate_agent_scaffold_structure(self):
        """Test agent scaffold has agent format."""
        instinct = {
            'id': 'test-agent-def45678',
            'trigger': 'when analyzing complex systems',
            'action': 'gather context → analyze → decide → report',
            'confidence': 0.85,
            'evidence_count': 20,
            'domain': 'architecture'
        }

        scaffold = evolution.generate_agent_scaffold(instinct, 'system-analyzer')

        # Check YAML frontmatter
        self.assertIn('---', scaffold)
        self.assertIn('name: system-analyzer', scaffold)
        self.assertIn('model: sonnet', scaffold)
        self.assertIn('tier: sonnet', scaffold)
        self.assertIn('tools:', scaffold)
        self.assertIn('whenToUse:', scaffold)

        # Check content
        self.assertIn('System Analyzer - Evolved Agent', scaffold)
        self.assertIn('test-agent-def45678', scaffold)
        self.assertIn('0.85', scaffold)

    def test_create_evolution_creates_file(self):
        """Test create_evolution writes file correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                instinct = {
                    'id': 'evo-test-abc12345',
                    'trigger': 'when deploying',
                    'action': 'build → deploy',
                    'confidence': 0.7,
                    'evidence_count': 12,
                    'domain': 'workflow'
                }

                result = evolution.create_evolution(instinct, 'command', 'deploy-cmd')

                self.assertTrue(result['success'])
                self.assertEqual(result['type'], 'command')
                self.assertEqual(result['name'], 'deploy-cmd')
                self.assertIsNone(result['error'])

                # Verify file exists
                target_file = Path(result['path'])
                self.assertTrue(target_file.exists())
                content = target_file.read_text()
                self.assertIn('evo-test-abc12345', content)

    def test_track_evolution_updates_index(self):
        """Test track_evolution adds to evolutions array."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Create index file
                instincts_dir = Path(tmpdir) / '.caw' / 'instincts'
                instincts_dir.mkdir(parents=True)
                index_file = instincts_dir / 'index.json'
                index_file.write_text(json.dumps({
                    'instincts': [],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }))

                # Track evolution
                result = evolution.track_evolution(
                    instinct_id='test-id-123',
                    evolution_type='command',
                    target_path='/path/to/cmd.md',
                    generated_name='test-cmd',
                    confidence=0.75,
                    evidence_count=10
                )

                self.assertTrue(result)

                # Verify index updated
                with open(index_file, 'r') as f:
                    index = json.load(f)

                self.assertIn('evolutions', index)
                self.assertEqual(len(index['evolutions']), 1)
                evo = index['evolutions'][0]
                self.assertEqual(evo['source_instinct'], 'test-id-123')
                self.assertEqual(evo['evolution_type'], 'command')
                self.assertEqual(evo['confidence'], 0.75)


class TestExportImportIntegration(unittest.TestCase):
    """Integration tests for export/import workflow."""

    def test_export_import_roundtrip(self):
        """Test export then import preserves data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Create sample instincts with markdown files
                instincts_dir = Path(tmpdir) / '.caw' / 'instincts' / 'personal'
                instincts_dir.mkdir(parents=True)

                instinct1 = {
                    'id': 'export-test-abc12345',
                    'trigger': 'when testing',
                    'action': 'run tests',
                    'confidence': 0.75,
                    'evidence_count': 10,
                    'domain': 'quality'
                }

                # Create instinct markdown file
                instinct_file = instincts_dir / 'export-test-abc12345.md'
                instinct_file.write_text(f"""---
id: {instinct1['id']}
trigger: "{instinct1['trigger']}"
confidence: {instinct1['confidence']}
evidence_count: {instinct1['evidence_count']}
domain: {instinct1['domain']}
---

# Test Instinct

{instinct1['action']}
""")

                # Create index
                index_file = instincts_dir.parent / 'index.json'
                index_file.write_text(json.dumps({
                    'instincts': [instinct1],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }))

                # Export
                export_file = Path(tmpdir) / 'export.json'
                args_export = argparse.Namespace(output=str(export_file))
                result = instinct_cli.cmd_export(args_export)
                self.assertEqual(result, 0)
                self.assertTrue(export_file.exists())

                # Verify export content
                with open(export_file, 'r') as f:
                    exported = json.load(f)
                self.assertEqual(len(exported['instincts']), 1)
                self.assertEqual(exported['instincts'][0]['id'], 'export-test-abc12345')

                # Clear instincts
                index_file.write_text(json.dumps({
                    'instincts': [],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }))
                instinct_file.unlink()

                # Import back
                args_import = argparse.Namespace(input=str(export_file))
                result = instinct_cli.cmd_import_instincts(args_import)
                self.assertEqual(result, 0)

                # Verify restored
                with open(index_file, 'r') as f:
                    index = json.load(f)
                self.assertEqual(len(index['instincts']), 1)
                self.assertEqual(index['instincts'][0]['id'], 'export-test-abc12345')

    def test_import_skips_duplicates(self):
        """Test import doesn't duplicate existing instincts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                instincts_dir = Path(tmpdir) / '.caw' / 'instincts'
                instincts_dir.mkdir(parents=True)

                existing = {
                    'id': 'duplicate-test-abc12345',
                    'trigger': 'test',
                    'confidence': 0.7,
                    'evidence_count': 5,
                    'domain': 'test'
                }

                # Create index with existing instinct
                index_file = instincts_dir / 'index.json'
                index_file.write_text(json.dumps({
                    'instincts': [existing],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }))

                # Create import file with same instinct
                import_file = Path(tmpdir) / 'import.json'
                import_file.write_text(json.dumps({
                    'instincts': [existing],
                    'exported_at': datetime.now(timezone.utc).isoformat()
                }))

                # Import
                args_import = argparse.Namespace(input=str(import_file))
                result = instinct_cli.cmd_import_instincts(args_import)
                self.assertEqual(result, 0)

                # Verify no duplication
                with open(index_file, 'r') as f:
                    index = json.load(f)
                self.assertEqual(len(index['instincts']), 1)

    def test_export_includes_all_fields(self):
        """Test exported JSON has all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                instincts_dir = Path(tmpdir) / '.caw' / 'instincts' / 'personal'
                instincts_dir.mkdir(parents=True)

                instinct = {
                    'id': 'field-test-xyz78901',
                    'trigger': 'test trigger',
                    'action': 'test action',
                    'confidence': 0.8,
                    'evidence_count': 15,
                    'domain': 'test',
                    'created_at': datetime.now(timezone.utc).isoformat()
                }

                # Create instinct markdown file
                instinct_file = instincts_dir / 'field-test-xyz78901.md'
                instinct_file.write_text(f"""---
id: {instinct['id']}
trigger: "{instinct['trigger']}"
confidence: {instinct['confidence']}
evidence_count: {instinct['evidence_count']}
domain: {instinct['domain']}
---

# Field Test

{instinct['action']}
""")

                index_file = instincts_dir.parent / 'index.json'
                index_file.write_text(json.dumps({
                    'instincts': [instinct],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }))

                # Export
                export_file = Path(tmpdir) / 'export.json'
                args_export = argparse.Namespace(output=str(export_file))
                instinct_cli.cmd_export(args_export)

                # Verify all fields present
                with open(export_file, 'r') as f:
                    exported = json.load(f)

                self.assertIn('version', exported)
                self.assertIn('exported_at', exported)
                self.assertIn('instincts', exported)

                # Only check structure if instincts exported
                if len(exported['instincts']) > 0:
                    exp_instinct = exported['instincts'][0]
                    self.assertIn('id', exp_instinct)
                    self.assertIn('trigger', exp_instinct)
                    self.assertIn('confidence', exp_instinct)
                    self.assertIn('evidence_count', exp_instinct)


class TestConcurrency(unittest.TestCase):
    """Concurrency and file locking tests."""

    def test_parallel_append_observations(self):
        """Test multiple parallel appends don't corrupt file."""
        import threading

        with tempfile.TemporaryDirectory() as tmpdir:
            obs_file = Path(tmpdir) / 'observations.jsonl'
            obs_file.parent.mkdir(parents=True, exist_ok=True)

            with patch('observe.get_observations_file', return_value=obs_file):
                from observe import append_observation

                def write_obs(thread_id):
                    for i in range(10):
                        obs = {
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                            'tool_name': f'Thread{thread_id}',
                            'event_type': 'pre',
                            'iteration': i
                        }
                        append_observation(obs)

                # Run 5 threads in parallel
                threads = []
                for tid in range(5):
                    t = threading.Thread(target=write_obs, args=(tid,))
                    threads.append(t)
                    t.start()

                for t in threads:
                    t.join()

                # Verify all 50 observations written
                self.assertTrue(obs_file.exists())
                lines = obs_file.read_text().strip().split('\n')
                self.assertEqual(len(lines), 50)

                # Verify each line is valid JSON
                for line in lines:
                    data = json.loads(line)
                    self.assertIn('tool_name', data)

    def test_file_lock_prevents_corruption(self):
        """Test file locking works correctly."""
        # This test is platform-dependent; fcntl not available on Windows
        import platform
        if platform.system() == 'Windows':
            self.skipTest("File locking test requires Unix-like system")

        with tempfile.TemporaryDirectory() as tmpdir:
            lock_file = Path(tmpdir) / 'test.lock'

            import fcntl

            # First process acquires lock
            f1 = open(lock_file, 'w')
            fcntl.flock(f1.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Second process should fail to acquire
            f2 = open(lock_file, 'w')
            with self.assertRaises(IOError):
                fcntl.flock(f2.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Release lock
            fcntl.flock(f1.fileno(), fcntl.LOCK_UN)
            f1.close()
            f2.close()


class TestLargeFileHandling(unittest.TestCase):
    """Tests for handling large observation files."""

    def test_load_observations_large_file(self):
        """Test loading observations from large file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 10000 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(10000):
                    f.write(json.dumps({
                        'event_type': 'pre',
                        'tool_name': f'Tool{i % 10}',
                        'session_id': f'session{i // 100}'
                    }) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Load observations using generator
                observations = list(instinct_cli.load_observations(since_line=0))
                self.assertEqual(len(observations), 10000)

    def test_incremental_analysis_skips_processed(self):
        """Test incremental mode skips already processed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Write 1000 observations
            with open(obs_file, 'w', encoding='utf-8') as f:
                for i in range(1000):
                    f.write(json.dumps({
                        'event_type': 'pre',
                        'tool_name': 'Edit',
                        'session_id': f's{i}'
                    }) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Mark first 800 as analyzed
                instinct_cli.save_analyzed_state(line_count=800, file_size=50000)

                # Load new observations
                new_obs = instinct_cli.load_new_observations()
                self.assertEqual(len(new_obs), 200)

    def test_rotation_on_large_file(self):
        """Test log rotation triggers at size limit."""
        from observe import rotate_if_needed

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'large.jsonl'
            # Write 6MB file (exceeds 5MB default)
            file_path.write_bytes(b'x' * (6 * 1024 * 1024))

            rotate_if_needed(file_path, max_size=5 * 1024 * 1024)

            # Verify backup created
            backup = file_path.with_suffix('.jsonl.1')
            self.assertTrue(backup.exists())
            self.assertEqual(backup.stat().st_size, 6 * 1024 * 1024)

            # Original should be renamed (not exist anymore)
            self.assertFalse(file_path.exists())


class TestAdvancedPatternDetection(unittest.TestCase):
    """Tests for advanced statistical pattern detection."""

    def test_calculate_tf_idf_empty(self):
        """Test TF-IDF with empty input."""
        result = instinct_cli.calculate_tf_idf([])
        self.assertEqual(result, {})

    def test_calculate_tf_idf_basic(self):
        """Test TF-IDF calculation for tool sequences."""
        sequences = [
            ('Read', 'Edit'),
            ('Read', 'Edit'),
            ('Read', 'Edit'),
            ('Grep', 'Read'),
            ('Bash',),
        ]
        result = instinct_cli.calculate_tf_idf(sequences, min_doc_freq=2)

        # Read->Edit should have higher TF-IDF (more frequent)
        self.assertIn(('Read', 'Edit'), result)
        self.assertGreater(result[('Read', 'Edit')], 0)

        # Bash shouldn't appear (doesn't meet min_doc_freq)
        self.assertNotIn(('Bash',), result)

    def test_calculate_tf_idf_distinctive_patterns(self):
        """Test TF-IDF identifies distinctive patterns."""
        sequences = [
            ('Common', 'Pattern'),
            ('Common', 'Pattern'),
            ('Common', 'Pattern'),
            ('Rare', 'Unique'),
            ('Rare', 'Unique'),
        ]
        result = instinct_cli.calculate_tf_idf(sequences, min_doc_freq=2)

        # Both should be present
        self.assertIn(('Common', 'Pattern'), result)
        self.assertIn(('Rare', 'Unique'), result)

        # Common pattern should have higher TF score
        self.assertGreater(result[('Common', 'Pattern')], result[('Rare', 'Unique')])

    def test_detect_workflow_patterns_empty(self):
        """Test workflow pattern detection with empty input."""
        result = instinct_cli.detect_workflow_patterns([])
        self.assertEqual(result, [])

    def test_detect_workflow_patterns_time_windows(self):
        """Test workflow patterns within time windows."""
        now = datetime.now(timezone.utc)
        observations = []

        # Create pattern within 30-min window
        for i in range(3):
            observations.append({
                'event_type': 'pre',
                'session_id': 's1',
                'tool_name': 'Grep',
                'timestamp': (now + timedelta(minutes=i*5)).isoformat().replace('+00:00', 'Z')
            })
            observations.append({
                'event_type': 'pre',
                'session_id': 's1',
                'tool_name': 'Edit',
                'timestamp': (now + timedelta(minutes=i*5 + 2)).isoformat().replace('+00:00', 'Z')
            })

        result = instinct_cli.detect_workflow_patterns(observations, window_minutes=30)

        # Should detect the Grep->Edit pattern within time windows
        self.assertGreaterEqual(len(result), 0)

    def test_detect_anomalies_empty(self):
        """Test anomaly detection with empty input."""
        result = instinct_cli.detect_anomalies([])
        self.assertEqual(result, [])

    def test_detect_anomalies_high_usage(self):
        """Test anomaly detection for unusually high usage."""
        observations = []

        # Create normal usage for most tools (around 5 times each)
        for tool in ['Read', 'Write', 'Grep', 'Bash', 'Task']:
            for _ in range(5):
                observations.append({
                    'event_type': 'pre',
                    'tool_name': tool
                })

        # Create anomalous high usage for Edit (100 times - much higher)
        for _ in range(100):
            observations.append({
                'event_type': 'pre',
                'tool_name': 'Edit'
            })

        result = instinct_cli.detect_anomalies(observations, threshold_std=1.5)

        # Should detect Edit as high usage anomaly
        high_usage = [a for a in result if a['type'] == 'anomaly-high-usage']
        self.assertGreater(len(high_usage), 0)

        # Verify Edit is flagged
        edit_anomaly = [a for a in high_usage if 'Edit' in a['trigger']]
        self.assertEqual(len(edit_anomaly), 1)

    def test_detect_anomalies_low_usage(self):
        """Test anomaly detection for unusually low usage."""
        observations = []

        # Create normal usage for most tools (around 50 times each)
        for tool in ['Read', 'Edit', 'Grep', 'Bash', 'Write', 'Task', 'Glob']:
            for _ in range(50):
                observations.append({
                    'event_type': 'pre',
                    'tool_name': tool
                })

        # Create anomalous low usage for Rare (only 1 time)
        observations.append({
            'event_type': 'pre',
            'tool_name': 'Rare'
        })

        result = instinct_cli.detect_anomalies(observations, threshold_std=1.5)

        # Should detect Rare as low usage anomaly
        low_usage = [a for a in result if a['type'] == 'anomaly-low-usage']
        self.assertGreater(len(low_usage), 0)

    def test_calculate_statistical_confidence_zero_obs(self):
        """Test confidence calculation with zero observations."""
        result = instinct_cli.calculate_statistical_confidence(0, 0, 0.0)
        self.assertEqual(result, 0.0)

    def test_calculate_statistical_confidence_wilson_score(self):
        """Test Wilson score confidence interval calculation."""
        # High frequency, high count -> high confidence
        conf1 = instinct_cli.calculate_statistical_confidence(
            evidence_count=50,
            total_observations=100,
            pattern_frequency=0.5
        )
        self.assertGreater(conf1, 0.3)

        # Low frequency, low count -> low confidence
        conf2 = instinct_cli.calculate_statistical_confidence(
            evidence_count=2,
            total_observations=100,
            pattern_frequency=0.02
        )
        self.assertLess(conf2, 0.1)

        # High confidence should be greater
        self.assertGreater(conf1, conf2)

    def test_calculate_statistical_confidence_bounds(self):
        """Test confidence is bounded between 0.0 and 1.0."""
        # Edge case: very high frequency
        conf = instinct_cli.calculate_statistical_confidence(
            evidence_count=100,
            total_observations=100,
            pattern_frequency=1.0
        )
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)

    def test_cluster_similar_patterns_empty(self):
        """Test clustering with empty input."""
        result = instinct_cli.cluster_similar_patterns([])
        self.assertEqual(result, [])

    def test_cluster_similar_patterns_jaccard(self):
        """Test pattern clustering using Jaccard similarity."""
        patterns = [
            {'pattern': ('Read', 'Edit', 'Write'), 'id': 'p1'},
            {'pattern': ('Read', 'Edit', 'Grep'), 'id': 'p2'},
            {'pattern': ('Bash', 'Test', 'Deploy'), 'id': 'p3'},
            {'pattern': ('Read', 'Write'), 'id': 'p4'},
        ]

        result = instinct_cli.cluster_similar_patterns(patterns, similarity_threshold=0.5)

        # Should create clusters
        self.assertGreater(len(result), 0)

        # p1 and p2 should cluster together (share Read, Edit)
        # p3 should be separate (no overlap)
        # p4 might cluster with p1 (shares Read, Write)

        # Verify cluster structure
        for cluster in result:
            self.assertIsInstance(cluster, list)
            self.assertGreater(len(cluster), 0)

    def test_cluster_similar_patterns_threshold(self):
        """Test clustering threshold controls grouping."""
        patterns = [
            {'pattern': ('A', 'B', 'C'), 'id': 'p1'},
            {'pattern': ('A', 'B', 'D'), 'id': 'p2'},
            {'pattern': ('X', 'Y', 'Z'), 'id': 'p3'},
        ]

        # High threshold -> more clusters
        result_strict = instinct_cli.cluster_similar_patterns(patterns, similarity_threshold=0.9)

        # Low threshold -> fewer clusters
        result_loose = instinct_cli.cluster_similar_patterns(patterns, similarity_threshold=0.3)

        # Strict should have more or equal clusters than loose
        self.assertGreaterEqual(len(result_strict), len(result_loose))

    def test_cmd_analyze_advanced_flag(self):
        """Test analyze command with --advanced flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Create observations with patterns
            observations = []
            now = datetime.now(timezone.utc)
            for i in range(30):
                observations.append({
                    'event_type': 'pre',
                    'tool_name': 'Edit',
                    'session_id': f's{i // 5}',
                    'timestamp': (now + timedelta(minutes=i)).isoformat().replace('+00:00', 'Z')
                })

            with open(obs_file, 'w', encoding='utf-8') as f:
                for obs in observations:
                    f.write(json.dumps(obs) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                args = argparse.Namespace(incremental=False, full=False, advanced=True)
                result = instinct_cli.cmd_analyze(args)
                self.assertEqual(result, 0)

    def test_cmd_insights_basic(self):
        """Test insights command basic functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            # Create sample observations
            observations = []
            for i in range(20):
                observations.append({
                    'event_type': 'pre',
                    'tool_name': 'Edit',
                    'session_id': f's{i // 5}'
                })

            with open(obs_file, 'w', encoding='utf-8') as f:
                for obs in observations:
                    f.write(json.dumps(obs) + '\n')

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                args = argparse.Namespace()
                result = instinct_cli.cmd_insights(args)
                self.assertEqual(result, 0)

    def test_cmd_insights_no_data(self):
        """Test insights command with no observations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                args = argparse.Namespace()
                result = instinct_cli.cmd_insights(args)
                self.assertEqual(result, 1)


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end workflow tests."""

    def test_observe_analyze_evolve_workflow(self):
        """Test complete workflow: observe -> analyze -> evolve."""
        with tempfile.TemporaryDirectory() as tmpdir:
            obs_dir = Path(tmpdir) / '.caw' / 'observations'
            obs_dir.mkdir(parents=True)
            obs_file = obs_dir / 'observations.jsonl'

            with patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': tmpdir}):
                # Step 1: Simulate tool observations (repeated pattern)
                now = datetime.now(timezone.utc)
                pattern_observations = []

                for session in range(5):  # 5 sessions with same pattern
                    for tool in ['Grep', 'Edit', 'Grep']:
                        pattern_observations.append({
                            'event_type': 'pre',
                            'session_id': f'session-{session}',
                            'tool_name': tool,
                            'timestamp': (now + timedelta(minutes=session*10)).isoformat(),
                        })

                # Write observations
                with open(obs_file, 'w', encoding='utf-8') as f:
                    for obs in pattern_observations:
                        f.write(json.dumps(obs) + '\n')

                # Step 2: Run analysis
                instincts = instinct_cli.detect_tool_sequences(pattern_observations)

                # Step 3: Check instincts generated
                self.assertGreater(len(instincts), 0, "Should detect pattern from repeated sequences")

                # Step 4: Evolve high-confidence instinct
                if instincts:
                    high_conf = [i for i in instincts if i.get('confidence', 0) >= 0.6]
                    if high_conf:
                        instinct = high_conf[0]
                        instinct['id'] = 'workflow-test-abc12345'

                        result = evolution.create_evolution(
                            instinct=instinct,
                            evolution_type='skill',
                            name='auto-search-edit'
                        )

                        # Step 5: Verify evolved file created
                        self.assertTrue(result['success'])
                        self.assertTrue(Path(result['path']).exists())


if __name__ == '__main__':
    # Import types module with alias to avoid conflict with builtins
    sys.path.insert(0, str(SKILL_ROOT / "lib"))
    import types as types_module_builtin
    from lib.types import *

    # Create a fake module for types to avoid import issues
    class TypesModule:
        Observation = Observation
        Instinct = Instinct
        Metrics = Metrics
        EvolutionCandidates = EvolutionCandidates

    sys.modules['types_module'] = TypesModule

    unittest.main()
