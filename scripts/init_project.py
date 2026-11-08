#!/usr/bin/env python3
"""Bootstrap team configuration and artifact templates into an application workspace."""
from pathlib import Path
import argparse, json, shutil, sys

ROOT = Path(__file__).resolve().parents[1]

def copy_tree(source, target):
    for item in source.rglob("*"):
        if item.is_dir():
            continue
        rel = item.relative_to(source)
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {destination}")
        shutil.copy2(item, destination)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", required=True)
    parser.add_argument("--target", required=True, type=Path)
    args = parser.parse_args()

    team_file = ROOT / "teams" / args.team / "team.json"
    if not team_file.exists():
        print(f"Team preset not found: {args.team}")
        return 2

    target = args.target.resolve()
    eco = target / ".agent-ecosystem"
    if eco.exists() and any(eco.iterdir()):
        print(f"Refusing to overwrite non-empty directory: {eco}")
        return 2

    eco.mkdir(parents=True, exist_ok=True)
    shutil.copy2(team_file, eco / "team.json")
    shutil.copy2(ROOT / "templates/project/PROJECT_CONTEXT.md", eco / "PROJECT_CONTEXT.md")

    artifacts = eco / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    for file in (ROOT / "templates/artifacts").glob("*.md"):
        shutil.copy2(file, artifacts / file.name)

    execution = eco / "execution"
    (execution / "tasks").mkdir(parents=True, exist_ok=True)
    (execution / "handoffs").mkdir(parents=True, exist_ok=True)
    (eco / "execution/README.md").write_text(
        "# Execution State\\n\\nStore plan.json, state.json, task contracts, and handoff records here.\\n",
        encoding="utf-8"
    )

    print(f"Bootstrapped team '{args.team}' into: {eco}")
    print("Next: fill PROJECT_CONTEXT.md, open the project in Antigravity, and start Team Orchestrator.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
