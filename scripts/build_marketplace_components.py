#!/usr/bin/env python3
"""Build and verify generated Cursor Marketplace components from canonical sources."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from adapter_support import ROOT, build_adapter

MARKER = ".generated-by-ai-agent-ecosystem.json"


def build_cursor_components(root: Path = ROOT, destination: Path | None = None, check: bool = False) -> list[str]:
    root = root.resolve()
    raw_destination = destination or root / "plugins" / "ai-agent-ecosystem"
    if raw_destination.is_symlink():
        return [f"refusing symlink destination: {raw_destination}"]
    destination = raw_destination.resolve()
    errors: list[str] = []

    if destination.exists() and not destination.is_dir():
        return [f"destination is not a directory: {destination}"]

    with tempfile.TemporaryDirectory(prefix="ai-agent-marketplace-") as temporary:
        bundle = Path(temporary) / "cursor"
        try:
            build_adapter(root, "cursor", bundle)
        except Exception as exc:
            return [f"cannot build canonical Cursor adapter: {exc}"]

        expected: dict[str, bytes] = {}
        source_agents = bundle / ".cursor" / "agents"
        source_rule = bundle / ".cursor" / "rules" / "ai-agent-ecosystem.mdc"
        for path in sorted(source_agents.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            content = content.replace(
                "Use the custom profiles in .cursor/agents/",
                "Use the custom profiles in agents/",
            )
            expected[f"agents/{path.name}"] = content.encode("utf-8")
        if not source_rule.is_file():
            return ["canonical Cursor adapter did not generate ai-agent-ecosystem.mdc"]
        rule_content = source_rule.read_text(encoding="utf-8")
        rule_content = rule_content.replace(
            "under .cursor/skills/ and load only the relevant SKILL.md files.",
            "under skills/ and load only the relevant SKILL.md files.",
        )
        expected["rules/ai-agent-ecosystem.mdc"] = rule_content.encode("utf-8")
        source_skills = bundle / ".cursor" / "skills"
        for skill_file in sorted(source_skills.glob("*/SKILL.md")):
            expected[f"skills/{skill_file.parent.name}/SKILL.md"] = skill_file.read_bytes()
        generated = {
            "generator": "scripts/build_marketplace_components.py",
            "ecosystem_version": json.loads((root / "ecosystem.json").read_text(encoding="utf-8"))["version"],
            "agents": sorted(path.stem for path in source_agents.glob("*.md")),
            "rules": ["ai-agent-ecosystem.mdc"],
            "skills": sorted(path.parent.name for path in source_skills.glob("*/SKILL.md")),
        }
        expected[MARKER] = (json.dumps(generated, indent=2) + "\n").encode("utf-8")

        if check:
            if not destination.is_dir():
                return [f"generated plugin directory is missing: {destination}"]
            actual = {
                path.relative_to(destination).as_posix()
                for path in destination.rglob("*")
                if path.is_file()
            }
            if actual != set(expected):
                errors.append(
                    f"generated file inventory mismatch: missing={sorted(set(expected) - actual)}, "
                    f"unexpected={sorted(actual - set(expected))}"
                )
            for relative, content in expected.items():
                path = destination / relative
                if not path.is_file() or path.read_bytes() != content:
                    errors.append(f"generated Cursor component is stale or missing: {relative}")
            return errors

        if destination.exists():
            marker = destination / MARKER
            if not marker.is_file():
                return [f"refusing to overwrite unmanaged directory: {destination}"]
            try:
                previous = json.loads(marker.read_text(encoding="utf-8"))
            except Exception as exc:
                return [f"invalid generated ownership marker: {exc}"]
            if previous.get("generator") != generated["generator"]:
                return [f"generated ownership marker mismatch: {destination}"]
            actual = {
                path.relative_to(destination).as_posix()
                for path in destination.rglob("*")
                if path.is_file()
            }
            unexpected = actual - set(expected)
            if unexpected:
                return [f"refusing to delete unowned files: {sorted(unexpected)}"]
            for name in ("agents", "rules", "skills"):
                child = destination / name
                if child.is_symlink():
                    return [f"refusing to replace symlink: {child}"]
                if child.exists():
                    if not child.is_dir():
                        return [f"generated path is not a directory: {child}"]
                    shutil.rmtree(child)
        else:
            destination.mkdir(parents=True)

        for relative, content in expected.items():
            target = destination / relative
            if target.is_symlink():
                return [f"refusing to write through symlink: {target}"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--check", action="store_true", help="fail if committed Cursor components are stale")
    args = parser.parse_args()
    errors = build_cursor_components(args.root, args.output, check=args.check)
    if errors:
        print("MARKETPLACE COMPONENT BUILD FAILED" if not args.check else "MARKETPLACE COMPONENT CHECK FAILED")
        for error in errors:
            print("ERROR:", error)
        return 1
    print("MARKETPLACE COMPONENTS VERIFIED" if args.check else "MARKETPLACE COMPONENTS BUILT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
