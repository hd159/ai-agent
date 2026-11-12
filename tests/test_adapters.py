"""Cross-platform build and safe-install tests for native runtime adapters."""
from __future__ import annotations

import json
import shutil
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

    def test_dry_run_does_not_create_project_files(self):
        result = install_adapter("copilot", self.project, root=ROOT, dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertFalse((self.project / ".github").exists())
        self.assertFalse((self.project / ".agent-ecosystem").exists())


if __name__ == "__main__":
    unittest.main()
