#!/usr/bin/env python3
"""Static capability audit for bundled agents, skills, rules, and MCP inheritance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Install: python -m pip install -r requirements-dev.txt") from exc


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"duplicate YAML key {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def frontmatter(path: Path, root: Path, errors: list[str]) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            raise ValueError("missing initial ---")
        end = text.find("\n---", 4)
        if end < 0:
            raise ValueError("missing closing ---")
        obj = yaml.load(text[4:end], Loader=UniqueLoader)
        if not isinstance(obj, dict):
            raise ValueError("frontmatter must be a mapping")
        return obj
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"{path.relative_to(root)}: {exc}")
        return {}


def audit(root: Path) -> tuple[list[str], dict]:
    errors = []
    stats = {"agents": 0, "skills": 0, "rules": 0, "bundled_mcp_servers": 0}
    try:
        policy = json.loads((root / "contracts/agent-tool-policy.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
        catalog = json.loads((root / "ecosystem.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"Missing/invalid manifest, policy or catalog: {exc}"], stats

    if manifest.get("disabled") is True or manifest.get("name") != "ai-agent":
        errors.append("plugin manifest is disabled or has the wrong name")
    if manifest.get("version") != catalog.get("version"):
        errors.append("plugin and ecosystem versions differ")
    if manifest.get("version") != "0.3.2":
        errors.append("plugin version must be 0.3.2")
    if "skills" in manifest and manifest["skills"] not in ("skills", "./skills", ["skills"], ["./skills"]):
        errors.append("plugin skills override may hide bundled skills")

    policy_fm = policy.get("frontmatter", {})
    expected_tools = policy_fm.get("tools")
    if not isinstance(expected_tools, list) or len(expected_tools) != 13 or len(set(expected_tools)) != 13:
        errors.append("agent-tool-policy.json: frontmatter.tools must contain exactly 13 unique tool names")
        expected_tools = []
    if policy_fm.get("commandExecutionPolicy") != "auto":
        errors.append("agent-tool-policy.json: commandExecutionPolicy must be 'auto'")
    for key in ("mainAgent", "subagent", "inheritMcp", "inheritCustomizations"):
        if policy_fm.get(key) is not True:
            errors.append(f"agent-tool-policy.json: {key} must be true")

    expected = set(policy.get("agents", []))
    sources = list((root / "modules").glob("*/agents/*.md"))
    if {p.stem for p in sources} != expected:
        errors.append("source agents disagree with policy")
    if {p.stem for p in (root / "agents").glob("*.md")} != expected:
        errors.append("generated agents disagree with policy")
    for path in sources:
        stats["agents"] += 1
        data = frontmatter(path, root, errors)
        if data.get("name") != path.stem or not isinstance(data.get("description"), str) or not data.get("description", "").strip():
            errors.append(f"{path.relative_to(root)}: invalid agent name/description")
        for key in ("mainAgent", "subagent", "inheritMcp", "inheritCustomizations"):
            if data.get(key) is not True:
                errors.append(f"{path.relative_to(root)}: {key} must be true")
        if data.get("tools") != expected_tools:
            errors.append(f"{path.relative_to(root)}: tools must exactly match the 13-tool policy list")
        if data.get("commandExecutionPolicy") != "auto":
            errors.append(f"{path.relative_to(root)}: commandExecutionPolicy must be 'auto'")
        for key in ("mcpServers", "skills"):
            if key in data:
                errors.append(f"{path.relative_to(root)}: {key} overrides are not permitted")
        generated = root / "agents" / path.name
        if not generated.exists() or generated.read_bytes() != path.read_bytes():
            errors.append(f"agents/{path.name}: generated copy missing or different")

    seen_skills: set[str] = set()
    for path in (root / "modules").glob("*/skills/*/SKILL.md"):
        stats["skills"] += 1
        name = path.parent.name
        if name in seen_skills:
            errors.append(f"duplicate skill: {name}")
        seen_skills.add(name)
        data = frontmatter(path, root, errors)
        description = data.get("description")
        if data.get("name") != name or not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
            errors.append(f"{path.relative_to(root)}: invalid name/description")
        if data.get("disable-model-invocation") is True:
            errors.append(f"{path.relative_to(root)}: automatic skill invocation disabled")
        generated = root / "skills" / name / "SKILL.md"
        if not generated.exists() or generated.read_bytes() != path.read_bytes():
            errors.append(f"skills/{name}/SKILL.md: generated copy missing or different")
    installed_skills = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    if installed_skills != seen_skills:
        errors.append(f"skill inventory mismatch: missing={sorted(seen_skills - installed_skills)}, extra={sorted(installed_skills - seen_skills)}")

    source_rule = root / "modules/agent-constitution/rules/AGENTS.md"
    packaged_rule = root / "rules/AGENTS.md"
    if not source_rule.exists() or not packaged_rule.exists():
        errors.append("missing always-on AGENTS.md rule")
    elif source_rule.read_bytes() != packaged_rule.read_bytes() or not packaged_rule.read_text(encoding="utf-8").strip():
        errors.append("always-on AGENTS.md is empty or out of sync")
    else:
        stats["rules"] = 1

    for kind in ("agents", "skills", "rules"):
        count = sum(mod.get("components", {}).get(kind, 0) for mod in catalog.get("modules", []))
        if count != stats[kind]:
            errors.append(f"catalog {kind}: count={count}, actual={stats[kind]}")

    mcp = root / "mcp_config.json"
    if mcp.exists():
        try:
            obj = json.loads(mcp.read_text(encoding="utf-8"))
            servers = obj.get("mcpServers")
            if not isinstance(servers, dict):
                errors.append("mcp_config.json: mcpServers must be an object")
            else:
                stats["bundled_mcp_servers"] = len(servers)
        except (OSError, ValueError) as exc:
            errors.append(f"invalid mcp_config.json: {exc}")
    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root.resolve()
    errors, stats = audit(root)
    if errors:
        print("FAIL: static capability contract")
        for error in errors:
            print(" -", error)
        return 1
    print(f"PASS: {stats['agents']} agents, {stats['skills']} skills, {stats['rules']} always-on rule, {stats['bundled_mcp_servers']} bundled MCP servers")
    print("Static only. Host permissions/MCP connectivity must be checked in Antigravity runtime.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
