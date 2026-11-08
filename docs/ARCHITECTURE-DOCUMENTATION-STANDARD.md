# Architecture Documentation Standard

This standard defines how every project stores architecture baselines, audit reports, findings, target designs, and architecture decisions.

## 1. Storage location

Keep product-specific architecture documents in the product repository:

~~~text
.agent-ecosystem/
└── artifacts/
    └── architecture/
        ├── ARCHITECTURE-CURRENT.md
        ├── ARCHITECTURE-TARGET.md
        ├── ARCHITECTURE-AUDIT-v1.md
        ├── ARCHITECTURE-AUDIT-v2.md
        ├── FINDINGS-REGISTER.md
        ├── diagrams/
        └── adr/
            ├── ADR-0001-<slug>.md
            └── ADR-0002-<slug>.md
~~~

The ai-agent repository contains generic standards and blank templates only. Never store a product's business logic, secrets, architecture audit, or task backlog in the shared plugin repository.

## 2. Document roles

| Document | Purpose | Update policy |
|---|---|---|
| ARCHITECTURE-CURRENT.md | Verified architecture as implemented now | Update when source changes materially |
| ARCHITECTURE-TARGET.md | Approved intended architecture | Update through review and approval |
| ARCHITECTURE-AUDIT-vN.md | Historical assessment at a specific source snapshot | Immutable after approval; create a new version |
| FINDINGS-REGISTER.md | Current lifecycle of every finding | Update when evidence or status changes |
| ADR-xxxx | Decision, alternatives, rationale, consequences | Append new/superseding ADR; preserve history |
| diagrams/ | C4, sequence, deployment, ERD and state diagrams | Keep editable source such as Mermaid |

## 3. Audit metadata

Every audit starts with metadata:

~~~yaml
---
document_type: architecture-audit
project: <project-id>
version: 1
repository: <owner/repository>
audited_commit: <full-git-commit-sha>
reviewed_at: YYYY-MM-DD
reviewer: architecture-agent
assessment_score: <number-or-null>
assessment_scale: 100
score_subject: <what-the-score-measures>
scoring_rubric: <rubric-name-and-version>
status: historical-baseline
---
~~~

Record the score exactly as stated by the source report. If the report does not define what the score measures or provide its rubric, write "not specified". Do not reinterpret an 86/100 score as production readiness, audit quality, or security maturity without evidence.

## 4. Required audit sections

1. Executive summary and scope.
2. Repository, branch, full audited commit, and review date.
3. System context and business-critical journeys.
4. Current architecture and module/container inventory.
5. Trust boundaries, data flows, identities, and external integrations.
6. Findings summary by severity and lifecycle status.
7. Detailed findings with evidence.
8. Architecture risks, constraints, assumptions, and unknowns.
9. Target architecture recommendations.
10. ADR references and unresolved decisions.
11. Prioritized remediation roadmap.
12. Test strategy and verification matrix.
13. Limitations, uninspected areas, and confidence statement.
14. Score breakdown with rubric, if supplied by the assessment method.

A finding must cite repository paths and relevant symbols or line ranges where possible. Separate direct source evidence from inference and recommendations.

## 5. Findings register

Each finding should record:

| Field | Description |
|---|---|
| ID | Stable ID, e.g. AUTH-001 |
| Title | Short description |
| Severity | Critical / High / Medium / Low / Informational |
| Confidence | High / Medium / Low |
| Status | Lifecycle status below |
| Evidence | File, symbol, line, test, or reproducible trace |
| Impact | User, security, data, reliability, or business impact |
| Recommendation | Smallest safe remediation |
| Owner | Accountable agent or team |
| Task | Task contract ID |
| Verification | Required positive and negative tests |
| Updated | Date and evidence revision |

Recommended statuses:

- Open: finding recorded but not yet fully validated.
- Confirmed: reproduced or supported by current source evidence.
- In Progress: remediation is underway.
- Fixed Pending Verification: code changed; independent verification is outstanding.
- Verified Fixed: acceptance criteria and tests demonstrate resolution.
- Accepted Risk: authorized decision to retain the risk, with rationale and review date.
- Stale: the original condition no longer exists because the system changed.
- False Positive: the original claim was incorrect.
- Needs Verification: evidence is insufficient to confirm or dismiss.

Do not mark a finding Verified Fixed based only on a code diff or implementation-agent statement.

## 6. Current vs target architecture

Current architecture describes what the repository demonstrably does today. Target architecture describes an approved design, not an assumption that it has already been implemented.

For every material difference, link:
- The related finding.
- The approved ADR or decision.
- The implementation task.
- The verification evidence.

Keep logical data relationships distinct from physical database constraints. Mark inferred relationships as logical until verified in migrations/schema.

## 7. ADR standard

Use one ADR per material decision:

1. Status: proposed, accepted, rejected, superseded.
2. Context and decision drivers.
3. Options considered.
4. Decision and rationale.
5. Security, reliability, cost, and operational consequences.
6. Migration/rollback implications.
7. Related findings, tasks, tests, and approvals.

Never edit an accepted ADR to make it appear that a later decision was always in force. Create a new ADR that supersedes it.

## 8. Versioning and score comparison

- Preserve the original audit as a historical snapshot.
- Create a new audit version for a new assessment.
- Record the exact Git commit for each assessment.
- Keep the same rubric and scope when comparing scores.
- If the rubric changes, label the score as non-comparable.
- Track remediation progress in FINDINGS-REGISTER.md; do not edit old audit findings to make the old score look better.
- A score is not a substitute for release gates, test results, threat modeling, or operational readiness.

## 9. Recommended diagrams

Use editable Mermaid source inside Markdown where possible:

- C4 System Context and Container diagrams.
- Component/module ownership.
- Sequence diagrams for authentication, payment, and other critical flows.
- ERD with logical/physical relationship distinctions.
- State machines for orders, subscriptions, entitlements, and background jobs.
- Deployment and trust-boundary diagrams.

## 10. Templates

Start from:
- templates/artifacts/ARCHITECTURE.md
- templates/artifacts/architecture/ARCHITECTURE-AUDIT-TEMPLATE.md
- templates/artifacts/architecture/FINDINGS-REGISTER-TEMPLATE.md
- templates/artifacts/ADR.md

Export PDF/DOCX only when a stakeholder needs a fixed or office-editable snapshot. Markdown remains the version-controlled source of truth.
