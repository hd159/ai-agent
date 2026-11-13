---
name: review-handoff
description: >-
  Validate a specialist handoff for scope compliance, acceptance criteria,
  evidence, risks, and readiness for downstream work.
---

# Review Handoff

1. Confirm task identity and assigned owner.
2. Inspect reported artifacts or changed files where available.
3. Map every acceptance criterion to evidence.
4. Review scope boundaries and contract compliance.
5. Separate factual defects from suggestions.
6. Identify unresolved blockers and downstream impact.
7. Return accept, request-changes, or blocked with reasons.
8. Update execution state only with evidence-backed status.

A handoff summary alone is not proof that implementation or tests occurred.

## Executable handoff gate

1. Require an independent QA verification record for every task proposed as completed.
2. Check the actual source revision, report schema, evidence paths and criterion-to-check mapping using `scripts/quality_gate.py task`.
3. Reject missing/failed/not-run required criteria, stale source, unresolved dependencies, and a reviewer identical to the implementer.
4. Reconcile `state.json` only after the task gate passes. Run the `validate` gate after checkpointing.
5. Treat a successful static validator as artifact consistency evidence, not proof of genuine command execution; require trusted CI checks for release.
