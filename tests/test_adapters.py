"""Cross-platform build and safe-install tests for native runtime adapters."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from adapter_support import (
    ADAPTERS,
    BEGIN_MARKER,
    END_MARKER,
    LAYOUTS,
    build_adapter,
    build_all_adapters,
    install_adapter,
)


class AdapterBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / "dist"

    def test_builds_all_native_adapters(self):
        results = build_all_adapters(ROOT, self.output)
        self.assertEqual([item["adapter"] for item in results], list(ADAPTERS))
        self.assertTrue(all(item["agents"] == 7 for item in results))
        self.assertTrue(all(item["skills"] == 19 for item in results))

        for adapter in ADAPTERS:
            bundle = self.output / adapter
            manifest = json.loads((bundle / "adapter.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["adapter"], adapter)
            self.assertEqual(len(manifest["agents"]), 7)
            self.assertEqual(len(manifest["skills"]), 19)
            self.assertTrue((bundle / LAYOUTS[adapter]["instructions"]).is_file())

    def test_builder_refuses_to_delete_unmanaged_output_directory(self):
        destination = self.output / "codex"
        destination.mkdir(parents=True)
        keep = destination / "user-file.txt"
        keep.write_text("preserve me", encoding="utf-8")
        with self.assertRaises(ValueError):
            build_adapter(ROOT, "codex", destination)
        self.assertEqual(keep.read_text(encoding="utf-8"), "preserve me")

    def test_codex_profiles_are_valid_toml(self):
        build_all_adapters(ROOT, self.output)
        agent_dir = self.output / "codex" / ".codex" / "agents"
        profiles = sorted(agent_dir.glob("*.toml"))
        self.assertEqual(len(profiles), 7)
        for path in profiles:
            profile = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(profile["name"])
            self.assertTrue(profile["description"])
            self.assertTrue(profile["developer_instructions"])

    def test_cursor_agents_use_native_frontmatter_without_antigravity_policy(self):
        build_all_adapters(ROOT, self.output)
        agent_dir = self.output / "cursor" / ".cursor" / "agents"
        profiles = sorted(agent_dir.glob("*.md"))
        self.assertEqual(len(profiles), 7)
        for path in profiles:
            content = path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\\n"))
            frontmatter = content.split("\\n---", 1)[0]
            self.assertIn(f"name: {path.stem}", frontmatter)
            self.assertIn("description:", frontmatter)
            self.assertNotIn("tools:", frontmatter)
            self.assertNotIn("commandExecutionPolicy:", content)
            self.assertNotIn("inheritCustomizations:", content)

    def test_cursor_project_rule_uses_native_mdc_frontmatter(self):
        build_all_adapters(ROOT, self.output)
        rule = self.output / "cursor" / ".cursor" / "rules" / "ai-agent-ecosystem.mdc"
        content = rule.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\\n"))
        frontmatter = content.split("\\n---", 1)[0]
        self.assertIn("description: Shared AI Agent Ecosystem instructions", frontmatter)
        self.assertIn("alwaysApply: true", frontmatter)
        self.assertNotIn("<!-- BEGIN AI AGENT ECOSYSTEM MANAGED INSTRUCTIONS -->", content)

    def test_copilot_subagents_inherit_repository_instructions(self):
        build_all_adapters(ROOT, self.output)
        agent_dir = self.output / "copilot" / ".github" / "agents"
        for path in agent_dir.glob("*.agent.md"):
            self.assertIn("include-custom-instructions: true", path.read_text(encoding="utf-8"))

    def test_non_antigravity_profiles_have_no_antigravity_frontmatter(self):
        build_all_adapters(ROOT, self.output)
        for adapter in ("copilot", "claude-code"):
            agent_dir = self.output / adapter / LAYOUTS[adapter]["agents"]
            for path in agent_dir.iterdir():
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("commandExecutionPolicy:", content)
                self.assertNotIn("inheritCustomizations:", content)
                self.assertNotIn("tools:\n  - read_file", content)

    def test_native_skill_payloads_match_canonical_sources(self):
        build_all_adapters(ROOT, self.output)
        for adapter in ADAPTERS:
            skill_dir = self.output / adapter / LAYOUTS[adapter]["skills"]
            self.assertEqual(len(list(skill_dir.glob("*/SKILL.md"))), 19)
            for source in (ROOT / "modules").glob("*/skills/*/SKILL.md"):
                target = skill_dir / source.parent.name / "SKILL.md"
                self.assertEqual(source.read_bytes(), target.read_bytes())


class AdapterInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir()

    def test_install_preserves_and_idempotently_updates_existing_instructions(self):
        instructions = self.project / "AGENTS.md"
        instructions.write_text("# My existing project rules\n\nKeep this section.\n", encoding="utf-8")

        first = install_adapter("codex", self.project, root=ROOT)
        self.assertEqual(first["conflicts"], [])
        installed = instructions.read_text(encoding="utf-8")
        self.assertIn("# My existing project rules", installed)
        self.assertIn(BEGIN_MARKER, installed)
        self.assertIn(END_MARKER, installed)

        second = install_adapter("codex", self.project, root=ROOT)
        self.assertEqual(second["conflicts"], [])
        self.assertEqual(instructions.read_text(encoding="utf-8"), installed)
        self.assertEqual(installed.count(BEGIN_MARKER), 1)
        self.assertTrue((self.project / ".codex/agents/backend-agent.toml").is_file())

    def test_installer_does_not_overwrite_unmanaged_agent_file(self):
        agent_path = self.project / ".codex/agents/backend-agent.toml"
        agent_path.parent.mkdir(parents=True)
        agent_path.write_text("# user-owned agent\n", encoding="utf-8")

        result = install_adapter("codex", self.project, root=ROOT)
        self.assertTrue(any(".codex/agents/backend-agent.toml" in item for item in result["conflicts"]))
        self.assertEqual(agent_path.read_text(encoding="utf-8"), "# user-owned agent\n")

    def test_uninstall_removes_only_managed_content(self):
        instructions = self.project / "CLAUDE.md"
        instructions.write_text("# Local Claude instructions\n", encoding="utf-8")
        install_adapter("claude-code", self.project, root=ROOT)

        result = install_adapter("claude-code", self.project, root=ROOT, uninstall=True)
        self.assertEqual(result["conflicts"], [])
        self.assertIn("# Local Claude instructions", instructions.read_text(encoding="utf-8"))
        self.assertNotIn(BEGIN_MARKER, instructions.read_text(encoding="utf-8"))
        self.assertFalse((self.project / ".claude/agents/backend-agent.md").exists())
        self.assertFalse((self.project / ".agent-ecosystem/adapters/claude-code.json").exists())

    def test_uninstall_restores_original_instruction_bytes_and_line_endings(self):
        instructions = self.project / ".github/copilot-instructions.md"
        original = b"# Existing Copilot instructions\r\nPreserve trailing spaces and no final newline. "
        instructions.parent.mkdir(parents=True)
        instructions.write_bytes(original)

        install_adapter("copilot", self.project, root=ROOT)
        result = install_adapter("copilot", self.project, root=ROOT, uninstall=True)

        self.assertEqual(result["conflicts"], [])
        self.assertEqual(instructions.read_bytes(), original)

    def test_all_runtime_adapters_can_coexist_in_one_project(self):
        for adapter in ADAPTERS:
            result = install_adapter(adapter, self.project, root=ROOT)
            self.assertEqual(result["conflicts"], [], msg=f"{adapter}: {result['conflicts']}")

        self.assertTrue((self.project / ".agents/skills/capability-smoke-test/SKILL.md").is_file())
        self.assertTrue((self.project / ".github/skills/capability-smoke-test/SKILL.md").is_file())
        self.assertTrue((self.project / ".claude/skills/capability-smoke-test/SKILL.md").is_file())
        self.assertTrue((self.project / ".cursor/skills/capability-smoke-test/SKILL.md").is_file())
        self.assertTrue((self.project / ".cursor/agents/backend-agent.md").is_file())
        self.assertTrue((self.project / ".cursor/rules/ai-agent-ecosystem.mdc").is_file())

        uninstall_adapter = install_adapter("codex", self.project, root=ROOT, uninstall=True)
        self.assertEqual(uninstall_adapter["conflicts"], [])
        self.assertFalse((self.project / ".agents/skills/capability-smoke-test/SKILL.md").exists())
        self.assertTrue((self.project / ".github/skills/capability-smoke-test/SKILL.md").is_file())
        self.assertTrue((self.project / ".claude/skills/capability-smoke-test/SKILL.md").is_file())
        self.assertTrue((self.project / ".cursor/skills/capability-smoke-test/SKILL.md").is_file())
        self.assertTrue((self.project / ".cursor/rules/ai-agent-ecosystem.mdc").is_file())

    def test_cursor_uninstall_removes_only_its_owned_rule_and_profiles(self):
        install_adapter("cursor", self.project, root=ROOT)
        rule = self.project / ".cursor/rules/ai-agent-ecosystem.mdc"
        self.assertTrue(rule.is_file())
        self.assertNotIn(BEGIN_MARKER, rule.read_text(encoding="utf-8"))
        result = install_adapter("cursor", self.project, root=ROOT, uninstall=True)
        self.assertEqual(result["conflicts"], [])
        self.assertFalse(rule.exists())
        self.assertFalse((self.project / ".cursor/agents/backend-agent.md").exists())
        self.assertFalse((self.project / ".cursor/skills/capability-smoke-test/SKILL.md").exists())

    def test_cursor_existing_rule_collision_is_preserved(self):
        rule = self.project / ".cursor/rules/ai-agent-ecosystem.mdc"
        rule.parent.mkdir(parents=True)
        original = "---\\ndescription: User-owned Cursor rule\\nalwaysApply: true\\n---\\nKeep my instructions.\\n"
        rule.write_text(original, encoding="utf-8")
        result = install_adapter("cursor", self.project, root=ROOT)
        self.assertTrue(any(".cursor/rules/ai-agent-ecosystem.mdc" in item for item in result["conflicts"]))
        self.assertEqual(rule.read_text(encoding="utf-8"), original)
        uninstall = install_adapter("cursor", self.project, root=ROOT, uninstall=True)
        self.assertEqual(uninstall["conflicts"], [])
        self.assertEqual(rule.read_text(encoding="utf-8"), original)

    def test_install_cli_supports_all_adapters_and_uninstall(self):
        script = ROOT / "scripts/install_adapter.py"
        install = subprocess.run(
            [sys.executable, str(script), "--adapter", "all", "--target", str(self.project)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(install.returncode, 0, msg=install.stdout + install.stderr)
        for adapter in ADAPTERS:
            self.assertTrue((self.project / f".agent-ecosystem/adapters/{adapter}.json").is_file())

        uninstall = subprocess.run(
            [sys.executable, str(script), "--adapter", "all", "--target", str(self.project), "--uninstall"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(uninstall.returncode, 0, msg=uninstall.stdout + uninstall.stderr)
        for adapter in ADAPTERS:
            self.assertFalse((self.project / f".agent-ecosystem/adapters/{adapter}.json").exists())

    def test_parent_file_collision_fails_before_any_project_write(self):
        blocked = self.project / ".codex"
        blocked.write_text("user-owned file", encoding="utf-8")
        with self.assertRaises(ValueError):
            install_adapter("codex", self.project, root=ROOT)
        self.assertFalse((self.project / "AGENTS.md").exists())
        self.assertFalse((self.project / ".agents").exists())
        self.assertEqual(blocked.read_text(encoding="utf-8"), "user-owned file")

    def test_dry_run_does_not_create_project_files(self):
        result = install_adapter("copilot", self.project, root=ROOT, dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertFalse((self.project / ".github").exists())
        self.assertFalse((self.project / ".agent-ecosystem").exists())


if __name__ == "__main__":
    unittest.main()
