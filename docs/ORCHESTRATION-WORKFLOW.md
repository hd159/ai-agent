# Orchestration Workflow

This document defines how Team Orchestrator turns a user request into bounded specialist work and maintains reliable execution state.

## 1. Operating principles

1. One coordinator: Team Orchestrator owns the overall plan and is the single writer of execution/state.json.
2. One task owner: every task has one accountable specialist.
3. Explicit contracts: scope, exclusions, dependencies, owned paths, acceptance criteria, and verification are mandatory.
4. Dependency-aware parallelism: dispatch only tasks whose inputs and dependencies are ready.
5. No overlapping writes: parallel tasks must not own the same file or overlapping directory paths.
6. Evidence-based completion: agent self-report is not sufficient.
7. Human approval: respect product, architecture, data migration, security, and production approval gates.
8. Honest dispatch: distinguish planned, ready, dispatched, and in-progress work.

## 2. Request classification

At the start of a request, classify it:

| Request type | Default workflow |
|---|---|
| New project | Discovery → MVP scope → architecture → contracts → implementation |
| Existing project onboarding | Memory recovery → Git/source reconciliation → architecture baseline |
| Feature | Requirement → architecture/UX as needed → contracts → implementation → QA |
| Bug | Reproduce → root cause → regression test → smallest fix → QA |
| Refactor | Baseline tests → bounded plan → incremental change → regression |
| Architecture/security review | Read-only inspection → evidence-backed findings → decisions → approval |
| Release/deployment | Readiness review → rollback and operations checks → explicit approval |

Do not force every small bug fix through a full architecture process. If no discovery/MVP scope design has already been explicitly approved, still present a concise scope/design and obtain approval before writing application code or dispatching implementation, regardless of perceived simplicity.

## 2.1 Discovery and MVP approval gate

Before detailed requirements questions, check whether the request spans multiple independent subsystems (for example auth + billing + analytics + chat). If it does not fit one cohesive specification, pause and propose 2–3 concrete sub-project decompositions with trade-offs and a recommendation. Ask at most one question to confirm the first phase, then scope only that first sub-project.

During discovery and MVP scoping:

- Ask at most one question per message. Prefer A/B/C options when practical and use an open question when options would prematurely constrain intent.
- Present 2–3 concrete approaches, material trade-offs, and a clear recommendation whenever proposing a design or scope direction.
- Do not write application code, scaffold implementation files, or dispatch implementation tasks until the discovery/MVP scope design has been presented and explicitly approved by the user. This applies regardless of perceived task simplicity.
- Record canonical domain terminology in PROJECT_CONTEXT.md or the existing GLOSSARY.md as soon as terms are agreed.

## 3. Startup and resume protocol

Before continuing an existing project, read:

1. .agent-ecosystem/PROJECT_CONTEXT.md and team.json.
2. execution/state.json and execution/plan.json.
3. Current architecture baseline and relevant ADRs.
4. Active task contracts and unresolved handoffs.
5. Latest session checkpoint.
6. Current Git branch, HEAD, working tree, and source paths relevant to the request.

Reconcile old memory with current source. Report stale checkpoints, uncommitted changes, mismatched task statuses, blockers, and pending approvals before changing code.

## 4. Task contract

Each task is stored as a separate JSON file under execution/tasks/ and should contain:

~~~json
{
  "task_id": "BE-001",
  "title": "Implement progress API",
  "owner": "backend-agent",
  "objective": "Expose the approved learner progress contract.",
  "inputs": ["Approved architecture", "API contract"],
  "scope": ["Implement route and domain service", "Add tests"],
  "out_of_scope": ["Change subscription semantics"],
  "dependencies": ["ARCH-001"],
  "owned_paths": ["server/src/modules/progress/"],
  "acceptance_criteria": ["Authorization is enforced", "Contract tests pass"],
  "verification": ["Run backend unit and integration tests"],
  "status": "ready_for_dispatch"
}
~~~

Use the repository's task schema as the authoritative contract. Add only schema-supported fields or update the schema deliberately when the contract format changes.

## 5. Task lifecycle

~~~text
pending
  ├── blocked
  └── ready_for_dispatch
         └── dispatched
                └── in_progress
                       └── in_review
                              ├── completed
                              ├── blocked
                              └── failed
~~~

