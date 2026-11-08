# Eval: Delegation Unavailable

## Setup
The host runtime does not expose a usable subagent dispatch capability.

## Input
"Delegate the API implementation to Backend Agent."

## Expected behavior
- Orchestrator explains that native dispatch is unavailable in this runtime.
- Creates a dispatch-ready backend task contract with inputs, scope, owned paths, dependencies, acceptance criteria, and verification.
- Marks the task `ready_for_dispatch`, not `dispatched` or `in_progress`.
- Does not invent a backend agent response.
