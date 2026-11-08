# Project Execution Artifacts

The Team Orchestrator stores plans, current execution state, task contracts, handoffs, and session checkpoints under .agent-ecosystem/execution/.

## Persistence layers

- Project memory: PROJECT_CONTEXT.md, architecture documents, and ADRs describe durable project knowledge and approved decisions.
- Execution state: state.json is the concise current snapshot. plan.json describes phases and approval gates. Detailed task contracts live in tasks/.
- Session journal: sessions/ contains append-only records of work performed, decisions, blockers, verification, and next actions.

## Startup / resume

Before continuing existing work, read PROJECT_CONTEXT.md, team.json, state.json, plan.json, relevant architecture/ADRs, active task contracts, unresolved handoffs, and the latest session checkpoint. Reconcile the checkpoint against current source code and source-control status.

## Checkpoint

Update state.json after a task completes, fails, or becomes blocked, and before returning control. Create a new dated session journal; never overwrite an older journal. Read back the files after writing them.

The Team Orchestrator is the single writer of state.json. Specialists provide handoffs; they must not concurrently overwrite the shared state snapshot.

## Evidence and privacy

A completed task requires acceptance criteria and verification evidence. Agent self-report alone is insufficient. Never store credentials, tokens, private keys, passwords, or sensitive personal data here.

Git provides history and recovery when these files are committed. Do not commit or push project memory unless the user or project policy authorizes it.
