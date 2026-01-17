#!/usr/bin/env python3
"""
Tests for validating the context-aware-workflow plugin structure.

Validates:
- plugin.json schema and required fields
- hooks.json schema and hook definitions
- Agent and skill file structure (skills/ contains slash commands)
- Required files existence
"""

import json
import os
import re
import unittest
from pathlib import Path

# Plugin root directory
PLUGIN_ROOT = Path(__file__).parent.parent


class TestPluginStructure(unittest.TestCase):
    """Test plugin directory structure and required files."""

    def test_plugin_json_exists(self):
        """plugin.json must exist in .claude-plugin directory."""
        plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        self.assertTrue(plugin_json.exists(), "plugin.json not found")

    def test_plugin_json_valid(self):
        """plugin.json must be valid JSON with required fields."""
        plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        with open(plugin_json, "r") as f:
            data = json.load(f)

        # Required fields
        self.assertIn("name", data, "plugin.json missing 'name'")
        self.assertIn("version", data, "plugin.json missing 'version'")
        self.assertIn("description", data, "plugin.json missing 'description'")

        # Validate name format
        self.assertRegex(
            data["name"],
            r"^[a-z][a-z0-9-]*$",
            "Plugin name must be lowercase with hyphens",
        )

        # Validate version format (semver)
        self.assertRegex(
            data["version"], r"^\d+\.\d+\.\d+", "Version must follow semver format"
        )

    def test_hooks_json_exists(self):
        """hooks.json must exist in hooks directory."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        self.assertTrue(hooks_json.exists(), "hooks.json not found")

    def test_hooks_json_valid_schema(self):
        """hooks.json must have valid Claude Code hooks schema."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        with open(hooks_json, "r") as f:
            data = json.load(f)

        # Must have 'hooks' key at root
        self.assertIn("hooks", data, "hooks.json must have 'hooks' key at root")
        self.assertIsInstance(data["hooks"], dict, "'hooks' must be an object")

        # Valid hook event names
        valid_events = {
            "SessionStart",
            "PreToolUse",
            "PostToolUse",
            "Notification",
            "Stop",
        }

        for event_name in data["hooks"].keys():
            self.assertIn(
                event_name, valid_events, f"Invalid hook event: {event_name}"
            )

            # Each event must be an array
            self.assertIsInstance(
                data["hooks"][event_name], list, f"{event_name} must be an array"
            )

            # Each item must have 'hooks' array
            for item in data["hooks"][event_name]:
                self.assertIn(
                    "hooks", item, f"{event_name} items must have 'hooks' array"
                )
                self.assertIsInstance(
                    item["hooks"], list, f"{event_name} hooks must be an array"
                )

    def test_required_directories_exist(self):
        """Required plugin directories must exist."""
        # commands/ contains the slash commands (e.g., /caw:start)
        required_dirs = ["agents", "hooks", "commands", "docs"]

        for dir_name in required_dirs:
            dir_path = PLUGIN_ROOT / dir_name
            self.assertTrue(dir_path.is_dir(), f"Directory '{dir_name}' not found")

    def test_readme_exists(self):
        """README.md must exist in plugin root."""
        readme = PLUGIN_ROOT / "README.md"
        self.assertTrue(readme.exists(), "README.md not found")


class TestAgentFiles(unittest.TestCase):
    """Test agent file structure and frontmatter."""

    def get_agent_files(self):
        """Get all agent markdown files."""
        agents_dir = PLUGIN_ROOT / "agents"
        return list(agents_dir.glob("*.md"))

    def test_agents_exist(self):
        """At least one agent file must exist."""
        agents = self.get_agent_files()
        self.assertGreater(len(agents), 0, "No agent files found")

    def test_agent_frontmatter(self):
        """Each agent must have valid YAML frontmatter."""
        for agent_file in self.get_agent_files():
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Must start with ---
            self.assertTrue(
                content.startswith("---"),
                f"{agent_file.name} must start with YAML frontmatter",
            )

            # Must have closing ---
            parts = content.split("---", 2)
            self.assertGreaterEqual(
                len(parts), 3, f"{agent_file.name} must have closing ---"
            )

            # Frontmatter must contain required fields
            frontmatter = parts[1]
            self.assertIn(
                "name:", frontmatter, f"{agent_file.name} missing 'name' in frontmatter"
            )
            self.assertIn(
                "description:",
                frontmatter,
                f"{agent_file.name} missing 'description' in frontmatter",
            )

    def test_agent_has_system_prompt(self):
        """Each agent must have a system prompt section."""
        for agent_file in self.get_agent_files():
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Should have a heading with "System Prompt" or similar
            self.assertTrue(
                "# " in content,
                f"{agent_file.name} must have markdown headings for system prompt",
            )


