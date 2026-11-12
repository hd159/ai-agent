"""Regression tests for Codex and Cursor native plugin marketplaces."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_marketplace_components import MARKER, build_cursor_components
from validate_marketplaces import validate as validate_marketplaces


class MarketplaceBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / "plugin"

    def test_builds_cursor_agents_rule_and_shared_skills(self):
        errors = build_cursor_components(ROOT, self.output)
        self.assertEqual(errors, [])
        agents = sorted((self.output / "agents").glob("*.md"))
        skills = sorted((self.output / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(agents), 7)
        self.assertEqual(len(skills), 19)
        self.assertTrue((self.output / "rules/ai-agent-ecosystem.mdc").is_file())
        marker = json.loads((self.output / MARKER).read_text(encoding="utf-8"))
        self.assertEqual(len(marker["agents"]), 7)
        self.assertEqual(len(marker["skills"]), 19)

    def test_build_is_deterministic_and_check_detects_stale_output(self):
        self.assertEqual(build_cursor_components(ROOT, self.output), [])
        self.assertEqual(build_cursor_components(ROOT, self.output, check=True), [])
        agent = self.output / "agents/backend-agent.md"
        agent.write_text("tampered", encoding="utf-8")
        errors = build_cursor_components(ROOT, self.output, check=True)
        self.assertTrue(any("agents/backend-agent.md" in error for error in errors))

    def test_builder_refuses_unmanaged_directory_without_deleting_user_files(self):
        self.output.mkdir()
        keep = self.output / "user-owned.txt"
        keep.write_text("preserve", encoding="utf-8")
        errors = build_cursor_components(ROOT, self.output)
        self.assertTrue(any("unmanaged directory" in error for error in errors))
        self.assertEqual(keep.read_text(encoding="utf-8"), "preserve")

    def test_marketplace_manifest_and_package_contracts_validate(self):
        self.assertEqual(validate_marketplaces(ROOT), [])

    def test_codex_plugin_does_not_claim_unsupported_agent_or_rule_components(self):
        manifest = json.loads(
            (ROOT / "plugins/ai-agent-ecosystem/.codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("agents", manifest)
        self.assertNotIn("rules", manifest)

    def test_cursor_plugin_manifest_exposes_agents_rules_and_skills(self):
        manifest = json.loads(
            (ROOT / "plugins/ai-agent-ecosystem/.cursor-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["agents"], "./agents/")
        self.assertEqual(manifest["rules"], "./rules/")
        self.assertEqual(manifest["skills"], "./skills/")


if __name__ == "__main__":
    unittest.main()
