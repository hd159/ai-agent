#!/usr/bin/env python3
"""Dependency-free structural validator for the single-repository AI Agent Ecosystem."""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def fail(message):
    errors.append(message)


def parse_frontmatter(text, path):
    if not text.startswith("---\n"):
        fail(f"{path}: missing YAML frontmatter")
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        fail(f"{path}: unterminated YAML frontmatter")
        return {}
    result = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return result


for path in ROOT.rglob("*.json"):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")

module_ids = set()
agent_ids = set()
module_dirs = sorted(path for path in (ROOT / "modules").iterdir() if path.is_dir())
for module_dir in module_dirs:
    manifest_path = module_dir / "module.json"
    if not manifest_path.is_file():
        fail(f"{module_dir.relative_to(ROOT)}: missing module.json")
        continue
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        continue
    module_id = manifest.get("id")
    if module_id != module_dir.name:
        fail(f"{manifest_path.relative_to(ROOT)}: id must match module directory")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", module_id or ""):
        fail(f"{manifest_path.relative_to(ROOT)}: invalid module id")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        fail(f"{manifest_path.relative_to(ROOT)}: invalid semantic version")
    module_ids.add(module_id)
    agent_dir = module_dir / "agents"
    if agent_dir.exists():
        for agent_file in agent_dir.glob("*.md"):
            fm = parse_frontmatter(agent_file.read_text(encoding="utf-8"), agent_file.relative_to(ROOT))
            if fm.get("name") != agent_file.stem:
                fail(f"{agent_file.relative_to(ROOT)}: agent name must match filename")
            if not fm.get("description"):
                fail(f"{agent_file.relative_to(ROOT)}: missing description")
            if fm.get("subagent") not in ("true", "false"):
                fail(f"{agent_file.relative_to(ROOT)}: subagent must be true or false")
            if fm.get("mainAgent") not in ("true", "false"):
                fail(f"{agent_file.relative_to(ROOT)}: mainAgent must be true or false")
            agent_ids.add(agent_file.stem)
    for skill_file in module_dir.glob("skills/*/SKILL.md"):
        fm = parse_frontmatter(skill_file.read_text(encoding="utf-8"), skill_file.relative_to(ROOT))
        if fm.get("name") != skill_file.parent.name:
            fail(f"{skill_file.relative_to(ROOT)}: skill name must match directory")
        if not fm.get("description"):
            fail(f"{skill_file.relative_to(ROOT)}: missing skill description")

catalog_path = ROOT / "ecosystem.json"
if catalog_path.is_file():
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_ids = {item.get("id") for item in catalog.get("modules", [])}
    if catalog_ids != module_ids:
        fail("ecosystem.json module IDs do not match modules/* directories")
    release_version = catalog.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", release_version):
        fail("ecosystem.json version must use MAJOR.MINOR.PATCH")
    adapter_versions = catalog.get("adapters", {})
    for adapter_id in ("antigravity", "codex", "copilot", "claude-code", "cursor"):
        adapter = adapter_versions.get(adapter_id, {})
        if not re.fullmatch(r"\d+\.\d+\.\d+", adapter.get("version", "")):
            fail(f"ecosystem.json adapter '{adapter_id}' must declare a semantic version")
    if adapter_versions.get("antigravity", {}).get("version") != "0.3.2":
        fail("Antigravity adapter version must remain 0.3.2")
    for adapter_id in ("codex", "copilot", "claude-code", "cursor"):
        if adapter_versions.get(adapter_id, {}).get("version") != release_version:
            fail(f"ecosystem.json adapter '{adapter_id}' version must match ecosystem release {release_version}")
    plugin_manifest_path = ROOT / "plugin.json"
    if plugin_manifest_path.is_file():
        plugin_manifest = json.loads(plugin_manifest_path.read_text(encoding="utf-8"))
        antigravity_version = catalog.get("adapters", {}).get("antigravity", {}).get("version", release_version)
        if plugin_manifest.get("version") != antigravity_version:
            fail("plugin.json version must match ecosystem.adapters.antigravity.version")
        if antigravity_version != "0.3.2":
            fail("Antigravity adapter must remain backward-compatible at version 0.3.2")
    for module in catalog.get("modules", []):
        if module.get("version") != release_version:
            fail(f"ecosystem.json module '{module.get('id')}' version must match release {release_version}")
    for module_dir in module_dirs:
        manifest_path = module_dir / "module.json"
        if manifest_path.is_file():
            module_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if module_manifest.get("version") != release_version:
                fail(f"{manifest_path.relative_to(ROOT)}: version must match ecosystem release {release_version}")