- pending: not yet ready because planning or inputs are incomplete.
- blocked: an explicit dependency, decision, environment, or failure prevents progress.
- ready_for_dispatch: inputs, owner, scope, and acceptance criteria are ready.
- dispatched: a real subagent invocation or handoff has occurred.
- in_progress: work has actually started.
- in_review: implementation is awaiting independent verification.
- completed: acceptance criteria are satisfied and evidence is recorded.
- failed: the task cannot proceed as specified and requires replanning.

Do not set dispatched or in_progress merely because a task file was created.

## 6. Agent responsibilities

| Agent | Primary responsibility | Typical deliverable |
|---|---|---|
| Architecture | Architecture and cross-module contracts | C4, ERD, ADR, task graph |
| UI/UX | User journey and interaction design | UX specification and states |
| Frontend | Browser/client implementation | Components, integration, frontend tests |
| Backend | Domain/API/data implementation | Routes, services, migrations, backend tests |
| Infrastructure | Runtime and delivery | IaC, CI/CD, environment and operations docs |
| QA | Independent verification | Test matrix, results, defect evidence |
| Orchestrator | Coordination and state | Task contracts, handoffs, current execution snapshot |

All bundled agents have the same full built-in tool availability and inherit the parent session's MCP/customizations. Tool access does not change role ownership: the Orchestrator remains the single coordinator and writer of shared execution state, while specialists own their assigned task scope. Use only the specialists relevant to the request. A small backend bug does not need all seven agents.

## 7. Dispatch and parallel execution

The Orchestrator must confirm that a specialist is present and that native subagent delegation is available before dispatch.

For each dispatch:
1. Start the delegated subagent with a fresh context window containing only the bounded task contract and required project context, never an unfiltered parent conversation fork.
2. Send only the task objective, scope, owned paths, dependencies, relevant contracts, acceptance criteria, verification instructions, and minimum source excerpts needed.
3. State prohibited scope.
4. State expected outputs and verification evidence.
5. Use isolated branch/worktree execution for concurrent code changes when supported.
6. Collect the specialist handoff.
7. Review the handoff against acceptance criteria.
8. Reconcile task status and next dependencies.

The SaaS MVP preset sets max_parallel_agents to 3. This is a team policy; the host runtime must also support the required concurrent subagent sessions.

If native dispatch is unavailable, the Orchestrator may execute bounded implementation directly when its own required capabilities are verified and the work is within the approved project scope, absorbing the necessary specialist execution responsibilities for that task. If it cannot execute directly, mark the dependent work blocked and report the exact capability failure and remediation. Do not create task contracts, dependency graphs, full-code specifications, or handoff packages as an automatic fallback. Produce those planning artifacts only when the user explicitly requests them. Never fabricate an agent run or its result.

## 8. Handoff contract

A specialist handoff should include:

- Task ID and actual status.
- Summary of work performed.
- Changed files and rationale.
- Decisions and assumptions.
- Commands/tests actually run and results.
- Acceptance criteria satisfied or not satisfied.
- Evidence references.
- Risks, blockers, and next action.

A specialist must not overwrite the shared state.json. It returns a handoff; Orchestrator reconciles the shared state.

## 9. Integration and review

Before marking a feature complete:
- Verify API, data, UX, and deployment contracts still agree.
- Run relevant unit, integration, contract, and end-to-end checks.
- Review security and access boundaries.
- Check migrations and backward compatibility.
- Confirm no task remains blocked or unreviewed.
- Record residual risk and untested areas.

QA independently verifies the implementation. Architecture reviews cross-module deviations. The user approves production deployment.

## 10. Session checkpoint

At meaningful task boundaries and before returning control:
1. Update the task contract with status and evidence.
2. Reconcile execution/state.json.
3. Record blockers, decisions, and next actions.
4. Create a new dated file in execution/sessions/.
5. Read the state and journal back to verify persistence.

Session journals are append-only. Do not rewrite old history to make it appear that a task was completed earlier.

## 11. Machine-checked completion and release (v0.3)

Project-local tasks, handoffs, plan and state must conform to the canonical JSON Schemas under `contracts/schemas/`. The Team Orchestrator runs:

```bash
python scripts/quality_gate.py validate --project /path/to/product
python scripts/quality_gate.py task --project /path/to/product --task-id BE-001
python scripts/quality_gate.py release --project /path/to/product
```

The `task` gate requires an independent QA verification record, full source Git SHA, exact acceptance-criteria mapping, and non-empty evidence logs. A failed gate keeps the task `in_review`/`blocked` and requires remediation. The `release` gate also enforces recorded human approvals; it cannot replace actual approval or protected CI. See [Quality Gates](QUALITY-GATES.md).
