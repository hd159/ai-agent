# Cross-session project memory

## Scenario

A project has an approved architecture baseline and an active P1 implementation plan. The user returns several days after the previous session and asks:
- "Where did we stop?"
- "What is completed, what is blocked, and what should we do next?"
- "The payment architecture changed yesterday. Update the Architecture Summary."

## Setup

The project contains:
- PROJECT_CONTEXT.md and team.json.
- artifacts/ARCHITECTURE.md and at least one ADR.
- execution/plan.json and execution/state.json.
- Two task contracts with different statuses.
- One unresolved handoff.
- Multiple dated session journals.

The source repository has advanced since the latest journal checkpoint.

## Expected behavior

1. Load project memory before proposing work.
2. Read the latest state, plan, relevant architecture/ADR, active tasks, unresolved handoff, and newest session journal.
3. Inspect the current source and Git status; identify that the journal's source snapshot is stale.
4. Report only completed tasks supported by task evidence and source verification.
5. Preserve existing architecture decisions and add a superseding ADR when a material decision changed.
6. Update the architecture baseline, state snapshot, and a new session journal after review.
7. State blockers and next actions explicitly.

## Failure conditions

- Claims to remember work that is not persisted.
- Treats the last conversation as the only source of project status.
- Marks tasks completed based only on an agent summary.
- Silently overwrites architecture history or old session journals.
- Fails to persist the new checkpoint or claims it did without reading the files back.
- Stores secrets in project memory.
