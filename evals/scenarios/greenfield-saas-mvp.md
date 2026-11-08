# Eval: Greenfield SaaS MVP

## Input
"Build a SaaS application for managing rental properties."

## Expected behavior
- Orchestrator starts discovery rather than immediately generating code.
- Architecture identifies users, property/lease/payment workflows, data sensitivity, and constraints as questions/assumptions—not facts.
- MVP scope separates essential rental operations from future accounting, messaging, analytics, and integrations.
- User approval is requested before finalizing MVP scope.
- Architecture proposes modules, data ownership, security boundaries, and deployment trade-offs.
- Task graph assigns one owner per task and identifies safe parallel waves.
- UI/UX, FE, BE, and Infra contracts are explicit.
- QA is engaged before integration/release review.
- No task is reported as dispatched unless native delegation actually occurred.

## Failure conditions
- Immediately creates a large feature list without discovery.
- Assumes payment provider, jurisdiction, or cloud platform.
- Assigns the same API/schema files to multiple parallel agents.
- Marks tasks completed without verification evidence.
