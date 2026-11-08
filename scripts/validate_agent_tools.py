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


def parse_frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return ""
    end = text.find("\n---", 4)
    if end < 0:
        errors.append(f"{path.relative_to(ROOT)}: unterminated YAML frontmatter")
        return ""
    return text[4:end]


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
    if re.search(r"(?m)^tools\s*:", frontmatter):
        errors.append(f"{source.relative_to(ROOT)}: remove tools allowlist; omission grants all built-in tools")
    if re.search(r"(?m)^commandExecutionPolicy\s*:", frontmatter):
        errors.append(f"{source.relative_to(ROOT)}: omit commandExecutionPolicy so host/user settings govern execution")
    if not re.search(r"(?m)^inheritMcp:\s*true\s*$", frontmatter):
        errors.append(f"{source.relative_to(ROOT)}: inheritMcp: true is required")
    if not re.search(r"(?m)^inheritCustomizations:\s*true\s*$", frontmatter):
        errors.append(f"{source.relative_to(ROOT)}: inheritCustomizations: true is required")

    generated = ROOT / "agents" / source.name
    if not generated.is_file():
        errors.append(f"agents/{source.name}: generated agent file is missing")
    elif generated.read_bytes() != source.read_bytes():
        errors.append(f"agents/{source.name}: generated bundle is out of sync with source module")

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
    "all built-in tools enabled; MCP/customization inheritance enabled; "
    "execution policy left to Antigravity host settings"
)
