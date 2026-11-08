#!/usr/bin/env python3
"""Bootstrap project context, plan, execution state, and memory folders."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def project_slug(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return value or "project"


def current_git_commit(target: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def copy_tree(source: Path, target: Path) -> None:
    for item in source.rglob("*"):
        if not item.is_file():
            continue
        relative = item.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {destination}")
        shutil.copy2(item, destination)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team", required=True)
    parser.add_argument("--target", required=True, type=Path)
    args = parser.parse_args()

    team_file = ROOT / "teams" / args.team / "team.json"
    if not team_file.is_file():
        print(f"Team preset not found: {args.team}")
        return 2

    target = args.target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    eco = target / ".agent-ecosystem"
    if eco.exists() and any(eco.iterdir()):
        print(f"Refusing to overwrite non-empty directory: {eco}")
        return 2

    team = json.loads(team_file.read_text(encoding="utf-8"))
    now = timestamp()
    project_id = project_slug(target.name)

    eco.mkdir(parents=True, exist_ok=True)
    shutil.copy2(team_file, eco / "team.json")
    shutil.copy2(ROOT / "templates/project/PROJECT_CONTEXT.md", eco / "PROJECT_CONTEXT.md")

    artifacts = eco / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    copy_tree(ROOT / "templates/artifacts", artifacts)

    execution = eco / "execution"
    for folder in ("tasks", "handoffs", "sessions", "decisions"):
        (execution / folder).mkdir(parents=True, exist_ok=True)

    workflow = team.get("workflow", [])
    phases = [
        {
            "phase_id": phase["id"],
            "status": "pending",
            "mode": phase["mode"],
            "agents": phase.get("agents", []),
            "approval_gate": phase.get("approval_gate"),
        }
        for phase in workflow
    ]
    approval_gates = [
        {
            "id": gate["id"],
            "required": gate["required"],
            "description": gate["description"],
            "status": "pending",
            "approved_at": None,
            "approved_by": None,
        }
        for gate in team.get("approval_gates", [])
    ]

    plan = {
        "schema_version": "1.0.0",
        "project_id": project_id,
        "team_id": args.team,
        "goal": None,
        "status": "planning",
        "created_at": now,
        "updated_at": now,
        "phases": phases,
        "approval_gates": approval_gates,
    }
    state = {
        "schema_version": "1.0.0",
        "project_id": project_id,
        "team_id": args.team,
        "status": "planning",
        "current_phase": phases[0]["phase_id"] if phases else "discovery",
        "current_focus": None,
        "updated_at": now,
        "last_checkpoint_at": now,
        "last_session_id": None,
        "source_commit": current_git_commit(target),
        "blockers": [],
        "pending_decisions": [],
        "next_actions": [
            "Complete .agent-ecosystem/PROJECT_CONTEXT.md.",
            "Review the project architecture and record the current baseline.",
            "Create the first approved project plan and task contracts.",
        ],
        "tasks": [],
    }

    write_json(execution / "plan.json", plan)
    write_json(execution / "state.json", state)
    shutil.copy2(
        ROOT / "templates/project/execution/SESSION_TEMPLATE.md",
        execution / "sessions/SESSION_TEMPLATE.md",
    )
    shutil.copy2(
        ROOT / "templates/project/EXECUTION_README.md",
        execution / "README.md",
    )

    print(f"Bootstrapped team '{args.team}' into: {eco}")
    print("Created PROJECT_CONTEXT.md, plan.json, state.json, task/handoff/session folders, and a session template.")
    print("Next: complete PROJECT_CONTEXT.md, open the target project in Antigravity, and start Team Orchestrator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
