# Persistent Project Memory

**Status:** Proposed implementation baseline for v0.2.x  
**Storage:** Project-local files, versioned with the target application's Git repository  
**Owner:** Team Orchestrator

## 1. Problem

Conversation history is not a reliable project state store. It is scoped to a chat, can be truncated or unavailable in a new session, and mixes planning, implementation, and unrelated discussion.

The ecosystem therefore needs durable project memory that lets an agent resume work days later without pretending it remembers unpersisted activity.

## 2. Design

Use three complementary persistence layers:

| Layer | Purpose | Canonical artifacts |
|---|---|---|
| Project memory | Stable knowledge and approved design | PROJECT_CONTEXT.md, architecture documents, ADRs |
| Execution state | Current work snapshot | execution/state.json, execution/plan.json, task contracts |
| Session journal | Historical activity and resume notes | execution/sessions/*.md, handoffs |

No separate database is required for a single project in one Git repository. Git supplies history, diffs, and recovery when the project memory files are committed.

## 3. Project layout

~~~text
.agent-ecosystem/
├── PROJECT_CONTEXT.md
├── team.json
├── artifacts/
│   ├── ARCHITECTURE.md
│   └── adr/
├── execution/
│   ├── README.md
│   ├── plan.json
│   ├── state.json
│   ├── tasks/
│   ├── handoffs/
│   ├── sessions/
│   └── decisions/
~~~

## 4. Source-of-truth rules

When records disagree, do not silently overwrite one with another.

1. Current source code and reproducible checks establish what is implemented now.
2. Approved architecture documents and ADRs establish intended design and approved decisions.
3. Task contracts establish scope, owner, acceptance criteria, and detailed task evidence.
4. state.json is the concise current execution dashboard and must be reconciled against task contracts.
5. plan.json describes intended phases and approval gates; it does not prove work was completed.
6. Session journals are append-only historical records. They explain what happened, but do not override newer source evidence or current state.

A checkpoint is stale when the source has advanced or changed materially since its recorded source commit. Re-inspect relevant files before relying on it.

## 5. Startup and resume protocol

Before acting on an existing project:

1. Read PROJECT_CONTEXT.md and team.json.
2. Read execution/state.json and execution/plan.json.
3. Read the current architecture baseline and only relevant ADRs.
4. Read active task contracts and unresolved handoffs.
5. Read the latest session journal; load older journals only when needed.
6. Inspect Git status, current commit, and the files relevant to the request.
7. Reconcile the state snapshot and report completed work, active work, blockers, pending decisions, and next actions.

If memory is absent, recover only facts supported by repository content, handoffs, and journals. Label recovered facts and unknowns; never invent progress.

## 6. Checkpoint protocol

Create a checkpoint after:
- A task completes, fails, or becomes blocked.
- A material architecture or product decision is made.
- Work switches to another major workstream.
- The user asks to pause, summarize, or hand off.
- The agent is about to return control after meaningful work.

Each checkpoint updates:
- The affected task contract(s).
- execution/state.json.
- A new dated session journal.
- Handoff records when work crosses agent boundaries.

The journal includes goal, timestamps, outcome, completed work, in-progress work, decisions, blockers, changed files, verification evidence, and next actions.

Do not rely on an assumed runtime shutdown hook. Checkpointing is an explicit action. Read back written files before claiming that persistence succeeded.

## 7. Concurrency

The Team Orchestrator is the single writer of state.json and plan.json. Specialist agents own bounded task files and return handoffs. The orchestrator reviews handoffs and reconciles the shared snapshot, avoiding concurrent lost updates.

Session journals are append-only. Use unique date-and-slug names; if a name already exists, choose a new suffix rather than overwrite history.

## 8. Architecture evolution

When the user asks to update architecture:
1. Inspect current implementation and configuration.
2. Compare the findings with the recorded architecture baseline.
3. Update the architecture document with review date and source commit.
4. Preserve the original decision history.
5. Add a new ADR or superseding decision when a material choice changes.
6. Record unresolved risks and assumptions.
7. Update execution state and write a session checkpoint.

Never regenerate an architecture summary from scratch if doing so would discard still-valid decisions.

## 9. Security and Git policy

- Never store passwords, API keys, access tokens, private keys, or sensitive personal data.
- Prefer references to secret-manager names over secret values.
- Project-local files are persistent on disk; Git history is available only after they are committed.
- Do not commit or push memory files unless the user or repository policy authorizes it.
- For shared or multi-user workspaces, use normal Git branch/merge practices to resolve concurrent changes.

## 10. Scope and future evolution

This is a project-local, Git-backed design. A centralized memory service may be added later if projects need cross-repository search, multiple independent workspaces, shared user identity, or centralized access control. Do not introduce PostgreSQL, Redis, or vector search merely to persist a small project status snapshot.
