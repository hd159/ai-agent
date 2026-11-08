"""Positive and negative regression tests for the generic project quality gate."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_gate import Gate

NOW = "2026-11-08T12:00:00+07:00"


def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.eco = self.project / ".agent-ecosystem"
        self.exe = self.eco / "execution"
        for directory in ("tasks", "handoffs", "verification/evidence"):
            (self.exe / directory).mkdir(parents=True)
        self.task = {
            "task_id": "BE-001", "title": "Backend change", "owner": "backend-agent",
            "objective": "Implement and test an approved backend change", "inputs": [],
            "scope": ["backend"], "out_of_scope": ["deployment"],
            "dependencies": [], "owned_paths": ["src/backend.py"],
            "acceptance_criteria": ["Valid response is returned"],
            "verification": ["Run backend test"], "status": "completed",
            "completion_evidence": []
        }
        self.state = {
            "schema_version": "1.0.0", "project_id": "sample", "team_id": "saas-mvp", "status": "in_review",
            "updated_at": NOW, "last_checkpoint_at": NOW, "source_commit": None,
            "blockers": [], "pending_decisions": [],
            "tasks": [{"task_id": "BE-001", "status": "completed", "owner": "backend-agent", "evidence": [], "blockers": []}]
        }
        self.plan = {
            "schema_version": "1.0.0", "project_id": "sample", "team_id": "saas-mvp",
            "status": "active", "created_at": NOW, "updated_at": NOW, "phases": [],
            "approval_gates": [
                {"id": "architecture", "required": True, "description": "Approve architecture",
                 "status": "approved", "approved_at": NOW, "approved_by": "user"},
                {"id": "production_deployment", "required": True, "description": "Approve release",
                 "status": "approved", "approved_at": NOW, "approved_by": "user"}
            ]
        }
        self.team = {
            "schema_version": "1.0.0", "id": "saas-mvp", "name": "SaaS MVP Team", "version": "0.3.0",
            "orchestrator": "team-orchestrator", "shared_modules": [],
            "members": [
                {"agent": "backend-agent", "module": "backend-agent", "role": "backend-engineering", "required": True},
                {"agent": "qa-agent", "module": "qa-agent", "role": "quality-engineering", "required": True}
            ],
            "workflow": [], "approval_gates": [],
            "execution_policy": {"max_parallel_agents": 2, "parallelism": "dependency-aware",
                "one_owner_per_task": True, "disallow_overlapping_owned_paths": True,
                "stop_dependent_tasks_on_failure": True, "completion_requires_evidence": True}
        }
        save(self.exe / "tasks/BE-001.json", self.task)
        save(self.exe / "state.json", self.state)
        save(self.exe / "plan.json", self.plan)
        save(self.eco / "team.json", self.team)
        (self.project / "src").mkdir()
        (self.project / "src/backend.py").write_text("print('ok')\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.org")
        self.git("config", "user.name", "Test User")
        self.git("add", "src/backend.py")
        self.git("commit", "-qm", "implementation")
        self.sha = self.git("rev-parse", "HEAD").stdout.strip()
        self.evidence = ".agent-ecosystem/execution/verification/evidence/backend-test.log"
        (self.project / self.evidence).write_text("1 test passed\n", encoding="utf-8")
        self.report = {
            "schema_version": "1.0.0", "task_id": "BE-001",
            "implementation_agent": "backend-agent", "reviewer_agent": "qa-agent", "reviewed_at": NOW,
            "review_status": "approved", "source_commit": self.sha,
            "checks": [{"id": "test-1", "kind": "test", "result": "passed", "executed_at": NOW,
                        "environment": "isolated", "command": "python -m unittest", "exit_code": 0,
                        "evidence_paths": [self.evidence]}],
            "acceptance_results": [{"criterion": "Valid response is returned", "result": "passed", "check_ids": ["test-1"]}]
        }
        self.write_report()

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.project), *args], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)
        return result

    def write_report(self):
        save(self.exe / "verification/BE-001.json", self.report)

    def check(self, mode="task"):
        gate = Gate(self.project)
        gate.validate(mode, "BE-001" if mode == "task" else None)
        return gate.errors

    def test_valid_task_and_release_pass(self):
        self.assertEqual(self.check(), [])
        self.assertEqual(self.check("validate"), [])
        self.assertEqual(self.check("release"), [])

    def test_missing_evidence_fails(self):
        (self.exe / "verification/BE-001.json").unlink()
        self.assertTrue(any("Missing" in e for e in self.check("validate")))

    def test_fabricated_pass_with_nonzero_exit_fails(self):
        self.report["checks"][0]["exit_code"] = 1
        self.write_report()
        self.assertTrue(any("successful exit code" in e for e in self.check()))

    def test_reviewer_must_be_independent(self):
        self.report["reviewer_agent"] = "backend-agent"
        self.write_report()
        self.assertTrue(any("independent reviewer" in e for e in self.check()))

    def test_reviewer_must_be_team_qa(self):
        self.report["reviewer_agent"] = "frontend-agent"
        self.write_report()
        self.assertTrue(any("not a configured QA agent" in e for e in self.check()))

    def test_team_must_configure_independent_qa(self):
        self.team["members"] = [m for m in self.team["members"] if m["agent"] != "qa-agent"]
        save(self.eco / "team.json", self.team)
        self.assertTrue(any("configured independent QA specialist required" in e for e in self.check()))

    def test_failed_extra_check_blocks_approved_review(self):
        self.report["checks"].append({
            "id": "regression", "kind": "test", "result": "failed", "executed_at": NOW,
            "command": "python -m unittest regression", "exit_code": 1, "evidence_paths": [self.evidence]
        })
        self.write_report()
        self.assertTrue(any("approved QA report contains failed/blocked" in e for e in self.check()))

    def test_qa_review_must_approve(self):
        self.report["review_status"] = "changes_requested"
        self.write_report()
        self.assertTrue(any("has not approved" in e for e in self.check()))

    def test_unverified_criterion_fails(self):
        self.report["acceptance_results"][0]["result"] = "not_run"
        self.write_report()
        self.assertTrue(any("not independently verified" in e for e in self.check()))

    def test_missing_evidence_log_fails(self):
        (self.project / self.evidence).unlink()
        self.assertTrue(any("missing or empty evidence" in e for e in self.check()))

    def test_evidence_path_traversal_fails(self):
        self.report["checks"][0]["evidence_paths"] = ["../../secrets.txt"]
        self.write_report()
        self.assertTrue(any("unsafe evidence path" in e for e in self.check()))

    def test_git_drift_invalidates_evidence(self):
        (self.project / "src/backend.py").write_text("print('changed')\n", encoding="utf-8")
        self.git("add", "src/backend.py")
        self.git("commit", "-qm", "change after test")
        self.assertTrue(any("stale evidence" in e for e in self.check()))

    def test_dirty_source_invalidates_evidence(self):
        (self.project / "src/backend.py").write_text("print('uncommitted')\n", encoding="utf-8")
        self.assertTrue(any("uncommitted" in e for e in self.check()))

    def test_state_status_mismatch_fails(self):
        self.state["tasks"][0]["status"] = "in_progress"
        save(self.exe / "state.json", self.state)
        self.assertTrue(any("state status" in e for e in self.check("validate")))

    def test_release_requires_explicit_approval(self):
        self.plan["approval_gates"][1].update(status="pending", approved_by=None, approved_at=None)
        save(self.exe / "plan.json", self.plan)
        self.assertEqual(self.check(), [])
        self.assertTrue(any("production_deployment not approved" in e for e in self.check("release")))

    def test_task_schema_requires_dependencies(self):
        self.task.pop("dependencies")
        save(self.exe / "tasks/BE-001.json", self.task)
        self.assertTrue(any("dependencies" in e for e in self.check("validate")))

    def test_dependency_must_exist(self):
        self.task["dependencies"] = ["ARCH-099"]
        save(self.exe / "tasks/BE-001.json", self.task)
        self.assertTrue(any("missing dependency" in e for e in self.check("validate")))

    def test_criteria_must_link_passing_check(self):
        self.report["checks"][0]["result"] = "not_run"
        self.write_report()
        self.assertTrue(any("non-passing/missing checks" in e for e in self.check()))


if __name__ == "__main__":
    unittest.main()
