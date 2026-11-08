---
name: test-driven-development
description: >-
  Implement behavior using a test-first RED, GREEN, REFACTOR loop. Use for
  new business logic, bug fixes, and behavior changes where tests are feasible.
---

# Test-Driven Development

## Procedure
1. Read the acceptance criteria and identify the smallest observable behavior.
2. Add a focused test that demonstrates the expected behavior and fails for the right reason.
3. Run the test and record the RED result.
4. Implement the smallest change that makes the test pass.
5. Run the focused test and record the GREEN result.
6. Refactor while keeping tests green.
7. Run relevant regression tests and static checks.
8. Report any untested behavior and explain why.

## Guardrails
- Do not write a test that merely mirrors the implementation.
- Do not weaken or delete a failing test to obtain a green build.
- Do not claim tests passed unless the command actually ran and returned success.
