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

## 2.1 Discovery and approval gate

Before detailed requirements questions, perform a sub-project decomposition check. If the request spans multiple independent subsystems or cannot fit one cohesive specification, pause and help split it into independent sub-projects/phases. Present 2–3 concrete decomposition approaches with trade-offs and a recommendation, ask at most one question to confirm the first sub-project, and scope only that first phase.

For discovery and MVP scoping:

- Ask at most one question per message; prefer concise A/B/C choices when they do not constrain intent prematurely.
- When proposing a design or scope direction, present 2–3 concrete approaches, explicit trade-offs, and a clear recommendation.
- Do not write application code, scaffold implementation files, or dispatch implementation tasks until the discovery/MVP scope design has been presented and explicitly approved by the user, regardless of perceived simplicity.
- Capture agreed domain terms immediately in `.agent-ecosystem/PROJECT_CONTEXT.md` or the existing `.agent-ecosystem/GLOSSARY.md`.

## 2.2 Delegation context hygiene

Start delegated subagents with a fresh context window containing only the bounded task contract and required project context, never an unfiltered parent conversation fork. Include only the objective, scope, owned paths, dependencies, relevant contracts, acceptance criteria, verification instructions, and minimum source context.

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

If subagent invocation is unavailable, the Orchestrator may perform bounded implementation directly when its own required capabilities are verified and the work is within the approved project scope, absorbing the necessary specialist execution responsibilities for that task. Otherwise mark the dependent work blocked and report the exact missing/denied capability and remediation. Do not generate dispatch-ready task files, dependency graphs, full-code specifications, or handoff packages as an automatic fallback. Create such artifacts only when the user explicitly requests planning or handoff deliverables. Never simulate delegation or invent results.

## 8. Persistent memory lifecycle

For an existing project, the orchestrator must:
1. Load PROJECT_CONTEXT.md, team.json, execution/state.json, and execution/plan.json.
2. Inspect relevant architecture/ADRs, active task contracts, unresolved handoffs, and the latest session journal.
3. Reconcile persisted status against current source and Git state.
4. Report completed, in-progress, pending, and blocked work before continuing.

For meaningful work, it must checkpoint after task outcomes and before returning control. A checkpoint updates task records, state.json, and a new append-only session journal. Decisions and architecture changes are recorded when made, not reconstructed only at the end.

The session journal is history; state.json is the current dashboard; task contracts are the detailed execution records. The orchestrator is the single writer of shared state. Do not rely on a guaranteed host shutdown hook.

See [Persistent Project Memory](PERSISTENT-PROJECT-MEMORY.md) for file layout, source-of-truth rules, recovery, concurrency, and security policy.
