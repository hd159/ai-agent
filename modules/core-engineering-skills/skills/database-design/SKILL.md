---
name: database-design
description: >-
  Model persistent data, ownership, relationships, constraints, and migration
  strategy for an application. Use when defining or changing the data layer.
---

# Database Design

## Procedure
1. Identify domain entities and their lifecycle.
2. Define ownership, relationships, cardinality, and invariants.
3. Choose identifiers, nullability, uniqueness, and referential behavior deliberately.
4. Identify indexes from query patterns rather than guessing.
5. Define audit, retention, deletion, and privacy requirements.
6. Plan migrations, backfills, rollback, and compatibility with deployed code.
7. Review concurrency and transaction boundaries.
8. Document assumptions and test representative queries.

## Output
ERD or schema, data dictionary, constraints, indexes, migration plan, and operational considerations.

## Guardrails
- Do not use free-form text for constrained values without a reason.
- Do not run destructive migrations against production without explicit approval.
- Do not store secrets in application tables unless a secure secret-management design requires it.
