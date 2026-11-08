# AI Agent Ecosystem

**Version:** `0.2.1` — Single-repository Antigravity plugin  
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


## Agent tool access

Every bundled custom agent declares an explicit, role-specific Antigravity built-in tool allowlist in its YAML frontmatter. The Orchestrator has file read/write, search, terminal, and subagent management tools; implementation specialists have the file-edit and terminal tools required by their role; UI/UX can create design artifacts without a terminal by default.

Do not rely on implicit tool defaults. Antigravity documentation describes tool allowlists and defaults across different agent surfaces; this repository uses explicit profiles to avoid runtime ambiguity.

Important:
- **tools** controls which tools are exposed to an agent.
- **commandExecutionPolicy** controls shell execution behavior; it does not grant missing tools.
- Host permission settings still govern workspace boundaries, sandboxing, and approval.
- The Orchestrator is the only bundled agent with **invoke_subagent** and **manage_subagents**.
- Tool profiles are defined in [contracts/agent-tool-policy.json](contracts/agent-tool-policy.json) and checked by [scripts/validate_agent_tools.py](scripts/validate_agent_tools.py).

If an agent reports that it cannot write files or run commands, first verify the selected agent's generated frontmatter, active workspace root, and Antigravity permission settings. Do not switch to unrestricted permissions to compensate for a missing tool declaration.

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

For the complete read/resume/checkpoint protocol, see [Persistent Project Memory](docs/architecture/PERSISTENT-PROJECT-MEMORY.md) and the [Project Bootstrap Guide](docs/PROJECT-BOOTSTRAP.md).

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
python .\scripts\validate_agent_tools.py
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


## Documentation Roadmap

The user documentation is organized by the lifecycle of adopting and using the ecosystem:

| Document | What it covers |
|---|---|
| [User Guide](docs/USER-GUIDE.md) | Install, verify agents, open a project, choose Orchestrator or a specialist, work on features/bugs, and resume sessions |
| [Command Reference](docs/COMMAND-REFERENCE.md) | Antigravity CLI commands, Python scripts, parameters, validation, and Windows examples |
| [Orchestration Workflow](docs/ORCHESTRATION-WORKFLOW.md) | Task contracts, lifecycle, dependency-aware dispatch, parallel ownership, handoffs, QA, and checkpoints |
| [Project Bootstrap](docs/PROJECT-BOOTSTRAP.md) | New vs existing projects, one-time initialization, recovery, source discovery, and safe reinitialization |
| [Architecture Documentation Standard](docs/ARCHITECTURE-DOCUMENTATION-STANDARD.md) | Audit versioning, current/target architecture, C4, ADRs, findings register, scoring, and evidence |
| [Prompt Cookbook](docs/PROMPT-COOKBOOK.md) | Reusable prompts for initialization, resume, feature work, bug fixes, architecture/security review, QA, and release |

### Architecture and project templates

- [Persistent Project Memory](docs/architecture/PERSISTENT-PROJECT-MEMORY.md)
- [Architecture Audit Template](templates/artifacts/architecture/ARCHITECTURE-AUDIT-TEMPLATE.md)
- [Findings Register Template](templates/artifacts/architecture/FINDINGS-REGISTER-TEMPLATE.md)
- [ADR Template](templates/artifacts/ADR.md)

The documentation is generic and belongs in this ecosystem repository. Product-specific architecture audits, ADRs, findings, and execution state must remain in the target product repository under .agent-ecosystem/.

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
