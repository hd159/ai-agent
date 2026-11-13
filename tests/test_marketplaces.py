"""Regression tests for one root-shared marketplace bundle across all runtimes."""
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

    def test_root_bundle_has_seven_agents_nineteen_skills_and_shared_rules(self):
        self.assertEqual(len(list((ROOT / "agents").glob("*.md"))), 7)
        self.assertEqual(len(list((ROOT / "skills").glob("*/SKILL.md"))), 19)
        self.assertTrue((ROOT / "rules/AGENTS.md").is_file())
        self.assertTrue((ROOT / "rules/ai-agent-constitution.mdc").is_file())

    def test_builder_generates_only_one_agents_and_skills_directory_at_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build_root_bundle(output)

            self.assertEqual(len(list((output / "agents").glob("*.md"))), 7)
            self.assertEqual(len(list((output / "skills").glob("*/SKILL.md"))), 19)
            self.assertEqual(
                [path.relative_to(output) for path in output.rglob("agents") if path.is_dir()],
                [Path("agents")],
            )
            self.assertEqual(
                [path.relative_to(output) for path in output.rglob("skills") if path.is_dir()],
                [Path("skills")],
            )
            self.assertFalse((output / "plugins").exists())
            self.assertFalse((output / ".agents").exists())

            codex_manifest = json.loads(
                (output / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual(codex_manifest["name"], "ai-agent-ecosystem")
            self.assertEqual(codex_manifest["agents"], "./agents/")
            self.assertEqual(codex_manifest["skills"], "./skills/")

    def test_no_codex_or_marketplace_component_mirror_exists(self):
        self.assertFalse((ROOT / "plugins").exists())
        self.assertFalse((ROOT / ".agents").exists())
        self.assertFalse((ROOT / "plugins/ai-agent/skills").exists())
        self.assertFalse((ROOT / "plugins/ai-agent/.codex-plugin").exists())

    def test_claude_cursor_and_codex_metadata_directories_are_manifest_only(self):
        expected = {
            ".claude-plugin": {"plugin.json", "marketplace.json"},
            ".cursor-plugin": {"plugin.json", "marketplace.json"},
            ".codex-plugin": {"plugin.json"},
        }
        for relative, expected_files in expected.items():
            directory = ROOT / relative
            self.assertEqual(
                {path.name for path in directory.iterdir()},
                expected_files,
            )
            self.assertFalse(any(path.is_dir() for path in directory.iterdir()))

    def test_claude_copilot_and_codex_manifests_resolve_from_root(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(claude["agents"], "./agents/")
        self.assertEqual(claude["skills"], "./skills/")

        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["agents"], "./agents/")
        self.assertEqual(codex["skills"], "./skills/")

    def test_cursor_manifest_resolves_all_root_components(self):
        cursor = json.loads((ROOT / ".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
        for component in ("agents", "skills", "rules"):
            self.assertEqual(cursor[component], f"./{component}/")

    def test_claude_and_cursor_marketplaces_use_root_source(self):
        for path in (".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json"):
            marketplace = json.loads((ROOT / path).read_text(encoding="utf-8"))
            self.assertEqual(len(marketplace["plugins"]), 1)
            self.assertEqual(marketplace["plugins"][0]["name"], "ai-agent-ecosystem")
            self.assertEqual(marketplace["plugins"][0]["source"], "./")

    def test_codex_reuses_claude_marketplace_catalog(self):
        # Current Codex core-plugins scans .claude-plugin/marketplace.json and
        # resolves source './' relative to the repository root.
        self.assertTrue((ROOT / ".claude-plugin/marketplace.json").is_file())
        self.assertFalse((ROOT / ".agents/plugins/marketplace.json").exists())
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(marketplace["plugins"][0]["source"], "./")

    def test_root_generated_files_match_canonical_module_sources(self):
        for source in (ROOT / "modules").glob("*/agents/*.md"):
            self.assertEqual(
                source.read_bytes(),
                (ROOT / "agents" / source.name).read_bytes(),
            )
        for source in (ROOT / "modules").glob("*/skills/*/SKILL.md"):
            self.assertEqual(
                source.read_bytes(),
                (ROOT / "skills" / source.parent.name / "SKILL.md").read_bytes(),
            )
        source_rule = ROOT / "modules/agent-constitution/rules/AGENTS.md"
        self.assertEqual(source_rule.read_bytes(), (ROOT / "rules/AGENTS.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
