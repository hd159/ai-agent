#!/usr/bin/env python3
"""Validate full Antigravity tool access and generated agent bundle parity."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts" / "agent-tool-policy.json"
errors: list[str] = []


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    relative = path.relative_to(ROOT)
    if not text.startswith("---\n"):
        errors.append(f"{relative}: missing YAML frontmatter")
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        errors.append(f"{relative}: unterminated YAML frontmatter")
        return {}

    raw = text[4:end]
    parsed: dict[str, str] = {}
    current_key: str | None = None
    for line_number, line in enumerate(raw.splitlines(), start=2):
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            if re.match(r"^\s+-\s+", line):
                errors.append(
                    f"{relative}:{line_number}: orphaned YAML sequence item; "
                    "all built-in tools are enabled by omitting the tools property"
                )
                continue
            if current_key != "description":
                errors.append(
                    f"{relative}:{line_number}: unexpected indented YAML content "
                    f"under '{current_key}'"
                )
            continue

        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):(?:[ \t]*(.*))?", line)
        if not match:
            errors.append(f"{relative}:{line_number}: invalid top-level YAML field: {line!r}")
            current_key = None
            continue

        key, value = match.group(1), (match.group(2) or "").strip()
        if key in parsed:
            errors.append(f"{relative}:{line_number}: duplicate frontmatter key '{key}'")
        parsed[key] = value
        current_key = key

    return parsed


if not POLICY_PATH.is_file():
    print("AGENT TOOL VALIDATION FAILED: missing contracts/agent-tool-policy.json")
    sys.exit(1)

policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
frontmatter_policy = policy.get("frontmatter", {})
if not str(frontmatter_policy.get("tools", "")).startswith("omitted"):
    errors.append("agent-tool-policy.json: tools must be omitted to expose all built-in tools")
if frontmatter_policy.get("inheritMcp") is not True:
    errors.append("agent-tool-policy.json: inheritMcp must be true")
if frontmatter_policy.get("inheritCustomizations") is not True:
    errors.append("agent-tool-policy.json: inheritCustomizations must be true")
if not str(frontmatter_policy.get("commandExecutionPolicy", "")).startswith("omitted"):
    errors.append("agent-tool-policy.json: commandExecutionPolicy must be omitted")

expected_agents = set(policy.get("agents", []))
seen: set[str] = set()
for source in sorted((ROOT / "modules").glob("*/agents/*.md")):
    agent_id = source.stem
    seen.add(agent_id)
    frontmatter = parse_frontmatter(source)

    if frontmatter.get("name") != agent_id:
        errors.append(
            f"{source.relative_to(ROOT)}: frontmatter name must match agent id '{agent_id}'"
        )
    if not frontmatter.get("description"):
        errors.append(f"{source.relative_to(ROOT)}: description is required")
    if "tools" in frontmatter:
        errors.append(
            f"{source.relative_to(ROOT)}: remove tools allowlist; omission grants all built-in tools"
        )
    if "commandExecutionPolicy" in frontmatter:
        errors.append(
            f"{source.relative_to(ROOT)}: omit commandExecutionPolicy so host/user settings govern execution"
        )
    if frontmatter.get("inheritMcp") != "true":
        errors.append(f"{source.relative_to(ROOT)}: inheritMcp: true is required")
    if frontmatter.get("inheritCustomizations") != "true":
        errors.append(f"{source.relative_to(ROOT)}: inheritCustomizations: true is required")
    if frontmatter.get("mainAgent") != "true":
        errors.append(f"{source.relative_to(ROOT)}: mainAgent: true is required")
    if frontmatter.get("subagent") != "true":
        errors.append(f"{source.relative_to(ROOT)}: subagent: true is required")

    generated = ROOT / "agents" / source.name
    if not generated.is_file():
        errors.append(f"agents/{source.name}: generated agent file is missing")
    elif generated.read_bytes() != source.read_bytes():
        errors.append(
            f"agents/{source.name}: generated bundle is out of sync with canonical module source"
        )

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
    f"AGENT TOOL VALIDATION PASSED: {len(seen)} agents; "
    "valid frontmatter; all built-in tools enabled; "
    "MCP/customization inheritance enabled; execution policy left to host settings"
)
