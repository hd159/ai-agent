"""Regression checks for every bundled agent, skill, and inherited capability."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_capabilities import audit


class CapabilityAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for folder in ("modules", "agents", "skills", "rules"):
            shutil.copytree(ROOT / folder, self.root / folder)
        (self.root / "contracts").mkdir()
        for file in ("plugin.json", "ecosystem.json"):
            shutil.copy2(ROOT / file, self.root / file)
        shutil.copy2(ROOT / "contracts/agent-tool-policy.json", self.root / "contracts/agent-tool-policy.json")

    def errors(self):
        return audit(self.root)[0]

    def update_agent(self, modification):
        path = self.root / "modules/team-orchestrator/agents/team-orchestrator.md"
        content = path.read_text(encoding="utf-8")
        path.write_text(modification(content), encoding="utf-8")

    def test_current_bundle_passes(self):
        errors, stats = audit(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(stats["agents"], 7)
        self.assertEqual(stats["skills"], 19)
        self.assertEqual(stats["rules"], 1)

    def test_forbids_tools_allowlist(self):
        self.update_agent(lambda s: s.replace("inheritMcp: true", "tools: []\ninheritMcp: true"))
        self.assertTrue(any("tools" in e for e in self.errors()))

    def test_missing_mcp_inheritance(self):
        self.update_agent(lambda s: s.replace("inheritMcp: true", "inheritMcp: false"))
        self.assertTrue(any("inheritMcp" in e for e in self.errors()))

    def test_missing_customizations_inheritance(self):
        self.update_agent(lambda s: s.replace("inheritCustomizations: true", "inheritCustomizations: false"))
        self.assertTrue(any("inheritCustomizations" in e for e in self.errors()))

    def test_denies_per_agent_skill_restrictions(self):
        self.update_agent(lambda s: s.replace("inheritMcp: true", "skills: []\ninheritMcp: true"))
        self.assertTrue(any("skills" in e for e in self.errors()))

    def test_missing_bundle_skill(self):
        (self.root / "skills/capability-smoke-test/SKILL.md").unlink()
        self.assertTrue(any("capability-smoke-test" in e for e in self.errors()))

    def test_bad_skill_metadata(self):
        path = self.root / "modules/core-engineering-skills/skills/capability-smoke-test/SKILL.md"
        path.write_text(path.read_text().replace("name: capability-smoke-test", "name: other"), encoding="utf-8")
        self.assertTrue(any("invalid name/description" in e for e in self.errors()))

    def test_cannot_ship_plugin_disabled(self):
        path = self.root / "plugin.json"
        obj = json.loads(path.read_text())
        obj["disabled"] = True
        path.write_text(json.dumps(obj))
        self.assertTrue(any("disabled" in e for e in self.errors()))

    def test_mismatched_catalog_counts(self):
        path = self.root / "ecosystem.json"
        obj = json.loads(path.read_text())
        obj["modules"][3]["components"]["skills"] = 0
        path.write_text(json.dumps(obj))
        self.assertTrue(any("catalog skills" in e for e in self.errors()))

    def test_invalid_yaml_fails(self):
        self.update_agent(lambda s: s.replace("inheritMcp: true", "inheritMcp: ["))
        self.assertTrue(any("expected" in e or "YAML" in e for e in self.errors()))

    def test_duplicate_yaml_keys_fail(self):
        self.update_agent(lambda s: s.replace("inheritMcp: true", "inheritMcp: true\ninheritMcp: true"))
        self.assertTrue(any("duplicate YAML key" in e for e in self.errors()))

    def test_missing_shared_rule(self):
        (self.root / "rules/AGENTS.md").unlink()
        self.assertTrue(any("always-on" in e for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
