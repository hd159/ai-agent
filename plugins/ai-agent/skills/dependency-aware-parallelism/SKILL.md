---
name: dependency-aware-parallelism
description: >-
  Determine which implementation tasks can run concurrently without contract,
  file ownership, or sequencing conflicts. Use when planning parallel agents.
---

# Dependency-aware Parallelism

## Procedure
1. Read all task dependencies and owned paths.
2. Mark tasks blocked until every prerequisite is complete.
3. Confirm shared contracts are stable before parallel implementation.
4. Detect write conflicts across paths, schemas, migrations, and generated files.
5. Group only independent ready tasks into a parallel wave.
6. Set a reasonable concurrency limit based on review capacity and runtime limits.
7. Keep integration tasks serial after their required outputs arrive.
8. Recompute readiness after each task completion or failure.

## Safe parallel examples
- UX exploration and infrastructure discovery after the same brief is approved.
- Frontend scaffolding and backend implementation after API contracts are frozen.
- Independent module tests with disjoint fixtures and ownership.

## Unsafe parallel examples
- Two agents editing the same shared schema.
- Frontend implementation while endpoint shapes are still changing without a mock contract.
- Production migration and application deployment without an approved release plan.

## Output
Parallel waves, blocked tasks, conflict warnings, and the reason each task is safe to start.
