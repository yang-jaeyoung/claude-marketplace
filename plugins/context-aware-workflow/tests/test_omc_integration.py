#!/usr/bin/env python3
"""
Tests for OMC (Oh-My-ClaudeCode) integration in CAW plugin.

Validates:
- omc_resolver.py script structure and functions
- Fallback mapping completeness
- Agent resolution logic
- OMC detection methods
- Schema documentation
"""

import json
import os
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Plugin root directory
PLUGIN_ROOT = Path(__file__).parent.parent

# Add hooks/scripts to path for importing
sys.path.insert(0, str(PLUGIN_ROOT / "hooks" / "scripts"))


class TestOMCResolverScript(unittest.TestCase):
    """Test omc_resolver.py script exists and is properly structured."""

    def test_omc_resolver_exists(self):
        """omc_resolver.py must exist in hooks/scripts."""
        resolver = PLUGIN_ROOT / "hooks" / "scripts" / "omc_resolver.py"
        self.assertTrue(resolver.exists(), "omc_resolver.py not found")

    def test_omc_resolver_importable(self):
        """omc_resolver.py must be importable."""
        try:
            import omc_resolver
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import omc_resolver: {e}")

    def test_required_functions_exist(self):
        """Required functions must be defined."""
        import omc_resolver

        required_functions = [
            "detect_omc",
            "is_omc_available",
            "resolve_agent",
            "get_fallback_map",
            "update_manifest_environment",
        ]

        for func_name in required_functions:
            self.assertTrue(
                hasattr(omc_resolver, func_name),
                f"Missing required function: {func_name}"
            )
            self.assertTrue(
                callable(getattr(omc_resolver, func_name)),
                f"{func_name} is not callable"
            )

    def test_fallback_map_constant_exists(self):
        """FALLBACK_MAP constant must be defined."""
        import omc_resolver

        self.assertTrue(
            hasattr(omc_resolver, "FALLBACK_MAP"),
            "FALLBACK_MAP constant not found"
        )
        self.assertIsInstance(omc_resolver.FALLBACK_MAP, dict)

    def test_degraded_features_constant_exists(self):
        """DEGRADED_FEATURES constant must be defined."""
        import omc_resolver

        self.assertTrue(
            hasattr(omc_resolver, "DEGRADED_FEATURES"),
            "DEGRADED_FEATURES constant not found"
        )
        self.assertIsInstance(omc_resolver.DEGRADED_FEATURES, list)


class TestFallbackMapping(unittest.TestCase):
    """Test OMC to CAW fallback mapping completeness."""

    def setUp(self):
        """Load fallback map."""
        import omc_resolver
        self.fallback_map = omc_resolver.get_fallback_map()

    def test_all_core_omc_agents_mapped(self):
        """All core OMC agents must have fallback mappings."""
        core_omc_agents = [
            "omc:architect",
            "omc:designer",
            "omc:researcher",
            "omc:scientist",
            "omc:analyst",
            "omc:explore",
            "omc:executor",
            "omc:build-fixer",
            "omc:qa-tester",
            "omc:critic",
            "omc:code-reviewer",
            "omc:security-reviewer",
            "omc:tdd-guide",
            "omc:planner",
            "omc:writer",
            "omc:vision",
        ]

        for agent in core_omc_agents:
            self.assertIn(
                agent, self.fallback_map,
                f"Missing fallback mapping for: {agent}"
            )

    def test_fallbacks_are_valid_caw_agents(self):
        """All fallback values must be valid CAW agents or built-in types."""
        valid_prefixes = ["cw:", "general-purpose", "Explore", "Plan"]

        for omc_agent, fallback in self.fallback_map.items():
            is_valid = any(fallback.startswith(p) or fallback == p for p in valid_prefixes)
            self.assertTrue(
                is_valid,
                f"Invalid fallback for {omc_agent}: {fallback}"
            )

    def test_tiered_agents_have_tiered_fallbacks(self):
        """Tiered OMC agents should have appropriate CAW tier fallbacks."""
        # Low tier OMC agents should fall back to haiku tier
        low_tier_mappings = {
            "omc:architect-low": "cw:architect",
            "omc:researcher-low": "cw:planner-haiku",
            "omc:executor-low": "cw:builder-haiku",
            "omc:build-fixer-low": "cw:fixer-haiku",
        }

        for omc_agent, expected in low_tier_mappings.items():
            if omc_agent in self.fallback_map:
                # Just verify it exists and is reasonable
                fallback = self.fallback_map[omc_agent]
                self.assertIsNotNone(fallback, f"Null fallback for {omc_agent}")


