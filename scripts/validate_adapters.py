#!/usr/bin/env python3
"""Build adapters in a temporary directory and validate native layouts and contracts."""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from adapter_support import ADAPTERS, LAYOUTS, ROOT, build_all_adapters


def _frontmatter(text: str) -> tuple[str, str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    name = ""
    description = ""
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
        if line.startswith("description:"):
            description = line.split(":", 1)[1].strip().strip('"')
    return name, description, text[end + 4:].strip()


def validate(root: Path = ROOT) -> tuple[list[str], dict]:
    errors = []
    stats = {"adapters": 0, "agents_per_adapter": 0, "skills_per_adapter": 0}
    policy = json.loads((root / "contracts/agent-tool-policy.json").read_text(encoding="utf-8"))
    platform_contract = json.loads((root / "contracts/platform-adapters.json").read_text(encoding="utf-8"))
    catalog = json.loads((root / "ecosystem.json").read_text(encoding="utf-8"))
    expected_agents = set(policy.get("agents", []))
    if platform_contract.get("ecosystem_version") != catalog.get("version"):
        errors.append("platform-adapters.json ecosystem_version does not match ecosystem.json")
    for adapter in ADAPTERS:
        declared = platform_contract.get("adapters", {}).get(adapter, {})
        catalog_adapter = catalog.get("adapters", {}).get(adapter, {})
        layout = LAYOUTS[adapter]
        if declared.get("version") != catalog_adapter.get("version"):
            errors.append(f"{adapter}: platform-adapters.json version mismatch")
        if declared.get("instructions_file") != layout["instructions"]:
            errors.append(f"{adapter}: platform-adapters.json instructions path mismatch")
        if declared.get("agent_directory", "").rstrip("/") != layout["agents"]:
            errors.append(f"{adapter}: platform-adapters.json agent directory mismatch")
        if declared.get("skill_directory", "").rstrip("/") != layout["skills"]:
            errors.append(f"{adapter}: platform-adapters.json skill directory mismatch")
        expected_instruction_mode = "managed-block" if layout.get("merge_instructions", True) else "exclusive-managed-file"
        if declared.get("instruction_mode", "managed-block") != expected_instruction_mode:
            errors.append(f"{adapter}: platform-adapters.json instruction mode mismatch")
    expected_skills = {path.parent.name for path in (root / "modules").glob("*/skills/*/SKILL.md")}

    with tempfile.TemporaryDirectory(prefix="ai-agent-adapter-validation-") as temporary:
        output = Path(temporary)
        try:
            build_all_adapters(root, output)
        except Exception as exc:
            return [f"adapter build failed: {exc}"], stats

        for adapter in ADAPTERS:
            stats["adapters"] += 1
            layout = LAYOUTS[adapter]
            bundle = output / adapter
            manifest_path = bundle / "adapter.json"
            if not manifest_path.is_file():
                errors.append(f"{adapter}: missing adapter.json")
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("adapter") != adapter:
                errors.append(f"{adapter}: adapter manifest identity mismatch")
            if set(manifest.get("agents", [])) != expected_agents:
                errors.append(f"{adapter}: manifest agent inventory mismatch")
            if set(manifest.get("skills", [])) != expected_skills:
                errors.append(f"{adapter}: manifest skill inventory mismatch")

            instructions = bundle / layout["instructions"]
            if not instructions.is_file():
                errors.append(f"{adapter}: missing native instructions file {layout['instructions']}")
            else:
                content = instructions.read_text(encoding="utf-8")
                for required in ("Universal Agent Constitution", "Persistent project memory", "capability-smoke-test"):
                    if required not in content:
                        errors.append(f"{adapter}: instructions missing {required}")
                if adapter == "cursor":
                    if not content.startswith("---\n"):
                        errors.append("cursor: native MDC rule must begin with YAML frontmatter")
                    if "description: Shared AI Agent Ecosystem instructions" not in content:
                        errors.append("cursor: MDC rule is missing its description")
                    if "alwaysApply: true" not in content:
                        errors.append("cursor: MDC rule must alwaysApply")
                    if content.count("\n---\n") < 1:
                        errors.append("cursor: MDC rule frontmatter is not closed")

            agent_dir = bundle / layout["agents"]
            agent_files = list(agent_dir.glob(f"*{layout['extension']}")) if agent_dir.is_dir() else []
            names = {path.name.removesuffix(layout["extension"]) for path in agent_files}
            if names != expected_agents:
                errors.append(f"{adapter}: native agent profile inventory mismatch")
            stats["agents_per_adapter"] = len(agent_files)

            for path in agent_files:
                text = path.read_text(encoding="utf-8")
                if adapter == "codex":
                    if tomllib is None:
                        errors.append("Codex TOML validation requires Python 3.11+ or tomli")
                        break
                    try:
                        profile = tomllib.loads(text)
                    except Exception as exc:
                        errors.append(f"{path.relative_to(bundle)}: invalid TOML: {exc}")
                        continue
                    if not all(isinstance(profile.get(key), str) and profile[key].strip()
                               for key in ("name", "description", "developer_instructions")):
                        errors.append(f"{path.relative_to(bundle)}: missing required Codex agent fields")
                    body = profile.get("developer_instructions", "")
                else:
                    try:
                        name, description, body = _frontmatter(text)
                    except ValueError as exc:
                        errors.append(f"{path.relative_to(bundle)}: {exc}")
                        continue
                    if name != path.name.removesuffix(layout["extension"]) or not description:
                        errors.append(f"{path.relative_to(bundle)}: invalid native agent frontmatter")
                    if adapter == "copilot" and "include-custom-instructions: true" not in text:
                        errors.append(f"{path.relative_to(bundle)}: Copilot subagents must include repository custom instructions")
                if not body.strip():
                    errors.append(f"{path.relative_to(bundle)}: empty native agent instructions")
                if "commandExecutionPolicy:" in text or "inheritCustomizations:" in text:
                    errors.append(f"{path.relative_to(bundle)}: Antigravity-only frontmatter leaked into native adapter")

            skill_dir = bundle / layout["skills"]
            installed_skills = {path.parent.name for path in skill_dir.glob("*/SKILL.md")} if skill_dir.is_dir() else set()
            if installed_skills != expected_skills:
                errors.append(f"{adapter}: native skill inventory mismatch")
            stats["skills_per_adapter"] = len(installed_skills)
            for skill in expected_skills & installed_skills:
                source_files = sorted((root / "modules").glob(f"*/skills/{skill}/**/*"))
                source_files = [path for path in source_files if path.is_file()]
                for source in source_files:
                    skill_root = next(parent for parent in source.parents if parent.name == skill)
                    relative = source.relative_to(skill_root)
                    target = skill_dir / skill / relative
                    if not target.is_file() or target.read_bytes() != source.read_bytes():
                        errors.append(f"{adapter}: skill payload mismatch for {skill}/{relative}")

    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors, stats = validate(args.root.resolve())
    if errors:
        print("ADAPTER VALIDATION FAILED")
        for error in errors:
            print("ERROR:", error)
        return 1
    print(
        f"ADAPTER VALIDATION PASSED: {stats['adapters']} adapters, "
        f"{stats['agents_per_adapter']} agents and {stats['skills_per_adapter']} skills per adapter"
    )
    print("Static validation only; host runtime permissions and delegation require live smoke tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