else:
    fail("missing ecosystem.json")

for team_file in (ROOT / "teams").glob("*/team.json"):
    team = json.loads(team_file.read_text(encoding="utf-8"))
    if team.get("orchestrator") not in agent_ids:
        fail(f"{team_file.relative_to(ROOT)}: unknown orchestrator agent")
    for module_id in team.get("shared_modules", []):
        if module_id not in module_ids:
            fail(f"{team_file.relative_to(ROOT)}: unknown shared module '{module_id}'")
    member_agents = set()
    for member in team.get("members", []):
        if member.get("module") not in module_ids:
            fail(f"{team_file.relative_to(ROOT)}: unknown member module '{member.get('module')}'")
        if member.get("agent") not in agent_ids:
            fail(f"{team_file.relative_to(ROOT)}: unknown member agent '{member.get('agent')}'")
        member_agents.add(member.get("agent"))
    for stage in team.get("workflow", []):
        for agent_id in stage.get("agents", []):
            if agent_id not in member_agents and agent_id != team.get("orchestrator"):
                fail(f"{team_file.relative_to(ROOT)}: workflow references unknown agent '{agent_id}'")

required = [
    "contracts/schemas/agent.schema.json",
    "contracts/schemas/task.schema.json",
    "contracts/schemas/verification.schema.json",
    "scripts/quality_gate.py",
    "tests/test_quality_gate.py",
    "requirements-dev.txt",
    "docs/QUALITY-GATES.md",
    "templates/project/execution/VERIFICATION_TEMPLATE.json",
    "contracts/schemas/team.schema.json",
    "contracts/schemas/handoff.schema.json",
    "contracts/schemas/execution-state.schema.json",
    "contracts/schemas/project-plan.schema.json",
    "contracts/examples/task-example.json",
    "contracts/examples/handoff-example.json",
    "contracts/examples/execution-state-example.json",
    "contracts/examples/project-plan-example.json",
    "plugin.json",
    "agents",
    "skills",
    "rules",
    "scripts/build_single_plugin.py",
    "scripts/validate_agent_tools.py",
    "scripts/validate_capabilities.py",
    "tests/test_capabilities.py",
    "skills/capability-smoke-test/SKILL.md",
    "docs/AGENT-DIAGNOSTICS.md",
    "contracts/agent-tool-policy.json",
    "docs/USER-GUIDE.md",
    "docs/COMMAND-REFERENCE.md",
    "docs/ORCHESTRATION-WORKFLOW.md",
    "docs/PROJECT-BOOTSTRAP.md",
    "docs/ARCHITECTURE-DOCUMENTATION-STANDARD.md",
    "docs/PROMPT-COOKBOOK.md",
    "docs/architecture/PERSISTENT-PROJECT-MEMORY.md",
    "contracts/platform-adapters.json",
    "scripts/adapter_support.py",
    "scripts/build_adapters.py",
    "scripts/install_adapter.py",
    "scripts/validate_adapters.py",
    "tests/test_adapters.py",
    "docs/architecture/MULTI-PLATFORM-ADAPTERS.md",
    "docs/adapters/copilot/README.md",
    "docs/adapters/codex/README.md",
    "docs/adapters/claude-code/README.md",
    "docs/adapters/cursor/README.md",
    "docs/adapters/antigravity/README.md",
    "docs/adapters/README.md",
    ".agents/plugins/marketplace.json",
    ".cursor-plugin/marketplace.json",
    "plugins/ai-agent-ecosystem/.codex-plugin/plugin.json",
    "plugins/ai-agent-ecosystem/.cursor-plugin/plugin.json",
    "plugins/ai-agent-ecosystem/skills",
    "plugins/ai-agent-ecosystem/agents",
    "plugins/ai-agent-ecosystem/rules/ai-agent-ecosystem.mdc",
    "scripts/build_marketplace_components.py",
    "scripts/validate_marketplaces.py",
    "tests/test_marketplaces.py",
    "docs/marketplaces/README.md",
]
for relative in required:
    if not (ROOT / relative).exists():
        fail(f"missing required path: {relative}")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print("ERROR:", error)
    sys.exit(1)

skill_count = sum(1 for _ in (ROOT / "modules").glob("*/skills/*/SKILL.md"))
team_count = len(list((ROOT / "teams").glob("*/team.json")))
print("VALIDATION PASSED")
print(f"Source modules: {len(module_ids)}")
print(f"Agents: {len(agent_ids)}")
print(f"Skills: {skill_count}")
print(f"Team presets: {team_count}")
