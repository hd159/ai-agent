# AI Agent Ecosystem

**Version:** `0.2.0` — Single-repository Antigravity plugin  
**Runtime:** Google Antigravity (`agy`)  
**License:** MIT

A complete multi-agent engineering team distributed as **one GitHub repository and one installable Antigravity plugin**. The bundle includes Architecture, Product Design, Frontend, Backend, Infrastructure, QA, and Team Orchestrator agents, plus shared engineering skills and constitution rules.

## Install — one command

~~~powershell
agy plugin install https://github.com/hd159/ai-agent
~~~

Then verify:

~~~powershell
agy plugin list
agy agents
~~~

To update, run the same install command again. To uninstall:

~~~powershell
agy plugin uninstall ai-agent
~~~

All specialists ship together. You do **not** need to install or clone nine separate repositories, copy plugin folders, or run a local folder installer.

## Included agents

| Agent | Responsibility |
|---|---|
| `team-orchestrator` | Team composition, task graph, delegation, handoffs, execution state, and persistent project memory |
| `architecture-agent` | Product-to-system architecture, module boundaries, ADRs, task decomposition |
| `uiux-design-agent` | User journeys, information architecture, interaction and design specifications |
| `frontend-agent` | Frontend implementation, client state, API integration, accessibility |
| `backend-agent` | Domain logic, APIs, persistence, authorization, integrations |
| `infrastructure-agent` | Cloud/runtime, IaC, CI/CD, secrets, observability, operations |
| `qa-agent` | Test strategy, acceptance, regression, independent verification |

Also included:
- **18 reusable skills** for product discovery, MVP scoping, architecture, API/data design, task decomposition, project memory, session checkpointing, TDD, debugging, code review, deployment readiness, and verification.
- **Shared constitution rules** for scoped changes, explicit assumptions, simplicity, and evidence-based completion.
- **SaaS MVP team preset**, task/handoff contracts, project templates, and evaluation scenarios.

## Repository design

This repository is both the canonical source and the installable plugin:

~~~text
ai-agent/
├── plugin.json                 # Root manifest; agy installs this repository
├── agents/                     # Generated bundle: all 7 specialist agents
├── skills/                     # Generated bundle: all 18 skills
├── rules/                      # Generated shared agent rules
├── modules/                    # Canonical source modules for each specialist
├── teams/                      # Logical team composition presets
├── contracts/                  # Agent/task/team/handoff/memory schemas
├── docs/                       # Architecture, security, and adapter docs
├── evals/                      # Agent and workflow evaluation scenarios
├── templates/                  # Project, execution, and artifact templates
└── scripts/                    # Build, bootstrap, install helper, and validators
~~~

The root `agents/`, `skills/`, `rules/`, and `plugin.json` are generated from the canonical modules under `modules/`. Do not hand-edit generated files; update the source module and rebuild.

## Persistent Project Memory

The ecosystem uses **Git-backed, project-local memory**. It does not depend on a chat transcript or require a separate database for a single-repository project.

Each initialized project gets:

~~~text
.agent-ecosystem/
├── PROJECT_CONTEXT.md           # Stable project context and constraints
├── team.json                    # Selected team and workflow
├── artifacts/                   # Architecture, ADRs, product and delivery docs
└── execution/
    ├── plan.json                # Planned phases and approval gates
    ├── state.json               # Current execution snapshot
    ├── tasks/                   # Detailed task contracts
    ├── handoffs/                # Specialist handoff records
    ├── sessions/                # Append-only session checkpoints
    └── decisions/               # Decision log and references
~~~

The three persistence layers have distinct responsibilities:

1. **Project memory:** architecture, requirements, constraints, and approved decisions.
2. **Execution state:** current phase, task statuses, blockers, pending decisions, evidence, and next actions.
3. **Session journal:** what happened in each work session and where the next session should resume.

The Team Orchestrator must load the current state before continuing an existing project, checkpoint after meaningful task outcomes, and write a session journal before handing work back. Specialist agents return handoffs; the orchestrator is the single writer that reconciles those handoffs into the shared execution state.

Session journals are historical records, not the current source of truth. Current source code, approved architecture/ADRs, task contracts, and `state.json` must be reconciled when they disagree. Never store credentials, access tokens, private keys, or other secrets in project memory.

Bootstrap a project:

~~~powershell
python .\scripts\init_project.py --team saas-mvp --target ..\my-saas-app
~~~

For the complete read/resume/checkpoint protocol, see [Persistent Project Memory](docs/architecture/PERSISTENT-PROJECT-MEMORY.md).

## Development

Requirements: Python 3.10+.

Build the single plugin bundle after changing agents, skills, or rules:

~~~powershell
python .\scripts\build_single_plugin.py
~~~

Validate the source and generated installable plugin:

~~~powershell
python .\scripts\validate_repo.py
python .\scripts\validate_plugin.py
python .\scripts\build_single_plugin.py --check
~~~

Optional helper to install the same single repository while validating the logical team preset:

~~~powershell
python .\scripts\install_team.py --team saas-mvp
~~~

The helper invokes exactly one command: `agy plugin install https://github.com/hd159/ai-agent`.

## Team Orchestration

`teams/saas-mvp/team.json` describes the logical team composition, workflow stages, approval gates, and execution constraints. It is a coordination contract, not a distributed scheduler. The Team Orchestrator uses native subagent delegation only when the installed Antigravity runtime supports it; otherwise it prepares dispatch-ready task contracts and reports that automatic dispatch is unavailable.

Start a project by asking Team Orchestrator to read `.agent-ecosystem/team.json` and `.agent-ecosystem/PROJECT_CONTEXT.md`. Bootstrap project artifacts with:

~~~powershell
python .\scripts\init_project.py --team saas-mvp --target ..\my-saas-app
~~~

## Design principles

1. **One repository, one install.** All agents, skills, and rules are distributed together from this repository.
2. **Modular source, unified runtime.** Specialist source modules remain separated under `modules/`; the build script assembles one root plugin bundle.
3. **Shared skills, not duplicated procedures.** Skills are portable and reusable across specialist agents.
4. **Project teams are configuration.** A team manifest selects roles and workflow stages without requiring separate plugin repositories.
5. **Persistent, evidence-based continuity.** Project state survives chat sessions through versionable files, task contracts, handoffs, and checkpoints.
6. **No false completion.** Work is complete only when acceptance criteria and evidence are recorded.
7. **Human approval gates.** MVP scope, material architecture decisions, and production deployment require explicit approval.

## Current limitations

- Native subagent delegation depends on Antigravity runtime support and agent discovery.
- The team manifest is declarative; it does not create a distributed scheduler.
- Session checkpointing is an explicit agent workflow, not a guaranteed host shutdown hook. The orchestrator must checkpoint at task boundaries and before returning control.
- Git-backed memory is project-local. Multi-user, multi-workspace centralized memory is outside the current scope.
- Codex and Claude Code adapters remain future work.

## References

- [Antigravity — Build plugins](https://antigravity.google/docs/build-plugins)
- [Antigravity — Plugins and GitHub installation](https://antigravity.google/docs/plugins)
- [Antigravity — Custom subagents](https://antigravity.google/docs/subagents)
- [Agent Skills specification](https://agentskills.io/)
- [obra/superpowers](https://github.com/obra/superpowers)
- [mattpocock/skills](https://github.com/mattpocock/skills)
- [garrytan/gstack](https://github.com/garrytan/gstack)
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)
