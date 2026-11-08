# Greenfield MVP Workflow

## Stage 1 — Discovery
Owner: Team Orchestrator with Architecture and UI/UX.
- Understand problem, users, workflows, constraints.
- Create Product Brief.
- Capture assumptions and open questions.

Gate: user approves direction before MVP scope is treated as committed.

## Stage 2 — MVP scope
Owner: Architecture Agent.
- Prioritize capabilities.
- Define non-goals and release criteria.
- Create MVP Scope.

Gate: `mvp_scope`.

## Stage 3 — Architecture
Owner: Architecture Agent.
- Define system context, modules, data ownership, integration, security, and operations.
- Request specialist reviews.
- Record ADRs and trade-offs.

Gate: `architecture`.

## Stage 4 — Contracts
Owners: Architecture, Backend, Frontend, UI/UX, Infrastructure.
- Freeze API contract, data model, design specification, and environment contract.
- Assign explicit owners and version.

## Stage 5 — Task planning
Owner: Team Orchestrator.
- Create bounded task contracts.
- Resolve dependencies and owned paths.
- Generate parallel execution waves.

## Stage 6 — Implementation
Owners: Frontend, Backend, Infrastructure.
- Dispatch only ready tasks.
- Use TDD where feasible.
- Record evidence and handoffs.

## Stage 7 — Integration and QA
Owners: QA and Architecture.
- Verify cross-module behavior.
- Review spec compliance and engineering quality separately.
- Resolve defects and update execution state.

## Stage 8 — Release readiness
Owners: QA and Infrastructure.
- Run deployment readiness.
- Document rollback, monitoring, and residual risk.

Gate: production deployment requires explicit user authorization.
