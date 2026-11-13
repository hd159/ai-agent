#!/usr/bin/env python3
"""Validate Codex, Claude Code, and Cursor marketplace manifests against one root bundle."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT_PATHS = {"agents": "./agents/", "skills": "./skills/", "rules": "./rules/"}


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

    catalog = load("ecosystem.json")
    version = catalog.get("version")
    manifests = {
        "claude": (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ("agents", "skills", "rules")),
        "cursor": (".cursor-plugin/plugin.json", ".cursor-plugin/marketplace.json", ("agents", "skills", "rules")),
        "codex": (".codex-plugin/plugin.json", ".agents/plugins/marketplace.json", ("agents", "skills")),
    }

    for platform, (plugin_path, marketplace_path, components) in manifests.items():
        plugin = load(plugin_path)
        marketplace = load(marketplace_path)
        if plugin.get("name") != "ai-agent-ecosystem":
            errors.append(f"{plugin_path}: plugin name must be ai-agent-ecosystem")
        if plugin.get("version") != version:
            errors.append(f"{plugin_path}: plugin version must match ecosystem.json ({version})")
        for component in components:
            expected = COMPONENT_PATHS[component]
            if plugin.get(component) != expected:
                errors.append(f"{plugin_path}: {component} must resolve from plugin root as {expected}")
            if not (root / expected.removeprefix("./")).is_dir():
                errors.append(f"{plugin_path}: referenced root component directory is missing: {expected}")

        entries = marketplace.get("plugins", [])
        if len(entries) != 1:
            errors.append(f"{marketplace_path}: expected exactly one marketplace plugin entry")
            continue
        entry = entries[0]
        if entry.get("name") != "ai-agent-ecosystem":
            errors.append(f"{marketplace_path}: marketplace plugin name mismatch")
        if platform in {"claude", "cursor"}:
            if entry.get("source") != "./":
                errors.append(f"{marketplace_path}: source must be ./ (repository root plugin)")
        else:
            source = entry.get("source", {})
            if source.get("source") != "local" or source.get("path") != ".":
                errors.append(f"{marketplace_path}: Codex source must resolve to the repository root plugin (local path '.')")
            policy = entry.get("policy", {})
            if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
                errors.append(f"{marketplace_path}: Codex installation/authentication policy mismatch")

    # Metadata directories contain manifests only; component paths always resolve from repository root.
    expected_files = {
        ".claude-plugin": {"plugin.json", "marketplace.json"},
        ".cursor-plugin": {"plugin.json", "marketplace.json"},
        ".codex-plugin": {"plugin.json"},
        ".agents/plugins": {"marketplace.json"},
    }
    for relative, expected in expected_files.items():
        directory = root / relative
        if not directory.is_dir():
            errors.append(f"required metadata directory is missing: {relative}")
            continue
        actual = {path.name for path in directory.iterdir() if path.is_file()}
        actual_dirs = {path.name for path in directory.iterdir() if path.is_dir()}
        if actual != expected or actual_dirs:
            errors.append(
                f"{relative} must contain only {sorted(expected)}; "
                f"files={sorted(actual)}, directories={sorted(actual_dirs)}"
            )

    # The distributable components exist once, at the repository root.
    for duplicate in (root / "plugins" / "ai-agent", root / "plugins" / "ai-agent-ecosystem"):
        if duplicate.exists():
            errors.append(f"duplicate plugin bundle is forbidden: {duplicate.relative_to(root)}")
    for metadata in (root / ".claude-plugin", root / ".cursor-plugin", root / ".codex-plugin"):
        for child in ("agents", "skills", "rules"):
            if (metadata / child).exists():
                errors.append(f"duplicate component directory is forbidden: {metadata.relative_to(root)}/{child}")

    agent_files = sorted((root / "agents").glob("*.md"))
    expected_agents = set(load("contracts/agent-tool-policy.json").get("agents", []))
    if {path.stem for path in agent_files} != expected_agents:
        errors.append("root ./agents inventory does not match contracts/agent-tool-policy.json")

    source_skills = sorted((root / "modules").glob("*/skills/*/SKILL.md"))
    root_skills = sorted((root / "skills").glob("*/SKILL.md"))
    if len(root_skills) != len(source_skills):
        errors.append(f"root ./skills inventory mismatch: expected {len(source_skills)}, found {len(root_skills)}")
    for source in source_skills:
        target = root / "skills" / source.parent.name / "SKILL.md"
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            errors.append(f"root skill differs from canonical module source: {source.parent.name}")

    rule = root / "rules" / "ai-agent-constitution.mdc"
    if not rule.is_file():
        errors.append("root ./rules/ai-agent-constitution.mdc is required")
    else:
        content = rule.read_text(encoding="utf-8")
        if not content.startswith("---\n") or "alwaysApply: true" not in content.split("\n---", 1)[0]:
            errors.append("root constitution rule must use native MDC frontmatter with alwaysApply: true")
        if "Universal Agent Constitution" not in content:
            errors.append("root constitution rule must contain the shared constitution")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("MARKETPLACE VALIDATION FAILED")
        for error in errors:
            print("ERROR:", error)
        return 1
    print("MARKETPLACE VALIDATION PASSED: one root bundle shared by Codex, Claude Code, and Cursor")
    print("Root components: 7 agents, 19 skills, 1 MDC constitution rule (+ Antigravity AGENTS.md compatibility rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
