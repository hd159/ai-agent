#!/usr/bin/env python3
"""Validate native Codex and Cursor marketplace manifests and package contents."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "plugins/ai-agent-ecosystem"


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    def load(relative: str) -> dict:
        path = root / relative
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("top-level JSON value must be an object")
            return value
        except Exception as exc:
            errors.append(f"{relative}: {exc}")
            return {}

    codex_market = load(".agents/plugins/marketplace.json")
    codex_plugin = load(f"{PACKAGE}/.codex-plugin/plugin.json")
    cursor_market = load(".cursor-plugin/marketplace.json")
    cursor_plugin = load(f"{PACKAGE}/.cursor-plugin/plugin.json")
    catalog = load("ecosystem.json")
    expected_version = catalog.get("version")

    codex_entries = codex_market.get("plugins", [])
    if codex_market.get("name") != "ai-agent-ecosystem" or len(codex_entries) != 1:
        errors.append("Codex marketplace must expose exactly one ai-agent-ecosystem plugin")
    else:
        entry = codex_entries[0]
        source = entry.get("source", {})
        if entry.get("name") != "ai-agent-ecosystem":
            errors.append("Codex marketplace plugin name mismatch")
        if source.get("source") != "local" or source.get("path") != f"./{PACKAGE}":
            errors.append("Codex marketplace must reference the nested local package relative to the repository root")
        policy = entry.get("policy", {})
        if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
            errors.append("Codex marketplace installation/authentication policy mismatch")
        if entry.get("category") != "Developer Tools":
            errors.append("Codex marketplace category mismatch")

    if codex_plugin.get("name") != "ai-agent-ecosystem":
        errors.append("Codex plugin identity mismatch")
    if codex_plugin.get("version") != expected_version:
        errors.append("Codex plugin version does not match ecosystem.json")
    if codex_plugin.get("skills") != "./skills/":
        errors.append("Codex plugin must package skills from ./skills/")
    if not (root / PACKAGE / "skills").is_dir():
        errors.append("Codex plugin skills directory is missing")
    codex_interface = codex_plugin.get("interface", {})
    if codex_interface.get("displayName") != "AI Agent Ecosystem":
        errors.append("Codex plugin interface displayName mismatch")

    cursor_entries = cursor_market.get("plugins", [])
    if cursor_market.get("name") != "ai-agent-ecosystem" or len(cursor_entries) != 1:
        errors.append("Cursor marketplace must expose exactly one ai-agent-ecosystem plugin")
    else:
        entry = cursor_entries[0]
        if entry.get("name") != "ai-agent-ecosystem" or entry.get("source") != PACKAGE:
            errors.append("Cursor marketplace must point to the nested native Cursor plugin")
        if entry.get("version") != expected_version:
            errors.append("Cursor marketplace entry version mismatch")
    if not cursor_market.get("owner", {}).get("name"):
        errors.append("Cursor marketplace owner.name is required")

    if cursor_plugin.get("name") != "ai-agent-ecosystem":
        errors.append("Cursor plugin identity mismatch")
    if cursor_plugin.get("version") != expected_version:
        errors.append("Cursor plugin version does not match ecosystem.json")
    for key in ("agents", "rules", "skills"):
        if cursor_plugin.get(key) != f"./{key}/":
            errors.append(f"Cursor plugin {key} path must be ./{key}/")

    package_root = root / PACKAGE
    agent_dir = package_root / "agents"
    agent_files = sorted(agent_dir.glob("*.md")) if agent_dir.is_dir() else []
    expected_agents = set(load("contracts/agent-tool-policy.json").get("agents", []))
    actual_agents = {path.stem for path in agent_files}
    if actual_agents != expected_agents:
        errors.append(f"Cursor plugin agent inventory mismatch: expected={sorted(expected_agents)}, actual={sorted(actual_agents)}")
    for path in agent_files:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n") or "\n---" not in content[4:]:
            errors.append(f"{path.relative_to(root)}: invalid Cursor agent frontmatter")
        else:
            frontmatter = content.split("\n---", 1)[0]
            if f"name: {path.stem}" not in frontmatter or "description:" not in frontmatter:
                errors.append(f"{path.relative_to(root)}: missing native Cursor name/description")
        for forbidden in ("commandExecutionPolicy:", "inheritCustomizations:", "tools:\n  - read_file"):
            if forbidden in content:
                errors.append(f"{path.relative_to(root)}: Antigravity-only metadata leaked into Cursor plugin")

    rule = package_root / "rules" / "ai-agent-ecosystem.mdc"
    if not rule.is_file():
        errors.append("Cursor plugin always-applied rule is missing")
    else:
        content = rule.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            errors.append("Cursor plugin rule must begin with MDC frontmatter")
        if "alwaysApply: true" not in content:
            errors.append("Cursor plugin rule must set alwaysApply: true")
        if "Universal Agent Constitution" not in content or "capability-smoke-test" not in content:
            errors.append("Cursor plugin rule is missing shared constitution or capability preflight guidance")

    skills = sorted((root / "modules").glob("*/skills/*/SKILL.md"))
    expected_skills = {path.parent.name for path in skills}
    actual_skills = {
        path.parent.name for path in (package_root / "skills").glob("*/SKILL.md")
    } if (package_root / "skills").is_dir() else set()
    if actual_skills != expected_skills:
        errors.append(f"Marketplace skill inventory mismatch: expected={sorted(expected_skills)}, actual={sorted(actual_skills)}")
    for source in skills:
        target = package_root / "skills" / source.parent.name / "SKILL.md"
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            errors.append(f"Marketplace skill payload differs from canonical source: {source.parent.name}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("MARKETPLACE VALIDATION FAILED")
        for error in errors:
            print("ERROR:", error)
        return 1
    print("MARKETPLACE VALIDATION PASSED: Codex and Cursor manifests, 7 Cursor agents, 1 rule, and 19 shared skills")
    print("Codex plugin packages skills only; use the Codex native adapter installer for AGENTS.md and .codex/agents profiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
