---
name: code-review
description: >-
  Review a change for specification compliance, correctness, security,
  maintainability, and regression risk. Use before merging or handing off code.
---

# Code Review

Perform two separate passes.

## Pass 1 — Specification compliance
- Does the change satisfy the task and acceptance criteria?
- Are required edge cases handled?
- Is anything missing, overbuilt, or outside scope?
- Are contracts and user-visible behavior consistent?

## Pass 2 — Engineering quality
- Are there correctness, security, privacy, performance, or reliability defects?
- Are errors handled and logged appropriately?
- Are tests meaningful and maintainable?
- Are naming, modularity, and project conventions respected?
- Are migrations and compatibility safe?

## Findings
For each finding provide:
- Severity: Critical / High / Medium / Low
- File and line or exact location
- Concrete impact
- Reproduction or reasoning
- Recommended correction

## Guardrails
- Report actionable defects, not personal style preferences.
- Do not approve work without inspecting the relevant diff and evidence.
