---
name: product-discovery
description: >-
  Discover the business problem, target users, workflows, constraints, and
  success measures for a new or existing product. Use before defining scope
  when requirements are incomplete or ambiguous.
---

# Product Discovery

<HARD-GATE>
Do NOT write application code, scaffold implementation files, or dispatch implementation tasks until the discovery/MVP scope design has been presented and explicitly approved by the user. This applies regardless of perceived task simplicity (Anti-Pattern: This Is Too Simple To Need A Design).
</HARD-GATE>

## Use when
A user presents an idea, problem statement, product request, or unclear feature request.

## Do not use when
The task is a fully specified, narrowly scoped implementation change with approved acceptance criteria.

## Step 0 — Sub-Project Decomposition Check

- Inspect the request for independently valuable subsystems, distinct domain models, separate data ownership, integrations, user groups, or release lifecycles (for example auth + billing + analytics + chat).
- If the request spans multiple independent subsystems and cannot be captured in one cohesive Product Brief, pause detailed discovery. Present 2–3 concrete decomposition approaches with explicit trade-offs and a clear recommendation.
- Ask at most one question in that message to confirm the first sub-project or phase. Do not scope every subsystem at once.
- After the decomposition is agreed, scope only the first sub-project; record later phases as boundaries/dependencies, not hidden MVP scope.

## Procedure

1. Identify the business problem, not just the requested feature.
2. Identify primary users, their goals, current workflow, and pain points.
3. Separate known facts, assumptions, constraints, and open questions.
4. Identify the smallest set of user journeys that delivers meaningful value.
5. Capture integrations, data sources, compliance, security, performance, and operational constraints.
6. Define measurable success signals where possible.
7. Ask only the highest-impact unanswered question; ask at most ONE question per message.
8. Summarize the findings as a concise Product Brief, present 2–3 concrete design/discovery directions when a choice exists, explain trade-offs, lead with a recommendation, and obtain explicit user confirmation before treating the design as approved.

## Socratic Interview Discipline

- Ask **at most ONE question per message**. Never send a questionnaire or a batch of 5–10 questions.
- Prefer concise A/B/C multiple-choice options when the decision can be framed clearly; use an open question when options would prematurely constrain the user's intent.
- Ask only about information that would materially change the product, scope, or decision. Build the next question on the user's previous answer and explain why it matters.
- When proposing a design or scoping direction, always present **2–3 concrete approaches**, their material trade-offs, and a clear recommendation first. Do not present a false choice: omit approaches ruled out by evidence or constraints and explain why.
- Keep a running distinction between confirmed facts, assumptions, and unresolved questions. Update the brief as answers arrive rather than asking everything upfront.

## Ubiquitous Language

- As soon as a domain term is agreed, record its canonical term and concise definition inline in `.agent-ecosystem/PROJECT_CONTEXT.md`; use or create `.agent-ecosystem/GLOSSARY.md` when the project already maintains a dedicated glossary.
- Record synonyms, rejected/ambiguous alternatives, and important distinctions where they prevent drift.
- Use the exact canonical terms consistently in UI labels, user-facing copy, API request/response fields, event names, and database schemas. Share the vocabulary with UI/UX, Frontend, Backend, and QA agents immediately; do not defer glossary capture until the end of discovery.

## Output
Produce a Product Brief with:
- Problem and opportunity
- Target users and jobs-to-be-done
- Current-state workflow
- Proposed outcomes
- Constraints and dependencies
- Assumptions and open questions
- Success measures

## Quality gate
A reader must be able to explain who the product serves, what problem it solves, and how success will be recognized.
