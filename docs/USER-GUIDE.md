# AI Agent Ecosystem — User Guide

This guide explains how to install the reusable agent team, open a project, initialize project memory, delegate work, and resume work across sessions.

## 1. What is installed?

Install the AI Agent Ecosystem once in Antigravity. One plugin contains:

- Team Orchestrator — primary project coordinator.
- Architecture Agent — architecture, ADRs, module boundaries, task decomposition.
- UI/UX Design Agent — journeys, information architecture, interaction specifications.
- Frontend Agent — frontend implementation and tests.
- Backend Agent — APIs, domain logic, persistence, authorization, integrations.
- Infrastructure Agent — runtime, CI/CD, secrets, observability, operations.
- QA Agent — independent test planning, regression, acceptance evidence.
- Shared skills, engineering rules, team presets, and project templates.

The plugin repository is generic. Product code, project context, architecture decisions, task state, and session history belong in each product repository.

## 2. Install and verify

Run in PowerShell or the Antigravity CLI terminal:

~~~powershell
agy plugin install https://github.com/hd159/ai-agent
agy plugin list
agy agents
~~~

To update the plugin, run the install command again. To remove it:

~~~powershell
agy plugin uninstall ai-agent
~~~

After updating, restart Antigravity and start a new session to load the updated agent definition. Check `agy plugin list --json` and `agy agents`. In the Antigravity App select Team Orchestrator using the agent selector (or Customizations > Installed > ai-agent > Agents). Do not type `@team-orchestrator` in the App composer; its `@` search does not select primary agents. In the CLI, use `agy --agent team-orchestrator` from the product repository root.

## 3. Open the correct workspace

Open the root directory of the application you want the agents to work on, for example:

~~~text
C:\work\certvault
~~~

The active workspace should be the product repository, not the ai-agent plugin source repository. In a multi-root workspace, confirm which root contains the files the task should change.

## 4. New project vs existing project

First check whether the project already has a non-empty .agent-ecosystem directory.

- If it exists and contains project memory, do not initialize it again. Ask Team Orchestrator to resume and reconcile it.
- If it does not exist, initialize it once using Project Bootstrap.
- If it exists but is empty, the bootstrap script can populate it.
- If it contains partial files, preserve them and ask Orchestrator to reconcile; do not delete the directory to force initialization.

A new project usually starts with discovery, MVP scope, architecture, and approval. An existing project starts with source inspection, architecture recovery, audit reconciliation, and current-state reporting.

## 5. Start work with Team Orchestrator

Select Team Orchestrator in the Antigravity App agent picker, or run `agy --agent team-orchestrator` in the CLI. CLI `@` can message an existing subagent; App `@` does not select a primary custom agent.

For a new project:

~~~text
Initialize this project. Inspect the repository, understand the product and
technology stack, and create the project context. Start with read-only
discovery. Report the current architecture, risks, unknowns, and recommended
next steps. Do not implement code until I approve the scope.
~~~

For an existing project:

~~~text
Resume this project. Read .agent-ecosystem project memory, inspect Git status
and the current source, reconcile the latest checkpoint, and report completed
work, in-progress tasks, blockers, pending decisions, and the next action.
Do not assume old task statuses are still accurate.
~~~

For a quick status:

~~~text
Show project status from state.json and verify it against the current Git
state. Summarize completed, active, blocked, and next tasks.
~~~

## 6. Which agent should I call?

Use Team Orchestrator for work that spans roles, has dependencies, needs a plan, or should be tracked across sessions.

Call a specialist directly for a focused, bounded task:

| Agent | Good direct assignment |
|---|---|
| Architecture Agent | Review a module boundary, API contract, data model, or ADR |
| UI/UX Design Agent | Design a user journey or page specification |
| Frontend Agent | Implement a defined component or frontend bug fix |
| Backend Agent | Implement a defined endpoint, domain rule, or migration |
| Infrastructure Agent | Review CI/CD, Docker, cloud configuration, or observability |
| QA Agent | Build a test matrix or independently verify a completed change |

A specialist assignment should include the goal, relevant files, constraints, acceptance criteria, and whether implementation is authorized.

## 7. Common work modes

### New feature

Ask Orchestrator to clarify the user outcome, inspect the current architecture, request UX/architecture input as needed, define contracts, create task contracts, dispatch ready work, and coordinate QA.

Approve material changes to product scope, API/data contracts, architecture, and deployment before implementation crosses those gates.

### Bug fix

Ask Orchestrator to reproduce the issue, identify root cause, add a regression test, assign the smallest suitable owner, implement the fix, and request independent verification. Avoid unrelated refactoring.

### Refactoring

Define the behavior that must remain unchanged. Require baseline tests, a bounded file scope, migration/compatibility notes, and regression evidence. Split large refactors into safe increments.

### Architecture or security review

Ask Architecture Agent to inspect actual source and compare it with existing architecture documents and ADRs. Findings must include evidence, severity, confidence, affected paths, recommended remediation, and verification steps.

### Release or deployment

Ask QA and Infrastructure to verify release readiness, rollback, migrations, monitoring, secrets, and operational risks. Production-impacting actions require explicit user approval.

## 8. How task delegation works

