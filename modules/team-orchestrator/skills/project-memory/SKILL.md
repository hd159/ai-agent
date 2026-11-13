---
name: project-memory
description: >-
  Load, reconcile, and update durable project context, architecture baselines,
  plans, execution state, and historical checkpoints when starting or resuming
  work across sessions.
---

# Project Memory

Use this skill whenever work starts on an existing project, resumes after a gap, changes an established architecture, or the user asks for current project status.

## 1. Locate the project memory

The default location is .agent-ecosystem/ in the target application's repository. Do not confuse it with the installed AI Agent Ecosystem plugin repository.

Read in this order:
1. PROJECT_CONTEXT.md and team.json.
2. execution/state.json and execution/plan.json.
3. Current architecture document and only the ADRs relevant to the requested work.
4. Active task contracts under execution/tasks/.
5. Unresolved handoffs under execution/handoffs/.
6. The newest session checkpoint under execution/sessions/.

Do not read every historical journal by default. Follow references into older sessions only when a decision, blocker, or task history requires it.

## 2. Reconcile before trusting

- Inspect the current source files and source-control status relevant to the task.
- Compare the current repository commit with the source snapshot recorded in state.json or the latest checkpoint.
- Treat source code and reproducible verification as evidence of implementation.
- Treat approved architecture documents and ADRs as the design record.
- Treat task contracts as the detailed work record and state.json as the current dashboard.
- Treat session journals as append-only history, not as the current state.
- If files disagree, report the conflict and reconcile it explicitly. Never silently choose the most convenient version.
- If memory is missing or incomplete, reconstruct only what is supported by source files, task contracts, handoffs, and journals. Mark reconstructed facts as recovered and uncertain facts as unknown.

## 3. Resume response

Before doing more work, summarize:
- Current phase and goal.
- Completed tasks with evidence.
- In-progress and pending tasks.
- Blockers and pending decisions.
- Last checkpoint and whether it is stale.
- The next recommended action.

Do not infer that work continued while no session was active. Do not mark a task complete based only on a prior assistant statement.

## 4. Update architecture memory

When the user requests an architecture update:
1. Inspect the actual changed code, configuration, schemas, and deployment files.
2. Compare findings with the current architecture baseline.
3. Update the architecture document with a current-as-of date and source commit when available.
4. Preserve historical decisions. Add a superseding ADR or decision-log entry for material changes; do not rewrite an old ADR as though the new decision had always existed.
5. Record unresolved questions, risks, and assumptions separately.
6. Update state.json and create a session checkpoint describing the review and evidence.

## 5. 3-Gate ADR Filter and domain language

- Capture canonical domain terms inline in `PROJECT_CONTEXT.md` (or the existing `GLOSSARY.md`) as soon as the user and team agree on them. Do not defer resolved terms to a later documentation pass.
- Record canonical spelling, concise definition, meaningful synonyms, and distinctions between easily confused concepts. Keep UI labels, API payloads, event names, and database schemas aligned with this vocabulary.
- Before creating a standalone ADR in `artifacts/` or `execution/decisions/`, require all three gates:
  1. **Reversibility:** Is the decision costly or difficult to reverse later?
  2. **Surprise:** Is the choice non-obvious (would a future engineer wonder why this path was taken)?
  3. **Trade-off:** Were there genuine competing alternatives with material trade-offs?
- **Rule:** If any of the three gates is missing, skip creating a standalone ADR file and record a concise note in `PROJECT_CONTEXT.md` instead.
- Apply this filter to new decisions and architecture changes. Do not create ADRs for routine or obvious choices merely to create a paper trail.

## 6. Privacy and persistence

- Never write secrets, access tokens, passwords, private keys, or sensitive personal data into project memory.
- Keep state.json concise; put detail in task files, ADRs, and session journals.
- Use ISO 8601 timestamps with explicit timezone offsets.
- Do not claim persistence until the relevant files were actually written and read back successfully.
- Do not commit or push project memory unless the user or project policy authorizes it.
