from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RuntimePreflightContractTests(unittest.TestCase):
    def test_capability_skill_defines_fail_closed_states(self):
        skill = (ROOT / "modules/core-engineering-skills/skills/capability-smoke-test/SKILL.md").read_text()
        for state in (
            "available_verified", "exposed_but_denied", "not_exposed",
            "not_configured", "not_required", "not_tested",
        ):
            self.assertIn(state, skill)
        self.assertIn("do not dispatch", skill.lower())
        self.assertIn("real host tools", skill.lower())

    def test_orchestrator_requires_preflight_before_dispatch(self):
        source = (ROOT / "modules/team-orchestrator/agents/team-orchestrator.md").read_text()
        generated = (ROOT / "agents/team-orchestrator.md").read_text()
        self.assertEqual(source, generated)
        self.assertIn("Mandatory runtime capability preflight", source)
        self.assertIn("Do not dispatch or start dependent implementation", source)
        self.assertIn("framework can grant permissions", source)

    def test_constitution_requires_runtime_evidence(self):
        source = (ROOT / "modules/agent-constitution/rules/AGENTS.md").read_text()
        generated = (ROOT / "rules/AGENTS.md").read_text()
        self.assertEqual(source, generated)
        self.assertIn("Capability preflight is mandatory", source)
        self.assertIn("available_verified", source)


if __name__ == "__main__":
    unittest.main()