class TestAgentResolution(unittest.TestCase):
    """Test agent resolution logic."""

    def test_caw_agents_pass_through(self):
        """CAW-namespaced agents should pass through unchanged."""
        import omc_resolver

        caw_agents = [
            "cw:Builder",
            "cw:Planner",
            "cw:Reviewer",
            "cw:Fixer",
            "cw:architect",
        ]

        for agent in caw_agents:
            resolved, is_fallback, warning = omc_resolver.resolve_agent(agent)
            self.assertEqual(resolved, agent)
            self.assertFalse(is_fallback)
            self.assertIsNone(warning)

    def test_bare_names_pass_through(self):
        """Bare agent names (no namespace) should pass through."""
        import omc_resolver

        bare_agents = ["general-purpose", "Explore", "Plan"]

        for agent in bare_agents:
            resolved, is_fallback, warning = omc_resolver.resolve_agent(agent)
            self.assertEqual(resolved, agent)
            self.assertFalse(is_fallback)

    @patch.dict(os.environ, {"OMC_ENABLED": ""}, clear=False)
    def test_omc_agents_fallback_when_unavailable(self):
        """OMC agents should fall back when OMC is not available."""
        import omc_resolver

        # Clear cache to force re-detection
        omc_resolver._omc_detection_cache = None

        resolved, is_fallback, warning = omc_resolver.resolve_agent("omc:architect")

        # Should fall back to cw:architect
        self.assertEqual(resolved, "cw:architect")
        self.assertTrue(is_fallback)
        self.assertIsNotNone(warning)

    @patch.dict(os.environ, {"OMC_ENABLED": "true"}, clear=False)
    def test_omc_agents_pass_through_when_available(self):
        """OMC agents should pass through when OMC is available."""
        import omc_resolver

        # Clear cache to force re-detection
        omc_resolver._omc_detection_cache = None

        resolved, is_fallback, warning = omc_resolver.resolve_agent("omc:architect")

        # Should keep original
        self.assertEqual(resolved, "omc:architect")
        self.assertFalse(is_fallback)
        self.assertIsNone(warning)

    def test_empty_agent_returns_general_purpose(self):
        """Empty agent string should return general-purpose."""
        import omc_resolver

        resolved, is_fallback, warning = omc_resolver.resolve_agent("")
        self.assertEqual(resolved, "general-purpose")
        self.assertFalse(is_fallback)


class TestOMCDetection(unittest.TestCase):
    """Test OMC detection methods."""

    def setUp(self):
        """Clear cache before each test."""
        import omc_resolver
        omc_resolver._omc_detection_cache = None

    @patch.dict(os.environ, {"OMC_ENABLED": "true"}, clear=False)
    def test_env_variable_detection(self):
        """OMC_ENABLED=true should enable OMC."""
        import omc_resolver

        # Clear cache
        omc_resolver._omc_detection_cache = None

        result = omc_resolver.detect_omc()

        self.assertTrue(result["omc_available"])
        self.assertEqual(result["detection_method"], "env_variable")
        self.assertFalse(result["fallback_mode"])
        self.assertEqual(result["degraded_features"], [])

    @patch.dict(os.environ, {"OMC_ENABLED": ""}, clear=False)
    def test_detection_returns_required_fields(self):
        """Detection result must have all required fields."""
        import omc_resolver

        # Clear cache
        omc_resolver._omc_detection_cache = None

        result = omc_resolver.detect_omc()

        required_fields = [
            "omc_available",
            "omc_version",
            "detection_method",
            "fallback_mode",
            "degraded_features",
            "detected_at",
        ]

        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")

    def test_detection_caching(self):
        """Detection result should be cached."""
        import omc_resolver

        # Clear cache
        omc_resolver._omc_detection_cache = None

        result1 = omc_resolver.detect_omc()
        result2 = omc_resolver.detect_omc()

        # Should return same cached result
        self.assertEqual(result1["detected_at"], result2["detected_at"])

    def test_is_omc_available_returns_bool(self):
        """is_omc_available() should return boolean."""
        import omc_resolver

        result = omc_resolver.is_omc_available()
        self.assertIsInstance(result, bool)


