"""Regression tests for discovery gates, architecture decision quality, and orchestration safety."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"

HARD_GATE_TEXT = (
    "Do NOT write application code, scaffold implementation files, or dispatch "
    "implementation tasks until the discovery/MVP scope design has been presented "
    "and explicitly approved by the user. This applies regardless of perceived "
    "task simplicity (Anti-Pattern: This Is Too Simple To Need A Design)."
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def frontmatter(content: str) -> dict[str, str]:
    if not content.startswith("---\n"):
        raise AssertionError("missing YAML frontmatter")
    end = content.find("\n---", 4)
    if end < 0:
        raise AssertionError("unterminated YAML frontmatter")
    result = {}
    for line in content[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip("\\\"'")
    return result


class DiscoveryArchitectureTests(unittest.TestCase):
    def test_product_discovery_has_hard_gate_decomposition_and_interview_rules(self):
        content = read("modules/core-engineering-skills/skills/product-discovery/SKILL.md")
        self.assertIn("<HARD-GATE>", content)
        self.assertIn(HARD_GATE_TEXT, content)
        self.assertIn("## Step 0 — Sub-Project Decomposition Check", content)
        self.assertIn("multiple independent subsystems", content)
        self.assertIn("at most ONE question per message", content)
        self.assertIn("2–3 concrete approaches", content)
        self.assertIn("explicit trade-offs", content)
        self.assertIn("clear recommendation", content)

    def test_mvp_scoping_has_hard_gate_decomposition_and_interview_rules(self):
        content = read("modules/core-engineering-skills/skills/mvp-scoping/SKILL.md")
        self.assertIn("<HARD-GATE>", content)
        self.assertIn(HARD_GATE_TEXT, content)
        self.assertIn("Sub-Project Decomposition Check", content)
        self.assertIn("multiple independent subsystems", content)
        self.assertIn("at most ONE question per message", content)
        self.assertIn("2–3 concrete approaches", content)
        self.assertIn("explicit user approval", content)

    def test_team_orchestrator_enforces_discovery_approval_and_fresh_context(self):
        content = read("modules/team-orchestrator/agents/team-orchestrator.md")
        self.assertIn(HARD_GATE_TEXT, content)
        self.assertIn("Step 0 — Sub-Project Decomposition Check", content)
        self.assertIn("at most **ONE question per message**", content)
        self.assertIn("2–3 concrete approaches", content)
        self.assertIn(
            "Start delegated subagents with a fresh context window containing only "
            "the bounded task contract and required project context, never an "
            "unfiltered parent conversation fork.",
            content,
        )

    def test_architecture_agent_enforces_three_gate_adr_filter(self):
        content = read("modules/architecture-agent/agents/architecture-agent.md")
        self.assertIn("3-Gate ADR Filter", content)
        self.assertIn("**Reversibility:**", content)
        self.assertIn("**Surprise:**", content)
        self.assertIn("**Trade-off:**", content)
        self.assertIn(
            "If any of the three gates is missing, skip creating a standalone ADR "
            "file and record a concise note in `PROJECT_CONTEXT.md` instead.",
            content,
        )

    def test_architecture_skill_and_project_memory_share_adr_filter(self):
        for relative in (
            "modules/core-engineering-skills/skills/system-architecture/SKILL.md",
            "modules/team-orchestrator/skills/project-memory/SKILL.md",
            "docs/architecture/PERSISTENT-PROJECT-MEMORY.md",
        ):
            content = read(relative)
            self.assertIn("3-Gate ADR Filter", content, relative)
            for gate in ("Reversibility", "Surprise", "Trade-off"):
                self.assertIn(gate, content, relative)
            self.assertIn("PROJECT_CONTEXT.md", content, relative)

    def test_product_and_architecture_capture_ubiquitous_language_inline(self):
        for relative in (
            "modules/core-engineering-skills/skills/product-discovery/SKILL.md",
            "modules/architecture-agent/agents/architecture-agent.md",
            "modules/team-orchestrator/agents/team-orchestrator.md",
        ):
            content = read(relative)
            self.assertIn("PROJECT_CONTEXT.md", content, relative)
            self.assertIn("canonical", content.lower(), relative)
        product = read("modules/core-engineering-skills/skills/product-discovery/SKILL.md")
        self.assertIn("UI labels", product)
        self.assertIn("API request/response fields", product)
        self.assertIn("database schemas", product)

    def test_high_level_orchestration_skills_require_explicit_invocation(self):
        paths = (
            "modules/team-orchestrator/skills/compose-team/SKILL.md",
            "modules/team-orchestrator/skills/create-task-graph/SKILL.md",
            "modules/core-engineering-skills/skills/capability-smoke-test/SKILL.md",
            "modules/team-orchestrator/skills/session-checkpoint/SKILL.md",
        )
        for relative in paths:
            fm = frontmatter(read(relative))
            self.assertEqual(fm.get("disable-model-invocation"), "true", relative)

    def test_optional_disable_model_invocation_is_validated_as_boolean(self):
        repo_validator = read("scripts/validate_repo.py")
        plugin_validator = read("scripts/validate_plugin.py")
        self.assertIn("disable-model-invocation", repo_validator)
        self.assertIn("disable-model-invocation must be true or false", repo_validator)
        self.assertIn("disable-model-invocation", plugin_validator)
        self.assertIn("disable-model-invocation must be true or false", plugin_validator)

    def test_constitution_requires_fresh_context_for_delegated_subagents(self):
        content = read("modules/agent-constitution/rules/AGENTS.md")
        self.assertIn(
            "Start delegated subagents with a fresh context window containing only "
            "the bounded task contract and required project context, never an "
            "unfiltered parent conversation fork.",
            content,
        )


if __name__ == "__main__":
    unittest.main()