class TestCommandFiles(unittest.TestCase):
    """Test command file structure and frontmatter."""

    def get_command_files(self):
        """Get all command .md files."""
        commands_dir = PLUGIN_ROOT / "commands"
        return list(commands_dir.glob("*.md"))

    def test_commands_exist(self):
        """At least one command file must exist."""
        commands = self.get_command_files()
        self.assertGreater(len(commands), 0, "No command files found")

    def test_command_frontmatter(self):
        """Each command must have valid YAML frontmatter with description."""
        for cmd_file in self.get_command_files():
            with open(cmd_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Must start with ---
            self.assertTrue(
                content.startswith("---"),
                f"{cmd_file.name} must start with YAML frontmatter",
            )

            # Must have closing ---
            parts = content.split("---", 2)
            self.assertGreaterEqual(
                len(parts), 3, f"{cmd_file.name} must have closing ---"
            )

            # Frontmatter must contain description
            frontmatter = parts[1]
            self.assertIn(
                "description:",
                frontmatter,
                f"{cmd_file.name} missing 'description' in frontmatter",
            )

    def test_command_has_usage(self):
        """Each command should have a Usage or Invocation section."""
        for cmd_file in self.get_command_files():
            with open(cmd_file, "r", encoding="utf-8") as f:
                content = f.read()
            content_lower = content.lower()

            # Should have Usage or Invocation section
            has_usage = "## usage" in content_lower
            has_invocation = "## invocation" in content_lower
            self.assertTrue(
                has_usage or has_invocation,
                f"{cmd_file.name} should have a Usage or Invocation section",
            )


class TestRequiredAgents(unittest.TestCase):
    """Test that required agents are present."""

    def test_planner_agent_exists(self):
        """Planner agent must exist."""
        planner = PLUGIN_ROOT / "agents" / "planner.md"
        self.assertTrue(planner.exists(), "planner.md agent not found")

    def test_builder_agent_exists(self):
        """Builder agent must exist."""
        builder = PLUGIN_ROOT / "agents" / "builder.md"
        self.assertTrue(builder.exists(), "builder.md agent not found")

    def test_reviewer_agent_exists(self):
        """Reviewer agent must exist."""
        reviewer = PLUGIN_ROOT / "agents" / "reviewer.md"
        self.assertTrue(reviewer.exists(), "reviewer.md agent not found")

    def test_compliance_checker_exists(self):
        """ComplianceChecker agent must exist."""
        checker = PLUGIN_ROOT / "agents" / "compliance-checker.md"
        self.assertTrue(checker.exists(), "compliance-checker.md agent not found")

    def test_ideator_agent_exists(self):
        """Ideator agent must exist."""
        ideator = PLUGIN_ROOT / "agents" / "ideator.md"
        self.assertTrue(ideator.exists(), "ideator.md agent not found")

    def test_designer_agent_exists(self):
        """Designer agent must exist."""
        designer = PLUGIN_ROOT / "agents" / "designer.md"
        self.assertTrue(designer.exists(), "designer.md agent not found")

    def test_architect_agent_exists(self):
        """Architect agent must exist."""
        architect = PLUGIN_ROOT / "agents" / "architect.md"
        self.assertTrue(architect.exists(), "architect.md agent not found")


class TestRequiredCommands(unittest.TestCase):
    """Test that required commands are present."""

    def test_start_command_exists(self):
        """start command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "start.md"
        self.assertTrue(cmd.exists(), "commands/start.md not found")

    def test_status_command_exists(self):
        """status command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "status.md"
        self.assertTrue(cmd.exists(), "commands/status.md not found")

    def test_next_command_exists(self):
        """next command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "next.md"
        self.assertTrue(cmd.exists(), "commands/next.md not found")

    def test_review_command_exists(self):
        """review command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "review.md"
        self.assertTrue(cmd.exists(), "commands/review.md not found")

    def test_check_command_exists(self):
        """check command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "check.md"
        self.assertTrue(cmd.exists(), "commands/check.md not found")

    def test_context_command_exists(self):
        """context command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "context.md"
        self.assertTrue(cmd.exists(), "commands/context.md not found")

    def test_brainstorm_command_exists(self):
        """brainstorm command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "brainstorm.md"
        self.assertTrue(cmd.exists(), "commands/brainstorm.md not found")

    def test_design_command_exists(self):
        """design command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "design.md"
        self.assertTrue(cmd.exists(), "commands/design.md not found")

    def test_fix_command_exists(self):
        """fix command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "fix.md"
        self.assertTrue(cmd.exists(), "commands/fix.md not found")

    def test_init_command_exists(self):
        """init command must exist."""
        cmd = PLUGIN_ROOT / "commands" / "init.md"
        self.assertTrue(cmd.exists(), "commands/init.md not found")

    def test_reflect_command_exists(self):
        """reflect command must exist for Ralph Loop."""
        cmd = PLUGIN_ROOT / "commands" / "reflect.md"
        self.assertTrue(cmd.exists(), "commands/reflect.md not found")


class TestSkillFiles(unittest.TestCase):
    """Test skill file structure and SKILL.md files."""

    def get_skill_dirs(self):
        """Get all skill directories."""
        skills_dir = PLUGIN_ROOT / "skills"
        if not skills_dir.exists():
            return []
        return [d for d in skills_dir.iterdir() if d.is_dir()]

    def test_skills_directory_exists(self):
        """skills/ directory must exist."""
        skills_dir = PLUGIN_ROOT / "skills"
        self.assertTrue(skills_dir.is_dir(), "skills/ directory not found")

    def test_skills_exist(self):
        """At least one skill must exist."""
        skills = self.get_skill_dirs()
        self.assertGreater(len(skills), 0, "No skill directories found")

    def test_skill_has_skill_md(self):
        """Each skill directory must have a SKILL.md file."""
        for skill_dir in self.get_skill_dirs():
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(
                skill_md.exists(),
                f"{skill_dir.name} missing SKILL.md",
            )

    def test_skill_frontmatter(self):
        """Each SKILL.md must have valid YAML frontmatter with name and description."""
        for skill_dir in self.get_skill_dirs():
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()

            # Must start with ---
            self.assertTrue(
                content.startswith("---"),
                f"{skill_dir.name}/SKILL.md must start with YAML frontmatter",
            )

            # Must have closing ---
            parts = content.split("---", 2)
            self.assertGreaterEqual(
                len(parts), 3, f"{skill_dir.name}/SKILL.md must have closing ---"
            )

            # Frontmatter must contain required fields
            frontmatter = parts[1]
            self.assertIn(
                "name:", frontmatter, f"{skill_dir.name}/SKILL.md missing 'name'"
            )
            self.assertIn(
                "description:",
                frontmatter,
                f"{skill_dir.name}/SKILL.md missing 'description'",
            )


class TestRequiredSkills(unittest.TestCase):
    """Test that required skills are present."""

    def test_plan_detector_skill_exists(self):
        """plan-detector skill must exist."""
        skill = PLUGIN_ROOT / "skills" / "plan-detector" / "SKILL.md"
        self.assertTrue(skill.exists(), "plan-detector/SKILL.md not found")

    def test_insight_collector_skill_exists(self):
        """insight-collector skill must exist."""
        skill = PLUGIN_ROOT / "skills" / "insight-collector" / "SKILL.md"
        self.assertTrue(skill.exists(), "insight-collector/SKILL.md not found")

    def test_session_persister_skill_exists(self):
        """session-persister skill must exist."""
        skill = PLUGIN_ROOT / "skills" / "session-persister" / "SKILL.md"
        self.assertTrue(skill.exists(), "session-persister/SKILL.md not found")

    def test_quality_gate_skill_exists(self):
        """quality-gate skill must exist."""
        skill = PLUGIN_ROOT / "skills" / "quality-gate" / "SKILL.md"
        self.assertTrue(skill.exists(), "quality-gate/SKILL.md not found")

    def test_progress_tracker_skill_exists(self):
        """progress-tracker skill must exist."""
        skill = PLUGIN_ROOT / "skills" / "progress-tracker" / "SKILL.md"
        self.assertTrue(skill.exists(), "progress-tracker/SKILL.md not found")

    def test_context_helper_skill_exists(self):
        """context-helper skill must exist."""
        skill = PLUGIN_ROOT / "skills" / "context-helper" / "SKILL.md"
        self.assertTrue(skill.exists(), "context-helper/SKILL.md not found")

    def test_reflect_skill_exists(self):
        """reflect skill must exist for Ralph Loop."""
        skill = PLUGIN_ROOT / "skills" / "reflect" / "SKILL.md"
        self.assertTrue(skill.exists(), "reflect/SKILL.md not found")

    def test_quick_fix_skill_exists(self):
        """quick-fix skill must exist."""
        skill = PLUGIN_ROOT / "skills" / "quick-fix" / "SKILL.md"
        self.assertTrue(skill.exists(), "quick-fix/SKILL.md not found")


class TestRalphLoopIntegration(unittest.TestCase):
    """Test Ralph Loop continuous improvement integration."""

    def test_ralph_loop_schema_exists(self):
        """Ralph Loop schema must exist."""
        schema = PLUGIN_ROOT / "_shared" / "schemas" / "ralph-loop.schema.json"
        self.assertTrue(schema.exists(), "ralph-loop.schema.json not found")

    def test_ralph_loop_schema_valid(self):
        """Ralph Loop schema must be valid JSON with required fields."""
        schema_path = PLUGIN_ROOT / "_shared" / "schemas" / "ralph-loop.schema.json"
        with open(schema_path, "r") as f:
            schema = json.load(f)

        # Required schema properties
        self.assertIn("properties", schema)
        props = schema["properties"]

        # Must have RALPH phases
        self.assertIn("phases", props)
        phases = props["phases"].get("properties", {})

        # Check all 5 RALPH phases exist
        required_phases = ["reflect", "analyze", "learn", "plan", "habituate"]
        for phase in required_phases:
            self.assertIn(phase, phases, f"Missing RALPH phase: {phase}")

    def test_learnings_template_exists(self):
        """Learnings template must exist."""
        template = PLUGIN_ROOT / "_shared" / "learnings-template.md"
        self.assertTrue(template.exists(), "learnings-template.md not found")

    def test_magic_keywords_doc_exists(self):
        """Magic keywords documentation must exist."""
        doc = PLUGIN_ROOT / "_shared" / "magic-keywords.md"
        self.assertTrue(doc.exists(), "magic-keywords.md not found")


class TestTieredAgents(unittest.TestCase):
    """Test tiered agent variants exist."""

    def test_planner_tiers_exist(self):
        """Planner agent tiers must exist."""
        agents_dir = PLUGIN_ROOT / "agents"
        self.assertTrue((agents_dir / "planner.md").exists(), "planner.md not found")
        self.assertTrue(
            (agents_dir / "planner-haiku.md").exists(), "planner-haiku.md not found"
        )
        self.assertTrue(
            (agents_dir / "planner-opus.md").exists(), "planner-opus.md not found"
        )

    def test_builder_tiers_exist(self):
        """Builder agent tiers must exist."""
        agents_dir = PLUGIN_ROOT / "agents"
        self.assertTrue((agents_dir / "builder.md").exists(), "builder.md not found")
        self.assertTrue(
            (agents_dir / "builder-haiku.md").exists(), "builder-haiku.md not found"
        )
        self.assertTrue(
            (agents_dir / "builder-sonnet.md").exists(), "builder-sonnet.md not found"
        )

    def test_reviewer_tiers_exist(self):
        """Reviewer agent tiers must exist."""
        agents_dir = PLUGIN_ROOT / "agents"
        self.assertTrue((agents_dir / "reviewer.md").exists(), "reviewer.md not found")
        self.assertTrue(
            (agents_dir / "reviewer-haiku.md").exists(), "reviewer-haiku.md not found"
        )
        self.assertTrue(
            (agents_dir / "reviewer-opus.md").exists(), "reviewer-opus.md not found"
        )

    def test_fixer_tiers_exist(self):
        """Fixer agent tiers must exist."""
        agents_dir = PLUGIN_ROOT / "agents"
        self.assertTrue((agents_dir / "fixer.md").exists(), "fixer.md not found")
        self.assertTrue(
            (agents_dir / "fixer-haiku.md").exists(), "fixer-haiku.md not found"
        )
        self.assertTrue(
            (agents_dir / "fixer-sonnet.md").exists(), "fixer-sonnet.md not found"
        )


class TestModelRoutingSchema(unittest.TestCase):
    """Test model routing schema exists."""

    def test_model_routing_schema_exists(self):
        """Model routing schema must exist."""
        schema = PLUGIN_ROOT / "_shared" / "schemas" / "model-routing.schema.json"
        self.assertTrue(schema.exists(), "model-routing.schema.json not found")


class TestHooksConfiguration(unittest.TestCase):
    """Test hooks configuration details."""

    def setUp(self):
        """Load hooks.json."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        with open(hooks_json, "r") as f:
            self.hooks_data = json.load(f)

    def test_required_hooks_exist(self):
        """Required hooks (SessionStart, PreToolUse) must be configured."""
        # PostToolUse is optional - only add if meaningful functionality needed
        self.assertIn("SessionStart", self.hooks_data["hooks"])
        self.assertIn("PreToolUse", self.hooks_data["hooks"])

    def test_hook_types_valid(self):
        """All hooks must have valid type field."""
        valid_types = {"prompt", "command"}

        for event_name, event_hooks in self.hooks_data["hooks"].items():
            for hook_group in event_hooks:
                for hook in hook_group["hooks"]:
                    self.assertIn("type", hook, f"{event_name} hook missing 'type'")
                    self.assertIn(
                        hook["type"],
                        valid_types,
                        f"{event_name} has invalid hook type: {hook['type']}",
                    )

    def test_hooks_have_matchers_where_needed(self):
        """PostToolUse hooks should have matchers for tool filtering."""
        post_hooks = self.hooks_data["hooks"].get("PostToolUse", [])
        for hook_group in post_hooks:
            # PostToolUse hooks should have matcher to specify which tool
            self.assertIn(
                "matcher",
                hook_group,
                "PostToolUse hooks should have matcher for tool filtering",
            )


if __name__ == "__main__":
    unittest.main()
