#!/usr/bin/env python3
"""Validate the single canonical root plugin bundle and its backward compatibility."""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        errors.append(f"{path.relative_to(ROOT)}: unterminated frontmatter")
        return {}
    result = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip("\\\"'")
    return result


manifest_path = ROOT / "plugin.json"
manifest = {}
if not manifest_path.is_file():
    errors.append("plugin.json must exist at repository root")
else:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", manifest.get("name", "")):
            errors.append("plugin.json name must be lowercase kebab-case")
        if not re.fullmatch(r"\\d+\\.\\d+\\.\\d+", manifest.get("version", "")):
            errors.append("plugin.json version must use MAJOR.MINOR.PATCH")
        if len(manifest.get("suggestedPrompts", [])) > 3:
            errors.append("plugin.json suggestedPrompts supports at most 3 items")
        if manifest.get("version") != "0.3.2":
            errors.append("Antigravity root plugin must remain backward-compatible at version 0.3.2")
    except Exception as exc:
        errors.append(f"invalid plugin.json: {exc}")

agents_dir = ROOT / "agents"
agent_files = sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []
policy_path = ROOT / "contracts" / "agent-tool-policy.json"
expected_agents = set()
if policy_path.is_file():
    expected_agents = set(json.loads(policy_path.read_text(encoding="utf-8")).get("agents", []))
if {path.stem for path in agent_files} != expected_agents:
    errors.append(
        f"root agent bundle mismatch: expected={sorted(expected_agents)}, "
        f"actual={sorted(path.stem for path in agent_files)}"
    )
for path in agent_files:
    fm = parse_frontmatter(path)
    if fm.get("name") != path.stem:
        errors.append(f"{path.relative_to(ROOT)}: name must match filename")
    if not fm.get("description"):
        errors.append(f"{path.relative_to(ROOT)}: description is required")

skills_dir = ROOT / "skills"
skill_files = sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []
source_skills = sorted((ROOT / "modules").glob("*/skills/*/SKILL.md"))
if len(skill_files) != len(source_skills):
    errors.append(f"root skill bundle count mismatch: expected={len(source_skills)}, actual={len(skill_files)}")
for path in skill_files:
    fm = parse_frontmatter(path)
    if fm.get("name") != path.parent.name:
        errors.append(f"{path.relative_to(ROOT)}: skill name must match directory")
    if not fm.get("description"):
        errors.append(f"{path.relative_to(ROOT)}: description is required")

constitution_mdc = ROOT / "rules" / "ai-agent-constitution.mdc"
if not constitution_mdc.is_file():
    errors.append("rules/ai-agent-constitution.mdc must exist in the shared root bundle")
else:
    content = constitution_mdc.read_text(encoding="utf-8")
    fm = parse_frontmatter(constitution_mdc)
    if fm.get("alwaysApply") != "true":
        errors.append("rules/ai-agent-constitution.mdc must set alwaysApply: true")
    if "Universal Agent Constitution" not in content:
        errors.append("rules/ai-agent-constitution.mdc must contain the shared constitution")

# Plugin metadata directories must never contain copied component bundles.
for metadata_dir in (".claude-plugin", ".cursor-plugin", ".codex-plugin", ".agents/plugins"):
    path = ROOT / metadata_dir
    if path.is_dir():
        for child in path.iterdir():
            if child.is_dir() and child.name in {"agents", "skills", "rules"}:
                errors.append(f"{metadata_dir} must contain metadata only; found duplicated {child.name}/")

# The previous nested package duplicated the root agents/skills/rules. Fail if it returns.
for duplicate in (ROOT / "plugins" / "ai-agent", ROOT / "plugins" / "ai-agent-ecosystem"):
    if duplicate.exists():
        errors.append(f"duplicate plugin component package is forbidden: {duplicate.relative_to(ROOT)}")

if errors:
    print("PLUGIN VALIDATION FAILED")
    for error in errors:
        print("ERROR:", error)
    sys.exit(1)

print("PLUGIN VALIDATION PASSED: Antigravity 0.3.2; shared root bundle "
      f"{len(agent_files)} agents, {len(skill_files)} skills, Cursor MDC rule")
