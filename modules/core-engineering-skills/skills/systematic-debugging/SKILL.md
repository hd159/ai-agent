---
name: systematic-debugging
description: >-
  Diagnose bugs using evidence, reproduction, hypothesis testing, and root
  cause analysis. Use when behavior is unexpected or tests fail.
---

# Systematic Debugging

## Procedure
1. Reproduce the issue or clearly state why it cannot yet be reproduced.
2. Capture the exact error, inputs, environment, and observed behavior.
3. Identify the narrowest failing boundary.
4. Form one or more falsifiable hypotheses.
5. Run targeted experiments that distinguish the hypotheses.
6. Trace the failure to its root cause rather than patching symptoms.
7. Implement the smallest correction.
8. Add a regression test.
9. Verify adjacent behavior and document residual risk.

## Output
Reproduction steps, root cause, fix, regression test, verification, and remaining uncertainty.

## Guardrails
- Do not make several unrelated changes before confirming a hypothesis.
- Do not suppress errors to make the symptom disappear.