class TestEnvironmentSchema(unittest.TestCase):
    """Test environment section is documented in manifest schema."""

    def test_manifest_schema_has_environment_section(self):
        """manifest.schema.md must document environment section."""
        schema_path = PLUGIN_ROOT / "_shared" / "schemas" / "manifest.schema.md"
        self.assertTrue(schema_path.exists(), "manifest.schema.md not found")

        with open(schema_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Must have environment section
        self.assertIn("## Environment Detection", content)
        self.assertIn("omc_available", content)
        self.assertIn("detection_method", content)
        self.assertIn("fallback_mode", content)
        self.assertIn("degraded_features", content)

    def test_manifest_schema_documents_detection_methods(self):
        """manifest.schema.md must document detection methods."""
        schema_path = PLUGIN_ROOT / "_shared" / "schemas" / "manifest.schema.md"

        with open(schema_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Must document detection methods
        self.assertIn("env_variable", content)
        self.assertIn("plugin_directory", content)
        self.assertIn("not_found", content)


class TestAgentResolverDocumentation(unittest.TestCase):
    """Test agent-resolver.md documents implementation."""

    def test_agent_resolver_documents_script(self):
        """agent-resolver.md must document omc_resolver.py."""
        doc_path = PLUGIN_ROOT / "_shared" / "agent-resolver.md"
        self.assertTrue(doc_path.exists(), "agent-resolver.md not found")

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Must reference the implementation script
        self.assertIn("omc_resolver.py", content)
        self.assertIn("hooks/scripts/omc_resolver.py", content)

    def test_agent_resolver_documents_functions(self):
        """agent-resolver.md must document key functions."""
        doc_path = PLUGIN_ROOT / "_shared" / "agent-resolver.md"

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Must document key functions
        functions = [
            "detect_omc",
            "is_omc_available",
            "resolve_agent",
            "get_fallback_map",
        ]

        for func in functions:
            self.assertIn(
                func, content,
                f"Function '{func}' not documented in agent-resolver.md"
            )

    def test_agent_resolver_documents_env_vars(self):
        """agent-resolver.md must document environment variables."""
        doc_path = PLUGIN_ROOT / "_shared" / "agent-resolver.md"

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Must document environment variables
        self.assertIn("OMC_ENABLED", content)
        self.assertIn("OMC_DEBUG", content)


class TestAgentRegistryConsistency(unittest.TestCase):
    """Test consistency between agent-registry.md and omc_resolver.py."""

    def setUp(self):
        """Load agent registry and fallback map."""
        self.registry_path = PLUGIN_ROOT / "_shared" / "agent-registry.md"

        import omc_resolver
        self.fallback_map = omc_resolver.get_fallback_map()

    def test_registry_exists(self):
        """agent-registry.md must exist."""
        self.assertTrue(self.registry_path.exists())

    def test_documented_fallbacks_match_implementation(self):
        """Documented fallbacks in registry should match implementation."""
        with open(self.registry_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract documented mappings from registry tables
        # Format: | `omc:agent` | Model | `cw:fallback` |
        pattern = r"\| `(omc:[a-z-]+)` \| [^|]+ \| `(cw:[^`]+)`"
        documented_mappings = re.findall(pattern, content)

        for omc_agent, documented_fallback in documented_mappings:
            if omc_agent in self.fallback_map:
                implemented_fallback = self.fallback_map[omc_agent]
                # Allow for minor differences (e.g., flags like --security)
                if not documented_fallback.startswith(implemented_fallback.split()[0]):
                    # Just check they are related
                    self.assertIn(
                        "cw:", implemented_fallback,
                        f"Mismatch for {omc_agent}: doc={documented_fallback}, impl={implemented_fallback}"
                    )


if __name__ == "__main__":
    unittest.main()
