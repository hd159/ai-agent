#!/usr/bin/env python3
"""Validate explicit Antigravity agent tool allowlists and generated bundle parity."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts" / "agent-tool-policy.json"
errors: list[str] = []


def parse_tools(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return []
    end = text.find("\n---", 4)
    if end < 0:
        errors.append(f"{path.relative_to(ROOT)}: unterminated YAML frontmatter")
        return []
    lines = text[4:end].splitlines()
    tools_index = next((i for i, line in enumerate(lines) if re.match(r"^tools:\s*$", line)), None)
    if tools_index is None:
        errors.append(f"{path.relative_to(ROOT)}: missing explicit tools allowlist")
        return []
    tools: list[str] = []
    for line in lines[tools_index + 1:]:
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            break
        match = re.fullmatch(r"\s+-\s+([a-z][a-z0-9_]*)\s*", line)
        if not match:
            errors.append(f"{path.relative_to(ROOT)}: malformed tools entry: {line.strip()}")
            continue
        tools.append(match.group(1))
    if not tools:
        errors.append(f"{path.relative_to(ROOT)}: tools allowlist must not be empty")
    if len(tools) != len(set(tools)):
        errors.append(f"{path.relative_to(ROOT)}: duplicate tool names")
    return tools


if not POLICY_PATH.is_file():
    print("AGENT TOOL VALIDATION FAILED: missing contracts/agent-tool-policy.json")
    sys.exit(1)

policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
allowed = set(policy.get("allowed_tools", []))
profiles = policy.get("agents", {})
for agent_id, tools in profiles.items():
    for tool in tools:
        if tool not in allowed:
            errors.append(f"agent-tool-policy.json: unapproved tool '{tool}' for {agent_id}")

seen: set[str] = set()
for source in sorted((ROOT / "modules").glob("*/agents/*.md")):
    agent_id = source.stem
    seen.add(agent_id)
    expected = profiles.get(agent_id)
    if expected is None:
        errors.append(f"{source.relative_to(ROOT)}: no tool profile in agent-tool-policy.json")
        continue
    actual = parse_tools(source)
    unknown = sorted(set(actual) - allowed)
    if unknown:
        errors.append(f"{source.relative_to(ROOT)}: unknown Antigravity tools: {', '.join(unknown)}")
    if actual != expected:
        errors.append(f"{source.relative_to(ROOT)}: tools differ from policy; expected={expected!r}, actual={actual!r}")
    generated = ROOT / "agents" / source.name
    if not generated.is_file():
        errors.append(f"agents/{source.name}: generated agent file is missing")
    elif generated.read_bytes() != source.read_bytes():
        errors.append(f"agents/{source.name}: generated bundle is out of sync with source module")

for agent_id in sorted(set(profiles) - seen):
    errors.append(f"agent-tool-policy.json: profile has no source agent: {agent_id}")

if errors:
    print("AGENT TOOL VALIDATION FAILED")
    for error in errors:
        print("ERROR:", error)
    sys.exit(1)

print(f"AGENT TOOL VALIDATION PASSED: {len(seen)} agents, {len(allowed)} approved tool names")
