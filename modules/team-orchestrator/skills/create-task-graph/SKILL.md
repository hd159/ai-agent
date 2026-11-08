---
name: create-task-graph
description: >-
  Convert approved project plans into task contracts and a dependency graph
  that can be dispatched safely to specialist agents.
---

# Create Task Graph

1. Read approved scope, architecture, contracts, and team manifest.
2. Split work into bounded deliverables.
3. Assign one owner to each task.
4. Declare inputs, scope, exclusions, dependencies, owned paths, acceptance criteria, and verification.
5. Detect shared-file and shared-contract conflicts.
6. Mark tasks `blocked`, `ready_for_dispatch`, or `pending` accurately.
7. Create execution waves based on dependency readiness.
8. Save each task as a separate JSON file conforming to the task schema.

Do not mark a task `in_progress` until a real dispatch or execution has begun.
