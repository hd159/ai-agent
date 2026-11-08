# Team Orchestration Specification

## 1. Responsibilities

The orchestrator owns coordination, not every technical decision.

It must:
- Read the team manifest and project context.
- Load and reconcile persistent project memory before resuming existing work.
- Identify missing information and ask concise clarification questions.
- Propose MVP scope and obtain approval.
- Request specialist reviews for material architecture decisions.
- Create a dependency-aware task graph.
- Assign one accountable owner per task.
- Dispatch only tasks whose dependencies are satisfied.
- Validate handoffs and completion evidence.
- Persist task outcomes, blockers, decisions, and session checkpoints.
- Replan when assumptions, dependencies, or requirements change.

## 2. Planning sequence

1. Discovery
2. Product brief
3. MVP scope
4. Architecture baseline
5. Specialist review
6. Technical contracts
7. Task decomposition
8. Dependency resolution
9. Implementation dispatch
10. Integration and quality review

## 3. Task decomposition rules

A good task:
- Produces one bounded, reviewable deliverable.
- Has one accountable owner.
- Names exact inputs and relevant source artifacts.
- Defines scope and explicit out-of-scope items.
- Declares dependencies.
- Declares owned paths or resources.
- Includes testable acceptance criteria.
- Defines verification evidence.

Avoid:
- "Build the whole backend" as one task.
- Tasks with multiple agents editing the same files.
- Tasks that depend on undocumented assumptions.
- Parallel execution before contracts are stable.

## 4. Parallel execution

Tasks can run in parallel when:
- Dependencies are complete.
- They own disjoint files/resources.
- Shared contracts are stable.
- No unresolved decision changes their implementation.

Default maximum parallel specialists in the SaaS MVP preset: 3. Increase only when the project and runtime can support it.

The Team Orchestrator is the single writer of the shared execution snapshot. Specialists update their owned task artifacts and return handoffs; the orchestrator reconciles those handoffs into state.json to prevent lost updates.

## 5. Handoff protocol

Every handoff includes:
- Task ID and status.
- Summary of work.
- Files or artifacts changed.
- Decisions made.
- Tests and verification results.
- Known limitations.
- Risks and blockers.
- Suggested next action.

## 6. Review gates

Two distinct reviews:
1. Specification compliance: does the deliverable satisfy the task and acceptance criteria?
2. Engineering quality: is it secure, maintainable, understandable, and consistent with project conventions?

## 7. Runtime behavior

If subagent invocation is unavailable, generate dispatch-ready task files and stop at ready_for_dispatch. Never simulate delegation or invent results.

## 8. Persistent memory lifecycle

For an existing project, the orchestrator must:
1. Load PROJECT_CONTEXT.md, team.json, execution/state.json, and execution/plan.json.
2. Inspect relevant architecture/ADRs, active task contracts, unresolved handoffs, and the latest session journal.
3. Reconcile persisted status against current source and Git state.
4. Report completed, in-progress, pending, and blocked work before continuing.

For meaningful work, it must checkpoint after task outcomes and before returning control. A checkpoint updates task records, state.json, and a new append-only session journal. Decisions and architecture changes are recorded when made, not reconstructed only at the end.

The session journal is history; state.json is the current dashboard; task contracts are the detailed execution records. The orchestrator is the single writer of shared state. Do not rely on a guaranteed host shutdown hook.

See [Persistent Project Memory](PERSISTENT-PROJECT-MEMORY.md) for file layout, source-of-truth rules, recovery, concurrency, and security policy.
