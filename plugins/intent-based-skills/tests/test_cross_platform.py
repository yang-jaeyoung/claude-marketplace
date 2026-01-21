#!/usr/bin/env python3
"""Cross-platform compatibility tests for intent-based-skills plugin.

Validates:
- Commands use cross-platform patterns for environment variables
- Python scripts include Windows UTF-8 support
"""

import re
import unittest
from pathlib import Path

# Plugin root directory
PLUGIN_ROOT = Path(__file__).parent.parent


class TestCommandsCrossPlatform(unittest.TestCase):
    """Test commands for cross-platform compatibility."""

    def test_no_direct_env_var_in_bash(self):
        """Commands should not use ${VAR} syntax directly for CLAUDE_PLUGIN_ROOT.
        
        The pattern `python ${CLAUDE_PLUGIN_ROOT}/...` fails on Windows because
        the shell variable is not expanded. Instead, use Python's os.environ.get().
        """
        commands_dir = PLUGIN_ROOT / "commands"

        for cmd_file in commands_dir.glob("*.md"):
            content = cmd_file.read_text(encoding="utf-8")

            # Check for bash blocks with direct env var expansion
            if "```bash" in content:
                bash_blocks = content.split("```bash")[1:]
                for block in bash_blocks:
                    block_content = block.split("```")[0]
                    
                    # The problematic pattern: python ${CLAUDE_PLUGIN_ROOT}/path
                    # This should be replaced with python -c "..." pattern
                    if "${CLAUDE_PLUGIN_ROOT}" in block_content:
                        # Check if it's using the safe pattern (python -c with os.environ.get)
                        has_safe_pattern = (
                            'python -c' in block_content and 
                            "os.environ.get('CLAUDE_PLUGIN_ROOT'" in block_content
                        )
                        
                        # If not using safe pattern, it's a problem
                        if not has_safe_pattern:
                            self.fail(
                                f"{cmd_file.name} uses ${{CLAUDE_PLUGIN_ROOT}} directly. "
                                "Use Python inline pattern with os.environ.get() instead."
                            )


class TestPythonScriptsCrossPlatform(unittest.TestCase):
    """Test Python scripts for cross-platform compatibility."""

    def test_python_scripts_have_utf8_support(self):
        """Python scripts that print should handle Windows UTF-8."""
        lib_dir = PLUGIN_ROOT / "lib"

        if not lib_dir.exists():
            self.skipTest("No lib directory found")

        for py_file in lib_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")

            # Scripts that print to stdout should have UTF-8 handling
            if "print(" in content:
                # Check for the Windows UTF-8 pattern
                has_platform_check = "sys.platform" in content
                has_encoding_handling = "reconfigure(encoding" in content or "encoding='utf-8'" in content

                self.assertTrue(
                    has_platform_check or has_encoding_handling,
                    f"{py_file.name} prints output but may lack Windows UTF-8 support. "
                    "Add sys.platform check with stdout.reconfigure(encoding='utf-8')"
                )


class TestLibraryScriptsHaveMain(unittest.TestCase):
    """Test that library scripts can be executed from command-line."""

    def test_feedback_collector_executable(self):
        """feedback_collector.py should be executable from command-line."""
        lib_dir = PLUGIN_ROOT / "lib"
        collector = lib_dir / "feedback_collector.py"

        if not collector.exists():
            self.skipTest("feedback_collector.py not found")

        content = collector.read_text(encoding="utf-8")
        # Should have either main() function or if __name__ == "__main__": block
        has_main = "def main(" in content
        has_name_main = 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content
        
        self.assertTrue(
            has_main or has_name_main,
            "feedback_collector.py should have main() function or if __name__ == '__main__' block for command-line usage"
        )

    def test_feedback_analyzer_executable(self):
        """feedback_analyzer.py should be executable from command-line."""
        lib_dir = PLUGIN_ROOT / "lib"
        analyzer = lib_dir / "feedback_analyzer.py"

        if not analyzer.exists():
            self.skipTest("feedback_analyzer.py not found")

        content = analyzer.read_text(encoding="utf-8")
        # Should have either main() function or if __name__ == "__main__": block
        has_main = "def main(" in content
        has_name_main = 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content
        
        self.assertTrue(
            has_main or has_name_main,
            "feedback_analyzer.py should have main() function or if __name__ == '__main__' block for command-line usage"
        )


if __name__ == "__main__":
    unittest.main()
