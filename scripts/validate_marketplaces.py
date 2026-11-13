#!/usr/bin/env python3
"""Validate root-shared Claude/Cursor components and the minimal Codex subdirectory package."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_COMPONENTS = {"agents": "./agents/", "skills": "./skills/", "rules": "./rules/"}
CODEX_PACKAGE = "plugins/ai-agent"


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

    # Claude Code and Cursor can consume the repository root as the plugin root.
    root_plugins = {
        "claude": (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"),
        "cursor": (".cursor-plugin/plugin.json", ".cursor-plugin/marketplace.json"),
    }
    for platform, (plugin_path, marketplace_path) in root_plugins.items():
        plugin = load(plugin_path)
        marketplace = load(marketplace_path)
        if plugin.get("name") != "ai-agent-ecosystem":
            errors.append(f"{plugin_path}: plugin name must be ai-agent-ecosystem")
        if plugin.get("version") != version:
            errors.append(f"{plugin_path}: plugin version must match ecosystem.json ({version})")
        for component, expected in ROOT_COMPONENTS.items():
            if plugin.get(component) != expected:
                errors.append(f"{plugin_path}: {component} must resolve from repository root as {expected}")
            if not (root / expected.removeprefix("./")).is_dir():
                errors.append(f"{plugin_path}: root component directory is missing: {expected}")

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

    # Codex currently rejects a repository-root local source and its plugin
    # manifest supports skills, not agents/rules. Its only permitted mirror is
    # the smallest package at ./plugins/ai-agent containing plugin.json + skills.
    codex_plugin_path = f"{CODEX_PACKAGE}/.codex-plugin/plugin.json"
    codex_marketplace_path = ".agents/plugins/marketplace.json"
    codex_plugin = load(codex_plugin_path)
    codex_marketplace = load(codex_marketplace_path)
    if codex_plugin.get("name") != "ai-agent":
        errors.append(f"{codex_plugin_path}: name must match the plugins/ai-agent directory")
    if codex_plugin.get("version") != version:
        errors.append(f"{codex_plugin_path}: plugin version must match ecosystem.json ({version})")
    if codex_plugin.get("skills") != "./skills/":
        errors.append(f"{codex_plugin_path}: skills must resolve to ./skills/ inside the Codex package")
    if "agents" in codex_plugin or "rules" in codex_plugin:
        errors.append(f"{codex_plugin_path}: Codex plugin manifest must not declare unsupported agents/rules components")

    if codex_marketplace.get("name") != "ai-agent-ecosystem":
        errors.append(f"{codex_marketplace_path}: marketplace name mismatch")
    codex_entries = codex_marketplace.get("plugins", [])
    if len(codex_entries) != 1:
        errors.append(f"{codex_marketplace_path}: expected exactly one Codex plugin entry")
    else:
        entry = codex_entries[0]
        if entry.get("name") != "ai-agent":
            errors.append(f"{codex_marketplace_path}: entry name must match the Codex plugin directory")
        source = entry.get("source", {})
        if source.get("source") != "local" or source.get("path") != f"./{CODEX_PACKAGE}":
            errors.append(f"{codex_marketplace_path}: Codex source must use ./plugins/ai-agent (root paths are rejected)")
        policy = entry.get("policy", {})
        if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
            errors.append(f"{codex_marketplace_path}: Codex installation/authentication policy mismatch")
        if entry.get("category") != "Developer Tools":
            errors.append(f"{codex_marketplace_path}: Codex category mismatch")

    # Metadata directories stay metadata-only; component directories are not copied here.
    expected_metadata = {
        ".claude-plugin": {"plugin.json", "marketplace.json"},
        ".cursor-plugin": {"plugin.json", "marketplace.json"},
        ".agents/plugins": {"marketplace.json"},
        f"{CODEX_PACKAGE}/.codex-plugin": {"plugin.json"},
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

    # No root Codex manifest can be installed as a repo-local plugin: Codex
    # requires a strict subdirectory. No legacy duplicated marketplace package may return.
    if (root / ".codex-plugin").exists():
        errors.append("root .codex-plugin/ is not a valid repo-marketplace plugin root; use plugins/ai-agent/.codex-plugin/")
    for duplicate in (root / "plugins" / "ai-agent-ecosystem",):
        if duplicate.exists():
            errors.append(f"obsolete duplicate plugin package is forbidden: {duplicate.relative_to(root)}")

    codex_root = root / CODEX_PACKAGE
    if not codex_root.is_dir():
        errors.append(f"required Codex plugin package is missing: {CODEX_PACKAGE}")
    else:
        actual_top_level = {path.name for path in codex_root.iterdir()}
        if actual_top_level != {".codex-plugin", "skills"}:
            errors.append(
                f"{CODEX_PACKAGE} may contain only .codex-plugin/ and skills/; "
                f"found={sorted(actual_top_level)}"
            )
        for unsupported in ("agents", "rules"):
            if (codex_root / unsupported).exists():
                errors.append(f"{CODEX_PACKAGE}/{unsupported}/ is not supported or required")

    # Root bundle is canonical for Claude Code, Cursor, and Antigravity.
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

    codex_skills = sorted((codex_root / "skills").glob("*/SKILL.md")) if codex_root.is_dir() else []
    if len(codex_skills) != len(root_skills):
        errors.append(f"Codex skills mirror mismatch: expected {len(root_skills)}, found {len(codex_skills)}")
    for source in root_skills:
        target = codex_root / "skills" / source.parent.name / "SKILL.md"
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            errors.append(f"Codex-required skill mirror differs from root source: {source.parent.name}")

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
    print("MARKETPLACE VALIDATION PASSED: Claude Code and Cursor share the root bundle; Codex uses the required skills-only subdirectory package")
    print("Root components: 7 agents, 19 skills, 1 MDC constitution rule (+ Antigravity AGENTS.md)")
    print("Codex exception: 19 skills mirrored under ./plugins/ai-agent; no agent/rule copies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
