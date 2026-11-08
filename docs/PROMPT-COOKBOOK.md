# Prompt Cookbook

Use these prompts with Team Orchestrator unless a specialist is explicitly named. Replace bracketed text with the project-specific details.

## 1. Initialize a new project

~~~text
Initialize this project. Inspect the repository, identify the product,
users, stack, integrations, and constraints. Create project memory if it
does not exist. Start with read-only discovery. Do not implement code
until I approve the scope.
~~~

## 2. Resume an existing project

~~~text
Resume this project. Read project memory, current plan and task contracts,
unresolved handoffs, and the latest session checkpoint. Reconcile them
against the current Git branch, HEAD, working tree, and relevant source.
Report completed, active, blocked, pending, and next tasks with evidence.
~~~

## 3. Show project status

~~~text
Show the current project status. Verify state.json against the source and
Git state. Summarize phase, completed tasks with evidence, active work,
blockers, pending approvals, and the next three actions.
~~~

## 4. Plan and implement a feature

~~~text
Plan and implement this feature: [feature description].

Clarify user outcome and acceptance criteria. Inspect architecture and
request UX/architecture input where needed. Define API/data/design
contracts, split implementation into owned task contracts, and dispatch
only dependency-ready tasks. Keep parallel work non-overlapping.
Run QA and integration checks before completion. Stop at approval gates.
~~~

## 5. Fix a bug

~~~text
Investigate and fix this bug: [steps, expected result, actual result].

Reproduce it first. Identify the root cause, add a regression test, assign
the smallest suitable owner, implement the minimal safe fix, and request
independent QA verification. Do not refactor unrelated code.
~~~

## 6. Architecture delta review

~~~text
Review the current architecture against the approved baseline.

Inspect the current Git commit and source. Classify each existing finding
as confirmed, fixed, stale, false positive, or needs verification.
Preserve historical audits. Update current architecture and findings
register with source evidence. Do not modify application code.
~~~

## 7. Security review

~~~text
Perform a scoped security review of [module/flow].

Trace trust boundaries, authentication, authorization, validation,
secrets, data access, external calls, failure handling, and logging.
For each finding include severity, confidence, source evidence, impact,
minimal remediation, owner, and positive/negative verification tests.
Do not claim exploitability without evidence.
~~~

## 8. UX design

~~~text
Design the user journey for [feature/page].

Inspect existing product patterns and design system. Identify target user,
job, page hierarchy, primary action, responsive behavior, accessibility,
and loading/empty/error/success states. Produce an implementation-ready
specification. Do not change source code.
~~~

## 9. Backend implementation

~~~text
Implement the approved backend contract for [feature].

Inspect existing conventions. Enforce authorization and validation at
the server boundary. Add unit/integration tests, migrations if needed,
and document compatibility/rollback. Stay within the task's owned paths.
~~~

## 10. Frontend implementation

~~~text
Implement the approved UX and API contract for [feature].

Reuse the existing design system and project conventions. Cover loading,
empty, error, success, accessibility, and responsive states. Add tests
and avoid inventing backend behavior.
~~~

## 11. QA verification

~~~text
Independently verify task [TASK-ID].

Read its contract and changed files. Run the required tests. Check positive,
negative, edge, authorization, and regression cases. Return passed,
failed, blocked, and not-run results with reproducible evidence. Do not
modify implementation unless explicitly assigned.
~~~

## 12. Refactor safely

~~~text
Refactor [module] without changing externally observable behavior.

Establish the test baseline, define non-goals, identify compatibility
constraints, split into reversible increments, and run regression tests
after each increment. Stop if behavior changes unexpectedly.
~~~

## 13. Prepare a release

~~~text
Prepare a release-readiness review for [release/version].

Check test evidence, migrations, secrets, configuration, observability,
backup/restore, rollback, security, dependencies, and known blockers.
Produce a go/no-go recommendation. Do not deploy or change production
without my explicit approval.
~~~

## 14. Checkpoint and stop

~~~text
Checkpoint this session. Reconcile task contracts and state.json against
actual source changes and test output. Write a new dated session journal,
read back the saved files, and report exactly what was persisted and
where the next session should resume.
~~~

## Prompt quality checklist

A good request provides:
- Context: product, module, user, and current behavior.
- Goal: observable outcome.
- Source: files, API, logs, or documents to inspect.
- Constraints: scope, compatibility, security, and non-goals.
- Acceptance criteria: what must be true.
- Verification: how success will be demonstrated.
- Approval boundary: what the agent may change without asking.
