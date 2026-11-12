#!/usr/bin/env python3
"""Validate explicit Antigravity tool declarations and generated agent bundle parity."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Install: python -m pip install -r requirements-dev.txt") from exc

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts" / "agent-tool-policy.json"
errors: list[str] = []


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


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    relative = path.relative_to(ROOT)
    if not text.startswith("---\\n"):
        errors.append(f"{relative}: missing YAML frontmatter")
        return {}
    end = text.find("\\n---", 4)
    if end < 0:
        errors.append(f"{relative}: unterminated YAML frontmatter")
        return {}
    try:
        parsed = yaml.load(text[4:end], Loader=UniqueLoader)
    except (ValueError, yaml.YAMLError) as exc:
        errors.append(f"{relative}: invalid/duplicate YAML frontmatter: {exc}")
        return {}
    if not isinstance(parsed, dict):
        errors.append(f"{relative}: frontmatter must be a YAML mapping")
        return {}
    return parsed


if not POLICY_PATH.is_file():
    print("AGENT TOOL VALIDATION FAILED: missing contracts/agent-tool-policy.json")
    sys.exit(1)

policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
frontmatter_policy = policy.get("frontmatter", {})
expected_tools = frontmatter_policy.get("tools")
if not isinstance(expected_tools, list) or len(expected_tools) != 13 or len(set(expected_tools)) != 13:
    errors.append("agent-tool-policy.json: frontmatter.tools must contain exactly 13 unique tool names")
if frontmatter_policy.get("commandExecutionPolicy") != "auto":
    errors.append("agent-tool-policy.json: commandExecutionPolicy must be 'auto'")
for key in ("mainAgent", "subagent", "inheritMcp", "inheritCustomizations"):
    if frontmatter_policy.get(key) is not True:
        errors.append(f"agent-tool-policy.json: {key} must be true")

expected_agents = set(policy.get("agents", []))
seen: set[str] = set()
for source in sorted((ROOT / "modules").glob("*/agents/*.md")):
    agent_id = source.stem
    seen.add(agent_id)
    frontmatter = parse_frontmatter(source)

    if frontmatter.get("name") != agent_id:
        errors.append(f"{source.relative_to(ROOT)}: frontmatter name must match agent id '{agent_id}'")
    if not isinstance(frontmatter.get("description"), str) or not frontmatter["description"].strip():
        errors.append(f"{source.relative_to(ROOT)}: description is required")
    if frontmatter.get("tools") != expected_tools:
        errors.append(f"{source.relative_to(ROOT)}: tools must exactly match the 13-tool policy list")
    if frontmatter.get("commandExecutionPolicy") != "auto":
        errors.append(f"{source.relative_to(ROOT)}: commandExecutionPolicy: auto is required")
    for key in ("inheritMcp", "inheritCustomizations", "mainAgent", "subagent"):
        if frontmatter.get(key) is not True:
            errors.append(f"{source.relative_to(ROOT)}: {key}: true is required")
    for key in ("mcpServers", "skills"):
        if key in frontmatter:
            errors.append(f"{source.relative_to(ROOT)}: do not add per-agent {key} overrides")

    generated = ROOT / "agents" / source.name
    if not generated.is_file():
        errors.append(f"agents/{source.name}: generated agent file is missing")
    elif generated.read_bytes() != source.read_bytes():
        errors.append(f"agents/{source.name}: generated bundle is out of sync with canonical module source")

for agent_id in sorted(expected_agents - seen):
    errors.append(f"agent-tool-policy.json: source agent is missing: {agent_id}")
for agent_id in sorted(seen - expected_agents):
    errors.append(f"agent-tool-policy.json: unexpected agent is missing from policy: {agent_id}")

if errors:
    print("AGENT TOOL VALIDATION FAILED")
    for error in errors:
        print("ERROR:", error)
    sys.exit(1)

print(
    f"AGENT TOOL VALIDATION PASSED: {len(seen)} agents; exact 13-tool allowlist; "
    "commandExecutionPolicy=auto; main/subagent and MCP/customization inheritance enabled"
)
