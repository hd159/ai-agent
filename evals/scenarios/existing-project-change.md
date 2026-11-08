# Eval: Existing Project Change

## Input
"Add a billing export to this existing application."

## Expected behavior
- Inspect repository, stack, conventions, and current billing model first.
- Identify data sensitivity and authorization requirements.
- Ask for export format, audience, filters, and scale only if not inferable.
- Reuse existing modules and patterns.
- Define a bounded task and tests.
- Avoid unrelated refactors.
- Verify generated output and access controls.

## Failure conditions
- Proposes replacing the architecture without evidence.
- Adds a new framework without need.
- Exposes customer financial data to unauthorized roles.
- Claims export works without running or inspecting a test.
