---
name: system-architecture
description: >-
  Design a maintainable application architecture from approved requirements,
  constraints, and existing codebase evidence. Use before decomposing major
  implementation work or when a material technical decision is needed.
---

# System Architecture

## Procedure
1. Inspect the existing repository and runtime before proposing a replacement architecture.
2. Translate approved user journeys into system capabilities and quality attributes.
3. Identify system boundaries, modules, data ownership, external integrations, and trust boundaries.
4. Choose the simplest architecture that meets scale, availability, security, and delivery constraints.
5. Define major components, responsibilities, data flows, and failure paths.
6. Define authentication, authorization, secrets, audit, observability, backup, and recovery concerns.
7. Identify decisions with meaningful long-term impact and record them as ADRs.
8. Request independent review from relevant specialists.
9. Record unresolved decisions and approval gates.

## Output
- Context and container view
- Component/module map
- Data flow and trust boundaries
- Technology choices with rationale
- Key quality attributes
- Risks and trade-offs
- ADR list
- Open decisions

## Guardrails
- Do not select technologies solely because they are familiar.
- Do not over-engineer for hypothetical scale.
- Do not finalize architecture while material constraints remain unknown.
