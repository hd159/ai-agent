# AI Agent Ecosystem

**Version:** `0.3.1` — Single-repository Antigravity plugin  
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
agy plugin list --json
agy agents
~~~

To update, run the same install command again. To uninstall:

~~~powershell
agy plugin uninstall ai-agent
~~~

All specialists ship together. You do **not** need to install or clone nine separate repositories, copy plugin folders, or run a local folder installer.

## Selecting an agent

**App:** Open Customizations > Installed > ai-agent > Agents, then use the agent selector to start a new Team Orchestrator session. App `@team-orchestrator` is not a primary-agent selector; `@` searches project references.

**CLI:** Open the product workspace and run `agy --agent team-orchestrator` (or open `/agents`). CLI `@` messages an existing subagent, not a primary agent.

If the custom agent can only read files despite Turbo, see [Agent Diagnostics](docs/AGENT-DIAGNOSTICS.md). Check actual tools in a new session and compare with the built-in agent; plugin packaging validation alone does not prove write/terminal capabilities.

## Capability validation

All seven bundled agents have no `tools` allowlist, declare `inheritMcp: true`
and `inheritCustomizations: true`, and discover 19 bundled skills on demand.
MCP servers are inherited from the user environment; no MCP server ships with this plugin.

~~~powershell
python -m pip install -r requirements-dev.txt
python .\scripts\validate_capabilities.py
~~~

Use `/capability-smoke-test` in a fresh Antigravity session **for each agent**
to test real file write/read, shell, skill activation and connected MCP tools.
Static validation does not grant permissions or prove the host exposed tools.

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
- **19 reusable skills** for product discovery, MVP scoping, architecture, API/data design, task decomposition, project memory, session checkpointing, TDD, debugging, code review, deployment readiness, and verification.
- **Shared constitution rules** for scoped changes, explicit assumptions, simplicity, and evidence-based completion.
- **SaaS MVP team preset**, task/handoff contracts, project templates, and evaluation scenarios.

## Repository design

This repository is both the canonical source and the installable plugin:

~~~text
ai-agent/
├── plugin.json                 # Root manifest; agy installs this repository
├── agents/                     # Generated bundle: all 7 specialist agents
├── skills/                     # Generated bundle: all 19 skills
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


## Agent tool access and mandatory preflight

All seven bundled agents omit a per-agent `tools` allowlist, so the plugin requests Antigravity's documented default built-in tool exposure. Keep their YAML frontmatter valid and omit the `tools` property entirely. Their YAML frontmatter intentionally omits the `tools` property; for bundled plugin agents, Antigravity documents omission as the default that exposes all built-in tools. Do not add a partial list or `tools: []`, because that would restrict the agent.

Every agent also sets:
- `inheritMcp: true` — inherit MCP servers and tools configured for the parent session.
- `inheritCustomizations: true` — inherit applicable workspace skills, rules, and hooks.
- `commandExecutionPolicy` is intentionally omitted — the plugin does not pin a per-agent command execution policy.

**The agent's role defines responsibility, not tool availability.** UI/UX, QA, Frontend, Backend, Infrastructure, Architecture, and Orchestrator can all use available built-in tools and inherited MCP tools when useful.

The user remains in control of execution and security through Antigravity settings: permission presets, allow/ask/deny rules, terminal auto-execution, sandboxing, workspace boundaries, non-workspace file access, and MCP permissions. Tool exposure does not prove an operation is authorized or succeeds. Before implementation or dispatch, run `/capability-smoke-test` in the exact agent/session/workspace and block dependent work until required operations are verified. The framework detects and gates missing capabilities; it cannot grant host permissions.

The full-access contract is defined in [contracts/agent-tool-policy.json](contracts/agent-tool-policy.json) and checked by [scripts/validate_agent_tools.py](scripts/validate_agent_tools.py). If an operation is denied or not exposed, diagnose the host permission/runtime restriction rather than assuming the agent can work around it. Run `/capability-smoke-test` before each task that needs write, terminal, MCP or delegation access. A read-only probe cannot establish write permission.

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
    ├── verification/            # Independent QA records and sanitized evidence logs
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

Requirements: Python 3.10+ (quality gate CLI also requires `python -m pip install -r requirements-dev.txt`).

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
python -m unittest discover -s tests -v
~~~

Optional helper to install the same single repository while validating the logical team preset:

~~~powershell
python .\scripts\install_team.py --team saas-mvp
~~~

The helper invokes exactly one command: `agy plugin install https://github.com/hd159/ai-agent`.

## Team Orchestration

`teams/saas-mvp/team.json` describes the logical team composition, workflow stages, approval gates, and execution constraints. It is a coordination contract, not a distributed scheduler. The Team Orchestrator uses native subagent delegation when the installed Antigravity runtime supports it. If delegation is unavailable, it executes bounded implementation directly when its required capabilities are verified and the work is within the approved project scope. If a required capability is unavailable or denied, it blocks the dependent implementation and reports the exact runtime blocker; it does not automatically replace implementation with task contracts or execution plans. Planning and handoff artifacts are created only when explicitly requested.

Start a project by asking Team Orchestrator to read `.agent-ecosystem/team.json` and `.agent-ecosystem/PROJECT_CONTEXT.md`. Bootstrap project artifacts with:

~~~powershell
python .\scripts\init_project.py --team saas-mvp --target ..\my-saas-app
~~~


## v0.3 Quality Gates

The framework now includes a **read-only, fail-closed project validator** for task/state/handoff schemas, dependency graphs, independent QA approval, acceptance evidence, Git source freshness, and mandatory production approval records.

```powershell
python -m pip install -r requirements-dev.txt
python .\scripts\quality_gate.py validate --project ..\my-saas-app
python .\scripts\quality_gate.py task --project ..\my-saas-app --task-id BE-001
python .\scripts\quality_gate.py release --project ..\my-saas-app
```

**Trust boundary:** the gate checks the authenticity of neither the user's approval nor whether commands genuinely ran. For enforceable release controls, use protected branches, required external CI checks and human approval. Learn more in [Quality Gates](docs/QUALITY-GATES.md).

## Documentation Roadmap

The user documentation is organized by the lifecycle of adopting and using the ecosystem:

| Document | What it covers |
|---|---|
| [User Guide](docs/USER-GUIDE.md) | Install, verify agents, open a project, choose Orchestrator or a specialist, work on features/bugs, and resume sessions |
| [Agent Diagnostics](docs/AGENT-DIAGNOSTICS.md) | Agent selection, actual runtime tool availability, and host troubleshooting |
| [Command Reference](docs/COMMAND-REFERENCE.md) | Antigravity CLI commands, Python scripts, parameters, validation, and Windows examples |
| [Orchestration Workflow](docs/ORCHESTRATION-WORKFLOW.md) | Task contracts, lifecycle, dependency-aware dispatch, parallel ownership, handoffs, QA, and checkpoints |
| [Project Bootstrap](docs/PROJECT-BOOTSTRAP.md) | New vs existing projects, one-time initialization, recovery, source discovery, and safe reinitialization |
| [Architecture Documentation Standard](docs/ARCHITECTURE-DOCUMENTATION-STANDARD.md) | Audit versioning, current/target architecture, C4, ADRs, findings register, scoring, and evidence |
| [Quality Gates](docs/QUALITY-GATES.md) | Executable task, evidence, state and release gate checks |
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
