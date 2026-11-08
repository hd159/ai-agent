#!/usr/bin/env python3
"""Build the single installable Antigravity plugin from the specialist modules."""
from __future__ import annotations
import argparse, json, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ("plugin.json", "agents", "skills", "rules")


def build(destination: Path) -> list[str]:
    components = ROOT / "modules"
    agents_dir = destination / "agents"
    skills_dir = destination / "skills"
    rules_dir = destination / "rules"
    for directory in (agents_dir, skills_dir, rules_dir):
        directory.mkdir(parents=True, exist_ok=True)

    seen_agents: set[str] = set()
    seen_skills: set[str] = set()
    agent_count = 0
    skill_count = 0
    rule_count = 0

    for component in sorted(components.iterdir()):
        if not component.is_dir():
            continue
        source_agents = component / "agents"
        if source_agents.is_dir():
            for source in sorted(source_agents.glob("*.md")):
                if source.stem in seen_agents:
                    raise ValueError(f"Duplicate agent name: {source.stem}")
                seen_agents.add(source.stem)
                target = agents_dir / source.name
                shutil.copy2(source, target)
                agent_count += 1

        source_skills = component / "skills"
        if source_skills.is_dir():
            for skill_dir in sorted(source_skills.iterdir()):
                skill_file = skill_dir / "SKILL.md"
                if not skill_file.is_file():
                    continue
                if skill_dir.name in seen_skills:
                    raise ValueError(f"Duplicate skill name: {skill_dir.name}")
                seen_skills.add(skill_dir.name)
                shutil.copytree(skill_dir, skills_dir / skill_dir.name)
                skill_count += 1

        source_rules = component / "rules"
        if source_rules.is_dir():
            for source in sorted(source_rules.glob("*.md")):
                target = rules_dir / source.name
                if target.exists():
                    raise ValueError(f"Duplicate rule file: {source.name}")
                shutil.copy2(source, target)
                rule_count += 1

    catalog = json.loads((ROOT / "ecosystem.json").read_text(encoding="utf-8"))
    version = catalog["version"]
    manifest = {
        "$schema": "https://antigravity.google/schemas/v1/plugin.json",
        "name": "ai-agent",
        "displayName": "AI Agent Ecosystem",
        "version": version,
        "description": "A complete multi-agent engineering team: architecture, product design, frontend, backend, infrastructure, QA, and orchestration, with shared engineering skills and behavioral rules.",
        "repository": "https://github.com/hd159/ai-agent",
        "suggestedPrompts": [
            "Use Team Orchestrator to plan a new SaaS product or feature",
            "Ask a specialist agent to review or implement a bounded task",
            "Run product discovery and define an MVP with measurable outcomes"
        ],
        "author": {"name": "AI Agent Ecosystem contributors"},
        "license": "MIT",
        "keywords": ["multi-agent", "orchestration", "architecture", "product-design", "frontend", "backend", "devops", "qa", "agent-skills"]
    }
    (destination / "plugin.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return [f"agents={agent_count}", f"skills={skill_count}", f"rules={rule_count}"]


def same_generated(temp: Path) -> list[str]:
    differences = []
    for relative in GENERATED:
        expected = temp / relative
        actual = ROOT / relative
        if expected.is_dir():
            if not actual.is_dir():
                differences.append(f"missing directory: {relative}")
                continue
            expected_files = {p.relative_to(expected) for p in expected.rglob("*") if p.is_file()}
            actual_files = {p.relative_to(actual) for p in actual.rglob("*") if p.is_file()}
            for rel in sorted(expected_files - actual_files): differences.append(f"missing: {relative}/{rel}")
            for rel in sorted(actual_files - expected_files): differences.append(f"unexpected: {relative}/{rel}")
            for rel in sorted(expected_files & actual_files):
                if (expected / rel).read_bytes() != (actual / rel).read_bytes():
                    differences.append(f"out of date: {relative}/{rel}")
        elif not actual.is_file():
            differences.append(f"missing file: {relative}")
        elif expected.read_bytes() != actual.read_bytes():
            differences.append(f"out of date: {relative}")
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated plugin files are out of date")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="ai-agent-build-") as tmp:
            temp = Path(tmp)
            try:
                stats = build(temp)
            except Exception as exc:
                print(f"BUILD FAILED: {exc}")
                return 1
            differences = same_generated(temp)
            if differences:
                print("PLUGIN BUNDLE OUT OF DATE")
                for item in differences: print(" -", item)
                print("Run: python scripts/build_single_plugin.py")
                return 1
            print("PLUGIN BUNDLE CURRENT:", ", ".join(stats))
            return 0

    for relative in GENERATED:
        target = ROOT / relative
        if target.is_dir(): shutil.rmtree(target)
        elif target.exists(): target.unlink()
    try:
        stats = build(ROOT)
    except Exception as exc:
        print(f"BUILD FAILED: {exc}")
        return 1
    print("BUILT SINGLE ANTIGRAVITY PLUGIN:", ", ".join(stats))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
