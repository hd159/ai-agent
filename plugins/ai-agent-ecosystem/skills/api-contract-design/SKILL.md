---
name: api-contract-design
description: >-
  Design stable, versionable API contracts between frontend, backend, and
  external consumers. Use before parallel frontend/backend implementation.
---

# API Contract Design

## Procedure
1. Identify consumers, use cases, and resource ownership.
2. Define endpoints or operations, request/response schemas, and error model.
3. Specify authentication, authorization, pagination, filtering, idempotency, and rate limits where relevant.
4. Define validation and consistent error semantics.
5. Include examples for success and failure cases.
6. Record compatibility and versioning rules.
7. Validate the contract against user journeys and data model.
8. Obtain frontend and backend review before implementation.

## Output
An OpenAPI document or equivalent interface contract, examples, error catalogue, and unresolved questions.

## Guardrails
- Avoid leaking database implementation details into public contracts.
- Do not make fields optional or nullable without an explicit semantic reason.
- Do not change a shared contract unilaterally after implementation begins.
