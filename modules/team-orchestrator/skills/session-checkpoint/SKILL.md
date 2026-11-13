---
name: session-checkpoint
disable-model-invocation: true
description: >-
  Persist work completed, task progress, blockers, decisions, verification
  evidence, and next actions to project execution state and an append-only
  session journal before pausing or handing work back.
---

# Session Checkpoint

Use this skill after a meaningful task outcome, when work becomes blocked, before switching major workstreams, and before returning control to the user.

## 1. Gather facts

Inspect the current task contract, relevant changed files, source-control diff/status, verification output, and specialist handoffs. Separate verified facts from agent-reported claims and assumptions.

## 2. Update task records

For every affected task:
- Set the accurate status: pending, blocked, ready_for_dispatch, dispatched, in_progress, in_review, completed, or failed.
- Record the owner, changed artifacts, verification results, evidence references, blockers, and next action.
- Mark completed only when acceptance criteria and required verification evidence are satisfied.
- Do not erase earlier evidence; append or reference the new result.

## 3. Reconcile execution state

Update execution/state.json as the concise current snapshot:
- Overall status and current phase.
- Current focus.
- Last checkpoint timestamp and session ID.
- Source commit or working-tree snapshot when available.
- Task status summary.
- Current blockers and pending decisions.
- Next concrete actions.

The Team Orchestrator is the single writer of state.json. Specialists return handoffs; they do not concurrently overwrite the shared snapshot.

## 4. Write the session journal

Create a new file under execution/sessions/ named YYYY-MM-DD-<short-slug>.md. Never overwrite an earlier journal. Use the project timezone when known; otherwise record the actual timezone offset used.

Include:
- Session ID, start/end timestamps, goal, and outcome.
- Work completed and task IDs.
- Work still in progress.
- Decisions made and ADR references.
- Blockers and unresolved questions.
- Changed files and artifacts.
- Tests/checks run and their actual results.
- Next actions in priority order.
- Source commit and whether the working tree was clean, when available.

## 5. Verify persistence

Read back state.json and the newly written journal. Confirm the task statuses, blockers, and next actions agree. If a write or read-back fails, tell the user exactly what was not persisted.

Do not rely on a runtime shutdown hook. A checkpoint is an explicit work action, not an assumed side effect of ending a chat.

## Gate reconciliation

Before writing a checkpoint that claims `completed`, confirm the task's independent QA report and successful quality gate execution. Record gate command, exit status, verified source commit, and evidence paths in the session journal. A failed or unavailable gate must be recorded as a blocker; do not silently preserve a false `completed` status. After checkpointing, run `quality_gate.py validate` to detect task/state drift.