Orchestrator creates a task contract before dispatch. A task should include:

- Task ID, title, and one accountable owner.
- Objective, inputs, scope, and exclusions.
- Dependencies and owned paths.
- Acceptance criteria and verification commands.
- Current status, blockers, and evidence.

The normal task lifecycle is:

~~~text
pending -> ready_for_dispatch -> dispatched -> in_progress
        -> in_review -> completed
                    -> blocked / failed
~~~

Only report a task as dispatched after a real subagent invocation. Only report it as completed after acceptance criteria and verification evidence are satisfied.

The default SaaS MVP team allows at most three parallel specialists. Do not allow parallel agents to edit overlapping paths. Use isolated branch/worktree execution for parallel code changes when supported by the host; otherwise serialize conflicting work.

## 9. Persistent project memory

Project memory lives in the application's repository:

~~~text
.agent-ecosystem/
├── PROJECT_CONTEXT.md
├── team.json
├── artifacts/
│   ├── architecture/
│   ├── adr/
│   └── product/
└── execution/
    ├── plan.json
    ├── state.json
    ├── tasks/
    ├── handoffs/
    ├── sessions/
    └── decisions/
~~~

- PROJECT_CONTEXT.md: stable product context and constraints.
- team.json: selected team and workflow policy.
- artifacts/: architecture, ADR, product, and delivery documents.
- plan.json: phases and approval gates.
- state.json: concise current status and next actions.
- tasks/: detailed task contracts.
- handoffs/: specialist results and evidence.
- sessions/: append-only session checkpoints.
- decisions/: decision log and references.

At meaningful task boundaries and before handing control back, Orchestrator must update the affected task, reconcile state.json, create a dated session journal, and read the files back. Never store credentials, tokens, private keys, or secrets in project memory.

## 10. Agent tools and permissions

Every bundled agent receives the **full Antigravity built-in toolset**. Agent frontmatter must remain valid YAML; never leave a tool-list item behind after removing the `tools:` key. The plugin intentionally omits the `tools` property from each agent's YAML frontmatter. For bundled plugin agents, Antigravity documents this as the default that exposes all built-in tools. Do not add a role-specific subset or `tools: []`.

Each agent also declares:
- `inheritMcp: true`: inherit MCP servers and tools configured for the parent session.
- `inheritCustomizations: true`: inherit applicable skills, rules, and hooks.
- No `commandExecutionPolicy`: the plugin does not pin a per-agent command execution policy.

The role of an agent defines its responsibility and task ownership, **not** which tools it is allowed to see. All seven agents can use available file, search, terminal, task, collaboration, question, image, and inherited MCP tools when useful.

### User-controlled permissions

Tool exposure is separate from authorization. Antigravity's host settings remain authoritative for:
- Allow / Ask / Deny decisions and approval prompts.
- Terminal command auto-execution and sandbox mode.
- Workspace and non-workspace file access.
- MCP tool permissions and connected server availability.

On Windows, configure the relevant controls in Antigravity's Agent Settings / permission settings. The exact controls shown depend on the Antigravity version and account type. The plugin does not force Turbo, unrestricted filesystem access, or automatic command approval.

If an agent cannot perform an operation:
1. Confirm the latest plugin version is installed and the updated agent was discovered.
2. Check that its frontmatter omits `tools` and has `inheritMcp: true`.
3. Confirm the correct product repository is the active workspace.
4. Inspect the exact Antigravity permission prompt or denial.
5. Fix the user-controlled host permission only if you want to authorize that operation; do not narrow the plugin's toolset to work around it.

Official references:
- [Build plugins — bundled agents, all tools, and MCP inheritance](https://antigravity.google/docs/build-plugins)
- [Custom subagents](https://antigravity.google/docs/subagents)
- [Agent settings](https://antigravity.google/docs/agent-settings)
- [Permissions](https://antigravity.google/docs/permissions)

## 11. End a session

## 11. End a session

Ask:

~~~text
Checkpoint this session. Reconcile completed, active, blocked, and pending
tasks against source changes and test output. Update task contracts and
state.json, write a new dated session journal, read the files back, and tell
me exactly what is persisted and where the next session should resume.
~~~

A session checkpoint is an explicit agent action. Do not assume the host automatically saves a complete project journal when a conversation ends.

## 12. Validate tasks and release readiness

When using project memory, install CLI dependencies in the `ai-agent` source clone with `python -m pip install -r requirements-dev.txt`. Then run `python scripts/quality_gate.py validate --project <project-root>`, `python scripts/quality_gate.py task --project <project-root> --task-id <TASK-ID>`, or `python scripts/quality_gate.py release --project <project-root>`.

Verification records are stored under the **product** `.agent-ecosystem/execution/verification/` directory. QA must be independent from implementation. The orchestrator cannot mark tasks completed without passing verification. Full details and caveats: [Quality Gates](QUALITY-GATES.md).

## 13. Agent discovery and runtime troubleshooting

See [Agent Diagnostics](AGENT-DIAGNOSTICS.md) when App `@` reports no matches or the selected agent says it cannot write files/run commands. These are separate issues. A successful plugin validation does not demonstrate actual runtime tool access.
