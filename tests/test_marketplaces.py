"""Regression tests for the root-shared plugin bundle and Codex's minimal package exception."""
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
    def test_all_marketplace_manifests_validate(self):
        self.assertEqual(validate_marketplaces(ROOT), [])

    def test_root_bundle_has_seven_agents_nineteen_skills_and_constitution_rule(self):
        self.assertEqual(len(list((ROOT / "agents").glob("*.md"))), 7)
        self.assertEqual(len(list((ROOT / "skills").glob("*/SKILL.md"))), 19)
        self.assertTrue((ROOT / "rules/ai-agent-constitution.mdc").is_file())
        self.assertTrue((ROOT / "rules/AGENTS.md").is_file())

    def test_builder_generates_root_bundle_and_minimal_codex_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build_root_bundle(output)
            self.assertEqual(len(list((output / "agents").glob("*.md"))), 7)
            self.assertEqual(len(list((output / "skills").glob("*/SKILL.md"))), 19)
            self.assertTrue((output / "rules/AGENTS.md").is_file())
            self.assertTrue((output / "rules/ai-agent-constitution.mdc").is_file())
            self.assertEqual(
                len(list((output / "plugins/ai-agent/skills").glob("*/SKILL.md"))),
                19,
            )
            codex_manifest = json.loads(
                (output / "plugins/ai-agent/.codex-plugin/plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual(codex_manifest["name"], "ai-agent")
            self.assertEqual(codex_manifest["skills"], "./skills/")
            self.assertNotIn("agents", codex_manifest)
            self.assertNotIn("rules", codex_manifest)

    def test_claude_plugin_directory_contains_metadata_only(self):
        directory = ROOT / ".claude-plugin"
        self.assertEqual({path.name for path in directory.iterdir()}, {"plugin.json", "marketplace.json"})
        for component in ("agents", "skills", "rules"):
            self.assertFalse((directory / component).exists())

    def test_cursor_plugin_directory_contains_metadata_only(self):
        directory = ROOT / ".cursor-plugin"
        self.assertEqual({path.name for path in directory.iterdir()}, {"plugin.json", "marketplace.json"})
        for component in ("agents", "skills", "rules"):
            self.assertFalse((directory / component).exists())

    def test_claude_and_cursor_manifests_resolve_from_repository_root(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(claude["agents"], "./agents/")
        self.assertEqual(claude["skills"], "./skills/")
        self.assertNotIn("rules", claude)

        cursor = json.loads((ROOT / ".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
        for component in ("agents", "skills", "rules"):
            self.assertEqual(cursor[component], f"./{component}/")

    def test_claude_and_cursor_marketplaces_use_root_source(self):
        for path in (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json"):
            manifest = json.loads((ROOT / path).read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["plugins"]), 1)
            self.assertEqual(manifest["plugins"][0]["source"], "./")

    def test_codex_uses_only_the_required_subdirectory_package(self):
        self.assertFalse((ROOT / ".codex-plugin").exists())
        package = ROOT / "plugins/ai-agent"
        self.assertEqual({path.name for path in package.iterdir()}, {".codex-plugin", "skills"})
        self.assertFalse((package / "agents").exists())
        self.assertFalse((package / "rules").exists())
        manifest = json.loads((package / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "ai-agent")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("agents", manifest)
        self.assertNotIn("rules", manifest)
        self.assertEqual(len(list((package / "skills").glob("*/SKILL.md"))), 19)

    def test_marketplace_sources_resolve_correctly(self):
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["plugins"][0]["name"], "ai-agent")
        self.assertEqual(
            codex["plugins"][0]["source"],
            {"source": "local", "path": "./plugins/ai-agent"},
        )

    def test_codex_skill_mirror_matches_root_without_agent_or_rule_copies(self):
        root_skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        codex_root = ROOT / "plugins/ai-agent"
        codex_skills = sorted((codex_root / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(codex_skills), len(root_skills))
        for source in root_skills:
            target = codex_root / "skills" / source.parent.name / "SKILL.md"
            self.assertEqual(source.read_bytes(), target.read_bytes())

    def test_no_legacy_nested_package_or_hidden_component_copies(self):
        self.assertFalse((ROOT / "plugins/ai-agent-ecosystem").exists())
        for metadata in (".claude-plugin", ".cursor-plugin"):
            for component in ("agents", "skills", "rules"):
                self.assertFalse((ROOT / metadata / component).exists())


if __name__ == "__main__":
    unittest.main()
