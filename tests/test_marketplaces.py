"""Regression tests for the single root-shared Codex, Claude Code, and Cursor marketplaces."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_single_plugin import build as build_root_bundle
from validate_marketplaces import validate as validate_marketplaces


class RootSharedMarketplaceTests(unittest.TestCase):
    def test_all_marketplace_manifests_validate_against_root_bundle(self):
        self.assertEqual(validate_marketplaces(ROOT), [])

    def test_root_bundle_has_seven_agents_nineteen_skills_and_constitution_rule(self):
        agents = sorted((ROOT / "agents").glob("*.md"))
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(agents), 7)
        self.assertEqual(len(skills), 19)
        self.assertTrue((ROOT / "rules/ai-agent-constitution.mdc").is_file())

    def test_build_single_plugin_generates_the_shared_root_layout(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build_root_bundle(output)
            self.assertEqual(len(list((output / "agents").glob("*.md"))), 7)
            self.assertEqual(len(list((output / "skills").glob("*/SKILL.md"))), 19)
            self.assertTrue((output / "rules/AGENTS.md").is_file())
            rule = output / "rules/ai-agent-constitution.mdc"
            self.assertTrue(rule.is_file())
            self.assertIn("alwaysApply: true", rule.read_text(encoding="utf-8"))

    def test_claude_plugin_directory_contains_metadata_only(self):
        directory = ROOT / ".claude-plugin"
        self.assertEqual(
            {path.name for path in directory.iterdir()},
            {"plugin.json", "marketplace.json"},
        )
        self.assertFalse((directory / "agents").exists())
        self.assertFalse((directory / "skills").exists())
        self.assertFalse((directory / "rules").exists())

    def test_cursor_plugin_directory_contains_metadata_only(self):
        directory = ROOT / ".cursor-plugin"
        self.assertEqual(
            {path.name for path in directory.iterdir()},
            {"plugin.json", "marketplace.json"},
        )

    def test_codex_plugin_directory_contains_only_manifest(self):
        directory = ROOT / ".codex-plugin"
        self.assertEqual({path.name for path in directory.iterdir()}, {"plugin.json"})

    def test_all_plugin_manifests_resolve_components_from_repository_root(self):
        cases = [
            (".claude-plugin/plugin.json", ("agents", "skills", "rules")),
            (".cursor-plugin/plugin.json", ("agents", "skills", "rules")),
            (".codex-plugin/plugin.json", ("agents", "skills")),
        ]
        for path, components in cases:
            manifest = json.loads((ROOT / path).read_text(encoding="utf-8"))
            for component in components:
                self.assertEqual(manifest[component], f"./{component}/")

    def test_marketplace_sources_point_to_the_root_plugin(self):
        for path in (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json"):
            manifest = json.loads((ROOT / path).read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["plugins"]), 1)
            self.assertEqual(manifest["plugins"][0]["source"], "./")
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["plugins"][0]["source"], {"source": "local", "path": "."})

    def test_nested_duplicate_packages_are_absent(self):
        self.assertFalse((ROOT / "plugins/ai-agent").exists())
        self.assertFalse((ROOT / "plugins/ai-agent-ecosystem").exists())
        for metadata in (".claude-plugin", ".cursor-plugin", ".codex-plugin"):
            for component in ("agents", "skills", "rules"):
                self.assertFalse((ROOT / metadata / component).exists())

    def test_codex_manifest_declares_root_agents_and_skills(self):
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["agents"], "./agents/")
        self.assertEqual(manifest["skills"], "./skills/")


if __name__ == "__main__":
    unittest.main()
