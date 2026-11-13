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

## 3-Gate ADR Filter (anti-ADR bloat)

Before creating any standalone ADR under `.agent-ecosystem/artifacts/` or `.agent-ecosystem/execution/decisions/`, verify that the candidate passes all three gates:

1. **Reversibility:** Is the decision costly or difficult to reverse later?
2. **Surprise:** Is the choice non-obvious (would a future engineer wonder why this path was taken)?
3. **Trade-off:** Were there genuine competing alternatives with material trade-offs?

**Rule:** If any of the three gates is missing, skip creating a standalone ADR file and record a concise note in `PROJECT_CONTEXT.md` instead.

Routine, obvious, low-cost, reversible choices belong in the concise project context, not a new ADR. Preserve the decision, rationale, and material consequence without inflating the ADR set.

## Ubiquitous Language

As domain concepts are resolved, capture canonical terms and definitions immediately in `.agent-ecosystem/PROJECT_CONTEXT.md` or the existing `.agent-ecosystem/GLOSSARY.md`. Record distinctions and rejected synonyms where they prevent ambiguity. Reuse the agreed terms in UI labels, API payloads, events, and database schemas; notify UI/UX, Frontend, Backend, and QA agents of terminology changes.

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
