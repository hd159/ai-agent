#!/usr/bin/env python3
"""Fail-closed quality gates for project-local AI Agent Ecosystem work.

Validation checks versioned artifacts and Git provenance; it does not attest that
an agent really ran a command. Require protected CI checks for trusted execution.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("ERROR: Install quality gate dependencies: python -m pip install -r requirements-dev.txt", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "contracts" / "schemas"


class Gate:
    def __init__(self, project: Path):
        self.project = project.resolve()
        self.eco = self.project / ".agent-ecosystem"
        self.execution = self.eco / "execution"
        self.errors: list[str] = []

    def error(self, message: str):
        self.errors.append(message)

    def read(self, path: Path, schema_name: str | None = None):
        if not path.is_file():
            self.error(f"Missing {path.relative_to(self.project) if path.is_relative_to(self.project) else path}")
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            self.error(f"Invalid JSON {path}: {exc}")
            return None
        if schema_name is not None:
            schema = json.loads((SCHEMAS / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            for issue in sorted(validator.iter_errors(data), key=lambda e: str(e.path)):
                loc = ".".join(map(str, issue.path)) or "root"
                self.error(f"{path.relative_to(self.project)} [{loc}]: {issue.message}")
        return data

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", "-C", str(self.project), *args], capture_output=True, text=True, check=False)

    def tasks_and_state(self):
        state = self.read(self.execution / "state.json", "execution-state")
        plan = self.read(self.execution / "plan.json", "project-plan")
        team = self.read(self.eco / "team.json", "team")
        tasks: dict[str, dict] = {}
        for path in sorted((self.execution / "tasks").glob("*.json")):
            t = self.read(path, "task")
            if not isinstance(t, dict):
                continue
            task_id = t.get("task_id")
            if task_id in tasks:
                self.error(f"Duplicate task_id: {task_id}")
            elif isinstance(task_id, str):
                tasks[task_id] = t
            if path.stem != task_id:
                self.error(f"{path}: filename must match task_id")
        if not isinstance(state, dict) or not isinstance(plan, dict) or not isinstance(team, dict):
            return {}, state, plan, team
        for obj, label in ((plan, "plan"), (state, "state")):
            if obj.get("project_id") != state.get("project_id") or obj.get("team_id") != state.get("team_id"):
                self.error(f"{label} project_id/team_id disagree with state")
        if team.get("id") != state.get("team_id"):
            self.error("team.json id disagrees with state team_id")
        state_tasks: dict[str, dict] = {}
        for t in state.get("tasks", []):
            task_id = t.get("task_id")
            if task_id in state_tasks:
                self.error(f"Duplicate task in state.json: {task_id}")
            state_tasks[task_id] = t
        for task_id, task in tasks.items():
            snap = state_tasks.get(task_id)
            if snap is None:
                self.error(f"Task {task_id} missing from state.json")
                continue
            if snap.get("status") != task.get("status"):
                self.error(f"Task {task_id}: state status {snap.get('status')} != contract status {task.get('status')}")
            if snap.get("owner") not in (None, task.get("owner")):
                self.error(f"Task {task_id}: state owner does not match contract owner")
            for dep in task.get("dependencies", []):
                if dep not in tasks:
                    self.error(f"Task {task_id}: missing dependency {dep}")
                elif task.get("status") == "completed" and tasks[dep].get("status") != "completed":
                    self.error(f"Task {task_id}: completed while dependency {dep} is not completed")
        for task_id in state_tasks:
            if task_id not in tasks:
                self.error(f"State references unknown task {task_id}")
        visited: set[str] = set()
        active: set[str] = set()
        def visit(task_id: str):
            if task_id in active:
                self.error(f"Dependency cycle involving {task_id}")
                return
            if task_id in visited:
                return
            active.add(task_id)
            for dep in tasks[task_id].get("dependencies", []):
                if dep in tasks:
                    visit(dep)
            active.remove(task_id)
            visited.add(task_id)
        for task_id in tasks:
            visit(task_id)
        gate_ids = [g.get("id") for g in plan.get("approval_gates", [])]
        if len(gate_ids) != len(set(gate_ids)):
            self.error("Duplicate approval gate IDs")
        for gate in plan.get("approval_gates", []):
            if gate.get("status") == "approved" and (not gate.get("approved_by") or not gate.get("approved_at")):
                self.error(f"Approval {gate.get('id')} missing approved_by or approved_at")
        for path in sorted((self.execution / "handoffs").glob("*.json")):
            handoff = self.read(path, "handoff")
            if isinstance(handoff, dict):
                if handoff.get("task_id") not in tasks:
                    self.error(f"Handoff {path.name} references unknown task")
                elif handoff.get("from_agent") != tasks[handoff["task_id"]].get("owner"):
                    self.error(f"Handoff {path.name} sender does not own task")
        return tasks, state, plan, team

    def check_evidence_path(self, evidence: str, task_id: str):
        p = Path(evidence)
        if p.is_absolute() or ".." in p.parts or not evidence.startswith(".agent-ecosystem/execution/verification/evidence/"):
            self.error(f"Task {task_id}: unsafe evidence path {evidence!r}")
            return
        resolved = (self.project / p).resolve()
        if not resolved.is_relative_to(self.execution.resolve()):
            self.error(f"Task {task_id}: evidence outside project execution directory: {evidence}")
        elif not resolved.is_file() or resolved.stat().st_size == 0:
            self.error(f"Task {task_id}: missing or empty evidence {evidence}")

    def verify_task(self, task: dict, team: dict | None = None):
        task_id = task["task_id"]
        if task.get("status") not in ("in_review", "completed"):
            self.error(f"Task {task_id}: only in_review/completed tasks can pass completion gate")
        report = self.read(self.execution / "verification" / f"{task_id}.json", "verification")
        if not isinstance(report, dict):
            return
        if report.get("task_id") != task_id or report.get("implementation_agent") != task.get("owner"):
            self.error(f"Task {task_id}: report task ID/implementation agent mismatch")
        reviewer = report.get("reviewer_agent")
        if not reviewer or reviewer == task.get("owner"):
            self.error(f"Task {task_id}: independent reviewer required")
        qa_agents = {m.get("agent") for m in (team or {}).get("members", []) if m.get("role") == "quality-engineering"}
        if not qa_agents:
            self.error(f"Task {task_id}: configured independent QA specialist required")
        elif reviewer not in qa_agents:
            self.error(f"Task {task_id}: reviewer {reviewer} is not a configured QA agent")
        if report.get("review_status") != "approved":
            self.error(f"Task {task_id}: independent QA review has not approved completion")
        source = report.get("source_commit") or ""
        if not (isinstance(source, str) and len(source) == 40 and all(x in "0123456789abcdef" for x in source)):
            self.error(f"Task {task_id}: source_commit must be a full lowercase Git SHA")
        else:
            ancestor = self.git("merge-base", "--is-ancestor", source, "HEAD")
            if ancestor.returncode:
                self.error(f"Task {task_id}: source commit is not an ancestor of HEAD")
            else:
                changed = self.git("diff", "--name-only", source, "HEAD")
                if changed.returncode:
                    self.error(f"Task {task_id}: cannot inspect Git diff after source commit")
                else:
                    stale = [x for x in changed.stdout.splitlines() if x and not x.startswith(".agent-ecosystem/")]
                    if stale:
                        self.error(f"Task {task_id}: stale evidence, code changed after {source[:8]}: {', '.join(stale[:5])}")
        dirty = self.git("status", "--porcelain", "--untracked-files=all")
        if dirty.returncode:
            self.error(f"Task {task_id}: cannot inspect Git working tree")
        else:
            changes = [line[3:] for line in dirty.stdout.splitlines() if line.strip()]
            dirty_code = [p for p in changes if not p.startswith(".agent-ecosystem/")]
            if dirty_code:
                self.error(f"Task {task_id}: uncommitted application/test files invalidate evidence: {', '.join(dirty_code[:5])}")
        checks: dict[str, dict] = {}
        for check in report.get("checks", []):
            ident = check.get("id")
            if ident in checks:
                self.error(f"Task {task_id}: duplicate verification check {ident}")
            checks[ident] = check
            if check.get("result") in ("failed", "blocked") and report.get("review_status") == "approved":
                self.error(f"Task {task_id}: approved QA report contains failed/blocked check {ident}")
            if check.get("result") == "passed":
                if check.get("kind") != "inspection" and (not check.get("command") or check.get("exit_code") != 0):
                    self.error(f"Task {task_id}: passed executable check {ident} missing command or successful exit code")
                if not check.get("evidence_paths"):
                    self.error(f"Task {task_id}: passed check {ident} missing file evidence")
                for path in check.get("evidence_paths", []):
                    self.check_evidence_path(path, task_id)
        criteria = task.get("acceptance_criteria", [])
        results: dict[str, dict] = {}
        for item in report.get("acceptance_results", []):
            criterion = item.get("criterion")
            if criterion in results:
                self.error(f"Task {task_id}: duplicate acceptance result {criterion!r}")
            results[criterion] = item
        for criterion in criteria:
            result = results.get(criterion)
            if not result or result.get("result") != "passed":
                self.error(f"Task {task_id}: criterion not independently verified: {criterion!r}")
                continue
            ids = result.get("check_ids", [])
            if not ids or any(checks.get(i, {}).get("result") != "passed" for i in ids):
                self.error(f"Task {task_id}: criterion {criterion!r} references non-passing/missing checks")
        if set(results) - set(criteria):
            self.error(f"Task {task_id}: report contains unknown acceptance criteria")
        if not any(ch.get("result") == "passed" for ch in checks.values()):
            self.error(f"Task {task_id}: no passing executed checks")

    def validate(self, mode: str, task_id: str | None):
        tasks, state, plan, team = self.tasks_and_state()
        if mode == "task":
            if task_id not in tasks:
                self.error(f"Unknown task {task_id!r}")
            else:
                self.verify_task(tasks[task_id], team)
        else:
            for task in tasks.values():
                if task.get("status") == "completed":
                    self.verify_task(task, team)
        if mode == "release":
            if not tasks:
                self.error("Release requires at least one implemented task")
            for task in tasks.values():
                if task.get("status") != "completed":
                    self.error(f"Release blocked: task {task['task_id']} is not completed")
            if isinstance(state, dict):
                if state.get("blockers") or state.get("pending_decisions"):
                    self.error("Release blocked by unresolved blockers/decisions")
                if state.get("status") not in ("in_review", "completed"):
                    self.error("Release requires project status in_review or completed")
            if isinstance(plan, dict):
                gates = {g.get("id"): g for g in plan.get("approval_gates", [])}
                prod = gates.get("production_deployment")
                if not prod or not prod.get("required"):
                    self.error("Release requires a mandatory production_deployment approval gate")
                for gate in gates.values():
                    if gate.get("required") and gate.get("status") != "approved":
                        self.error(f"Release blocked: required approval {gate.get('id')} not approved")
        return not self.errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["validate", "task", "release"])
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--task-id", help="Required for task mode")
    args = parser.parse_args()
    if args.mode == "task" and not args.task_id:
        parser.error("task mode requires --task-id")
    gate = Gate(args.project)
    good = gate.validate(args.mode, args.task_id)
    if good:
        print(f"PASS: {args.mode} quality gate for {gate.project}")
        return 0
    print(f"FAIL: {args.mode} quality gate ({len(gate.errors)} error(s))", file=sys.stderr)
    for error in gate.errors:
        print(f" - {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
