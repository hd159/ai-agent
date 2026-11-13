---
name: mvp-scoping
description: >-
  Define a focused minimum viable product, prioritize features, and document
  non-goals and release criteria. Use after discovery and before architecture
  or implementation planning.
---

# MVP Scoping

<HARD-GATE>
Do NOT write application code, scaffold implementation files, or dispatch implementation tasks until the discovery/MVP scope design has been presented and explicitly approved by the user. This applies regardless of perceived task simplicity (Anti-Pattern: This Is Too Simple To Need A Design).
</HARD-GATE>

## Step 0 — Sub-Project Decomposition Check

- Re-evaluate the Product Brief for independently valuable subsystems, distinct domain models, data ownership, integrations, user groups, or release lifecycles (for example auth + billing + analytics + chat).
   - If the request is too broad for one cohesive MVP, pause detailed requirements and feature prioritization. Present 2–3 concrete ways to split the work into independent sub-projects/phases, show trade-offs, and recommend a sequence.
   - Ask at most ONE question to confirm the decomposition. Scope only the first agreed sub-project; keep later phases as explicit out-of-scope items/dependencies.

## Procedure

1. Start from the confirmed Product Brief and user journeys.
2. List candidate capabilities by user outcome, not by technical layer.
3. Classify each capability as Must, Should, Could, or Not in MVP.
4. For every Must item, state the user value and acceptance outcome.
5. Identify dependencies and operational requirements that are genuinely required for launch.
6. Explicitly list non-goals and deferred capabilities.
7. Define an MVP boundary that can be delivered and tested end-to-end.
8. Define release criteria and success measures.
9. Present 2–3 concrete scope approaches when a real choice exists, with explicit value, cost, risk, and trade-offs; lead with a recommendation.
10. Present the complete discovery/MVP scope design and wait for the user's explicit approval before creating implementation plans or dispatching implementation work.

## Socratic Interview Discipline

- Ask **at most ONE question per message**. Never dump a questionnaire or multiple independent questions in one turn.
- Prefer concise A/B/C options when the decision is concrete and the choices are genuinely distinct. Ask an open question when the user's intent is not yet clear enough to define options.
- Ask the highest-impact question first; explain what the answer changes. Incorporate the answer before asking the next question.
- Every proposed design or scope direction must include **2–3 concrete approaches**, material trade-offs, and a clear recommendation first. Explain why an option is unsuitable when constraints rule it out.
- Do not treat silence, a tentative preference, or approval of one detail as approval of the complete discovery/MVP scope.


## Output
- MVP objective
- In-scope capabilities
- Out-of-scope capabilities
- Core user journeys
- Dependencies
- Release criteria
- Risks and assumptions

## Guardrails
- Do not equate MVP with a low-quality prototype.
- Do not include speculative features "for future flexibility".
- Do not silently expand scope to make the architecture more interesting.
