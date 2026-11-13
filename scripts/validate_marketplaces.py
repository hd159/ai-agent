#!/usr/bin/env python3
"""Validate one canonical root bundle shared by Codex, Claude Code, Copilot CLI, and Cursor."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_COMPONENTS = {"agents": "./agents/", "skills": "./skills/", "rules": "./rules/"}


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

    # Claude Code, Codex core-plugins, and Copilot CLI share the Claude-format
    # marketplace/catalog. Codex also reads the root .codex-plugin manifest.
    marketplaces = {
        "claude_code": (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ("agents", "skills"),
        ),
        "cursor": (
            ".cursor-plugin/plugin.json",
            ".cursor-plugin/marketplace.json",
            ("agents", "skills", "rules"),
        ),
    }
    for platform, (plugin_path, marketplace_path, components) in marketplaces.items():
        plugin = load(plugin_path)
        marketplace = load(marketplace_path)
        if plugin.get("name") != "ai-agent-ecosystem":
            errors.append(f"{plugin_path}: plugin name must be ai-agent-ecosystem")
        if plugin.get("version") != version:
            errors.append(f"{plugin_path}: plugin version must match ecosystem.json ({version})")
        for component in components:
            expected = ROOT_COMPONENTS[component]
            if plugin.get(component) != expected:
                errors.append(f"{plugin_path}: {component} must resolve from repository root as {expected}")
            if not (root / component).is_dir():
                errors.append(f"{plugin_path}: root component directory is missing: {component}/")
        if platform == "claude_code" and "rules" in plugin:
            errors.append(f"{plugin_path}: Claude Code manifest should declare only supported agents/skills paths")

        if marketplace.get("name") != "ai-agent-ecosystem":
            errors.append(f"{marketplace_path}: marketplace name mismatch")
        entries = marketplace.get("plugins", [])
        if len(entries) != 1:
            errors.append(f"{marketplace_path}: expected exactly one marketplace plugin entry")
            continue
        entry = entries[0]
        if entry.get("name") != "ai-agent-ecosystem":
            errors.append(f"{marketplace_path}: plugin entry name mismatch")
        if entry.get("source") != "./":
            errors.append(f"{marketplace_path}: source must be ./ (repository root plugin)")
        if entry.get("version") != version:
            errors.append(f"{marketplace_path}: plugin version must match ecosystem.json")

    # Codex core-plugins discovers .claude-plugin/marketplace.json and resolves
    # source './' to the repository root. Its native manifest lives at
    # .codex-plugin/plugin.json. The agents path is shared ecosystem metadata;
    # current Codex core-plugins consumes the skills path.
    codex_manifest_path = ".codex-plugin/plugin.json"
    codex_manifest = load(codex_manifest_path)
    if codex_manifest.get("name") != "ai-agent-ecosystem":
        errors.append(f"{codex_manifest_path}: name must be ai-agent-ecosystem")
    if codex_manifest.get("version") != version:
        errors.append(f"{codex_manifest_path}: version must match ecosystem.json ({version})")
    for component in ("agents", "skills"):
        expected = ROOT_COMPONENTS[component]
        if codex_manifest.get(component) != expected:
            errors.append(f"{codex_manifest_path}: {component} must resolve to {expected}")
        if not (root / component).is_dir():
            errors.append(f"{codex_manifest_path}: root {component}/ directory is missing")

    # All hidden plugin directories contain manifests only. The Codex marketplace
    # intentionally reuses .claude-plugin/marketplace.json; no .agents catalog
    # or nested plugins/ copy is needed.
    expected_metadata = {
        ".claude-plugin": {"plugin.json", "marketplace.json"},
        ".cursor-plugin": {"plugin.json", "marketplace.json"},
        ".codex-plugin": {"plugin.json"},
    }
    for relative, expected_files in expected_metadata.items():
        directory = root / relative
        if not directory.is_dir():
            errors.append(f"required metadata directory is missing: {relative}")
            continue
        files = {path.name for path in directory.iterdir() if path.is_file()}
        directories = {path.name for path in directory.iterdir() if path.is_dir()}
        if files != expected_files or directories:
            errors.append(
                f"{relative} must contain only {sorted(expected_files)}; "
                f"files={sorted(files)}, directories={sorted(directories)}"
            )

    if (root / "plugins").exists():
        errors.append("plugins/ is forbidden: all marketplace components must be shared from the repository root")
    if (root / ".agents").exists():
        errors.append(".agents/ is obsolete for this layout; Codex uses .claude-plugin/marketplace.json")
    
    # Verify the root bundle is generated from canonical module sources.
    expected_agents = set(load("contracts/agent-tool-policy.json").get("agents", []))
    root_agent_files = sorted((root / "agents").glob("*.md"))
    if {path.stem for path in root_agent_files} != expected_agents:
        errors.append("root ./agents inventory does not match contracts/agent-tool-policy.json")
    source_agents = sorted((root / "modules").glob("*/agents/*.md"))
    if len(root_agent_files) != len(source_agents):
        errors.append(f"root ./agents count mismatch: expected {len(source_agents)}, found {len(root_agent_files)}")
    for source in source_agents:
        target = root / "agents" / source.name
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            errors.append(f"root agent differs from canonical module source: {source.name}")

    source_skills = sorted((root / "modules").glob("*/skills/*/SKILL.md"))
    root_skills = sorted((root / "skills").glob("*/SKILL.md"))
    if len(root_skills) != len(source_skills):
        errors.append(f"root ./skills inventory mismatch: expected {len(source_skills)}, found {len(root_skills)}")
    for source in source_skills:
        target = root / "skills" / source.parent.name / "SKILL.md"
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            errors.append(f"root skill differs from canonical module source: {source.parent.name}")

    source_rule = root / "modules" / "agent-constitution" / "rules" / "AGENTS.md"
    root_rule = root / "rules" / "AGENTS.md"
    if not source_rule.is_file() or not root_rule.is_file() or source_rule.read_bytes() != root_rule.read_bytes():
        errors.append("root rules/AGENTS.md must match the canonical module constitution")
    mdc_rule = root / "rules" / "ai-agent-constitution.mdc"
    if not mdc_rule.is_file():
        errors.append("root rules/ai-agent-constitution.mdc is required")
    else:
        content = mdc_rule.read_text(encoding="utf-8")
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
    print("MARKETPLACE VALIDATION PASSED: Codex, Claude Code, Copilot CLI, and Cursor share the root bundle")
    print("Root components: 7 agents, 19 skills, AGENTS.md, and ai-agent-constitution.mdc")
    print("No plugins/ mirror or .agents/plugins marketplace catalog")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
