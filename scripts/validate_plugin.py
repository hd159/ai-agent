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
            result[match.group(1)] = match.group(2).strip().strip("\"'")
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
        if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
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

# Claude Code and Cursor metadata directories contain manifests only.
for metadata_dir in (".claude-plugin", ".cursor-plugin", ".agents/plugins"):
    path = ROOT / metadata_dir
    if path.is_dir():
        for child in path.iterdir():
            if child.is_dir():
                errors.append(f"{metadata_dir} must contain metadata only; found directory {child.name}/")

# Codex requires a strict subdirectory source. Keep only its manifest and the
# skills-only mirror; agents and rules remain canonical at the repository root.
if (ROOT / ".codex-plugin").exists():
    errors.append("root .codex-plugin/ cannot be installed through a Codex repo marketplace; use plugins/ai-agent/")
codex_root = ROOT / "plugins" / "ai-agent"
if codex_root.is_dir():
    top_level = {path.name for path in codex_root.iterdir()}
    if top_level != {".codex-plugin", "skills"}:
        errors.append(f"plugins/ai-agent may contain only .codex-plugin/ and skills/; found {sorted(top_level)}")
    for unsupported in ("agents", "rules"):
        if (codex_root / unsupported).exists():
            errors.append(f"plugins/ai-agent/{unsupported}/ must not duplicate the root bundle")
    codex_manifest_path = codex_root / ".codex-plugin" / "plugin.json"
    try:
        codex_manifest = json.loads(codex_manifest_path.read_text(encoding="utf-8"))
        if codex_manifest.get("name") != "ai-agent":
            errors.append("plugins/ai-agent/.codex-plugin/plugin.json name must match its directory")
        if codex_manifest.get("skills") != "./skills/":
            errors.append("Codex plugin manifest must reference its local ./skills/ mirror")
        if "agents" in codex_manifest or "rules" in codex_manifest:
            errors.append("Codex plugin manifest must not declare unsupported agents/rules components")
    except Exception as exc:
        errors.append(f"invalid Codex plugin manifest: {exc}")
    root_skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    codex_skill_files = sorted((codex_root / "skills").glob("*/SKILL.md"))
    if len(codex_skill_files) != len(root_skill_files):
        errors.append("Codex skill mirror count must match the shared root skills directory")
    for source in root_skill_files:
        target = codex_root / "skills" / source.parent.name / "SKILL.md"
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            errors.append(f"Codex skill mirror differs from root source: {source.parent.name}")
else:
    errors.append("required Codex plugin subdirectory plugins/ai-agent is missing")

if (ROOT / "plugins" / "ai-agent-ecosystem").exists():
    errors.append("obsolete duplicate plugins/ai-agent-ecosystem package is forbidden")

if errors:
    print("PLUGIN VALIDATION FAILED")
    for error in errors:
        print("ERROR:", error)
    sys.exit(1)

print("PLUGIN VALIDATION PASSED: Antigravity 0.3.2; shared root bundle "
      f"{len(agent_files)} agents, {len(skill_files)} skills, Cursor MDC rule")
