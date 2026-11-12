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
        self.assertIn("actual host tools available", skill.lower())

    def test_orchestrator_requires_preflight_before_dispatch(self):
        source = (ROOT / "modules/team-orchestrator/agents/team-orchestrator.md").read_text()
        generated = (ROOT / "agents/team-orchestrator.md").read_text()
        self.assertEqual(source, generated)
        self.assertIn("Mandatory runtime capability preflight", source)
        self.assertIn("Do not dispatch or start dependent implementation", source)
        self.assertIn("framework can grant permissions", source)
        self.assertIn("Execution policy — no planning-only fallback", source)
        self.assertNotIn("Mode B — Native delegation unavailable", source)
        self.assertIn("Do not switch to a planning-only mode", source)
        self.assertIn("only when the user explicitly asks", source)
        self.assertNotIn("within its role", (ROOT / "docs/ORCHESTRATION-WORKFLOW.md").read_text())
        self.assertNotIn("within its role", (ROOT / "docs/architecture/ORCHESTRATION-SPEC.md").read_text())
        self.assertIn("absorbing the necessary specialist execution responsibilities", (ROOT / "docs/ORCHESTRATION-WORKFLOW.md").read_text())
        readme = (ROOT / "README.md").read_text()
        self.assertNotIn("otherwise it prepares dispatch-ready task contracts", readme)
        self.assertIn("does not automatically replace implementation with task contracts", readme)

    def test_constitution_requires_runtime_evidence(self):
        source = (ROOT / "modules/agent-constitution/rules/AGENTS.md").read_text()
        generated = (ROOT / "rules/AGENTS.md").read_text()
        self.assertEqual(source, generated)
        self.assertIn("Capability preflight is mandatory", source)
        self.assertIn("available_verified", source)


    def test_task_graph_is_not_an_automatic_fallback(self):
        skill = (ROOT / "modules/team-orchestrator/skills/create-task-graph/SKILL.md").read_text()
        self.assertIn("Never invoke it as a fallback", skill)
        self.assertIn("user explicitly requests", skill)


if __name__ == "__main__":
    unittest.main()
