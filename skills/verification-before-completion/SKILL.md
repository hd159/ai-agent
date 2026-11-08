---
name: verification-before-completion
description: >-
  Verify implementation, tests, and deliverables before reporting a task as
  complete. Use immediately before any completion claim or handoff.
---

# Verification Before Completion

## Procedure
1. Map each acceptance criterion to a concrete verification step.
2. Run the relevant commands or inspect the actual artifact.
3. Capture command, exit status, and concise result.
4. Distinguish executed checks from checks that were not run.
5. Record limitations, environment constraints, and remaining blockers.
6. Confirm no required deliverable is missing.
7. Mark complete only when evidence supports every required criterion.

## Output
A verification report containing criterion, check, result, evidence, and residual risk.

## Hard rule
Never infer success from code being written, an agent saying it finished, or a command being planned.

## Project quality gate

For project-local work, run \`python <ai-agent-root>/scripts/quality_gate.py task --project <project-root> --task-id <TASK-ID>\` before completing a task, then \`quality_gate.py validate\` after reconciling state. The independent reviewer must not be the task owner, and passing checks must include actual output files under the project's verification/evidence directory. Evidence linked to an older source revision is stale. A failed, blocked, unavailable, or skipped required check prevents completion.

Before production release, run \`quality_gate.py release --project <project-root>\`, require all mandatory approvals, and independently confirm a trusted CI run. The tool verifies recorded evidence and Git freshness; it cannot prove that a user/agent did not fabricate a log file.
