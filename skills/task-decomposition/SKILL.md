---
name: task-decomposition
description: >-
  Convert an approved feature or architecture into small, owned, verifiable
  implementation tasks with explicit dependencies and file boundaries.
---

# Task Decomposition

## Procedure
1. Read the approved requirement, architecture, and technical contracts.
2. Decompose by independently verifiable outcomes, not merely by department.
3. Give every task one accountable owner.
4. Include exact inputs and relevant artifacts.
5. Define scope and out-of-scope work.
6. Declare dependencies and owned paths/resources.
7. Write testable acceptance criteria and verification steps.
8. Identify tasks that can safely run in parallel.
9. Check for overlapping file ownership and unstable shared interfaces.
10. Produce a task graph and execution order.

## Task sizing
A task should be small enough for one specialist to complete and review without coordinating several unrelated workstreams. Split tasks that mix multiple layers or produce ambiguous completion.

## Output
A list of task contracts conforming to `contracts/schemas/task.schema.json`, plus a dependency graph.

## Guardrails
- Never assign the same mutable file to parallel owners.
- Do not dispatch implementation against an unapproved contract.
- Do not hide dependencies in prose.
