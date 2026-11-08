# AI Agent Ecosystem

**Version:** `0.2.0` — Single-repository Antigravity plugin  
**Runtime:** Google Antigravity (`agy`)  
**License:** MIT

A complete multi-agent engineering team distributed as **one GitHub repository and one installable Antigravity plugin**. The bundle includes Architecture, Product Design, Frontend, Backend, Infrastructure, QA, and Team Orchestrator agents, plus shared engineering skills and constitution rules.

## Install — one command

```powershell
agy plugin install https://github.com/hd159/ai-agent
```

Then verify:

```powershell
agy plugin list
agy agents
```

To update, run the same install command again. To uninstall:

```powershell
agy plugin uninstall ai-agent
```

All specialists ship together. You do **not** need to install or clone nine separate repositories, copy plugin folders, or run a local folder installer.

## Included agents

| Agent | Responsibility |
|---|---|
| `team-orchestrator` | Team composition, task graph, delegation, handoffs, execution state |
| `architecture-agent` | Product-to-system architecture, module boundaries, ADRs, task decomposition |
| `uiux-design-agent` | User journeys, information architecture, interaction and design specifications |
| `frontend-agent` | Frontend implementation, client state, API integration, accessibility |
| `backend-agent` | Domain logic, APIs, persistence, authorization, integrations |
| `infrastructure-agent` | Cloud/runtime, IaC, CI/CD, secrets, observability, operations |
| `qa-agent` | Test strategy, acceptance, regression, independent verification |

Also included:
- **16 reusable skills** for product discovery, MVP scoping, architecture, API/data design, task decomposition, TDD, debugging, code review, deployment readiness, and verification.
- **Shared constitution rules** for scoped changes, explicit assumptions, simplicity, and evidence-based completion.
- **SaaS MVP team preset**, task/handoff contracts, project templates, and evaluation scenarios.

## Repository design

This repository is both the canonical source and the installable plugin:

```text
ai-agent/
├── plugin.json                 # Root manifest; agy installs this repository
├── agents/                     # Generated bundle: all 7 specialist agents
├── skills/                     # Generated bundle: all 16 skills
├── rules/                      # Generated shared agent rules
├── modules/                    # Canonical source modules for each specialist
├── teams/                      # Logical team composition presets
├── contracts/                  # Agent/task/team/handoff JSON schemas
├── workflows/                  # Project lifecycle workflows
├── templates/                  # Project and artifact templates
├── docs/                       # Architecture, security, and adapter docs
└── scripts/                    # Build, install helper, and validators
```

The root `agents/`, `skills/`, `rules/`, and `plugin.json` are generated from the canonical modules under `modules/`. Do not hand-edit generated files; update the source module and rebuild.

## Development

Requirements: Python 3.10+.

Build the single plugin bundle after changing agents, skills, or rules:

```powershell
python .\scripts\build_single_plugin.py
```

Validate the source and generated installable plugin:

```powershell
python .\scripts\validate_repo.py
python .\scripts\validate_plugin.py
python .\scripts\build_single_plugin.py --check
```

Optional helper to install the same single repository while validating the logical team preset:

```powershell
python .\scripts\install_team.py --team saas-mvp
```

The helper invokes exactly one command: `agy plugin install https://github.com/hd159/ai-agent`.

## Team Orchestration

`teams/saas-mvp/team.json` describes the logical team composition, workflow stages, approval gates, and execution constraints. It is a coordination contract, not a distributed scheduler. The Team Orchestrator uses native subagent delegation only when the installed Antigravity runtime supports it; otherwise it prepares dispatch-ready task contracts and reports that automatic dispatch is unavailable.

Start a project by asking Team Orchestrator to read `.agent-ecosystem/team.json` and `.agent-ecosystem/PROJECT_CONTEXT.md`. Bootstrap project artifacts with:

```powershell
python .\scripts\init_project.py --team saas-mvp --target ..\my-saas-app
```

## Design principles

1. **One repository, one install.** All agents, skills, and rules are distributed together from this repository.
2. **Modular source, unified runtime.** Specialist source modules remain separated under `modules/`; the build script assembles one root plugin bundle.
3. **Shared skills, not duplicated procedures.** Skills are portable and reusable across specialist agents.
4. **Project teams are configuration.** A team manifest selects roles and workflow stages without requiring separate plugin repositories.
5. **No false completion.** Work is complete only when acceptance criteria and evidence are recorded.
6. **Human approval gates.** MVP scope, material architecture decisions, and production deployment require explicit approval.

## Current limitations

- Native subagent delegation depends on Antigravity runtime support and agent discovery.
- The team manifest is declarative; it does not create a distributed scheduler.
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
