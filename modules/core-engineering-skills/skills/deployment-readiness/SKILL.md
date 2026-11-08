---
name: deployment-readiness
description: >-
  Assess whether an application release is operationally ready, including
  configuration, security, observability, rollback, and deployment evidence.
---

# Deployment Readiness

## Checklist
- Environment configuration and secret references are defined.
- Build and test pipeline is reproducible.
- Database migrations are reviewed and reversible or have a recovery plan.
- Health checks and readiness probes are defined.
- Logs, metrics, traces, and alerts cover critical paths.
- Backup and restore expectations are documented.
- Rollback or roll-forward strategy is documented.
- Security and dependency checks are complete.
- Release notes and operational ownership are clear.
- Production deployment has explicit user authorization.

## Output
A readiness checklist with pass/fail/unknown status, evidence, blockers, and required approvals.

## Guardrails
A readiness review is not permission to deploy. Never deploy to production without explicit approval.
