# Ecosystem Architecture

**Status:** Accepted for v0.4.0  
**Scope:** Reusable specialist agents, portable skills, project teams, shared project memory, and native multi-runtime distribution.

## 1. Goals

- Create focused specialist agents that remain modular in source and are distributed together through native runtime adapters generated from one repository.
- Separate role identity from reusable capabilities.
- Compose teams per project without creating a new agent for every project.
- Make task ownership, dependencies, boundaries, and completion evidence explicit.
- Keep core knowledge portable across compatible agent runtimes.

## 2. Non-goals for v0.4.0

- A cloud-hosted multi-tenant agent control plane.
- A distributed scheduler with durable remote queues.
- Automatic GitHub repository creation or publishing is outside the runtime orchestration scope.
- Automatic deployment to production.
- Guaranteed cross-platform parity for every runtime feature or delegation surface.

## 3. Logical layers

### Layer A — Constitution

Global behavioral constraints:
- Think before acting.
- Prefer the simplest adequate solution.
- Make scoped changes.
- Work toward observable goals.
- Protect user data and secrets.
- Verify before claiming completion.

### Layer B — Skills

Reusable procedures packaged as Agent Skills:
- Product discovery and MVP scoping.
- Architecture and task decomposition.
- API and database design.
- TDD, debugging, review, and verification.

A skill is a capability, not an agent identity.

### Layer C — Specialist agents

Each agent owns a specialist identity and its prompt. Initial specialists:
- Architecture
- UI/UX Design
- Frontend
- Backend
- Infrastructure
- QA
- Team Orchestrator

One focused specialist identity per agent is the default. Multiple agent definitions are bundled together in the single installable plugin.

### Layer D — Team composition

A project-level `team.json` declares:
- Orchestrator
- Shared source modules and capabilities
- Specialist members
- Workflow stages
- Approval gates
- Concurrency and conflict policy

A team manifest is configuration, not an execution engine.

### Layer E — Orchestration

The orchestrator:
1. Reads project context and team manifest.
2. Selects the relevant specialists.
3. Produces a project brief and MVP scope.
4. Establishes architecture and contracts.
5. Decomposes work into tasks.
6. Resolves dependencies.
7. Delegates ready tasks where runtime support exists.
8. Reviews handoffs and integration evidence.
9. Reports blockers and actual completion state.

### Layer F — Platform adapters

Antigravity remains the backward-compatible plugin adapter. Codex CLI, GitHub Copilot CLI / supported VS Code agent mode, and Claude Code CLI are generated from the same canonical role instructions and skills. Native tool permissions and delegation remain runtime-specific.

## 4. Independent agent plugin contract

Each agent module must declare:
- Unique agent ID and source module ID.
- One primary specialist identity.
- Mission and expertise.
- Responsibilities and explicit boundaries.
- Required inputs and expected outputs.
- Handoff protocol.
- Quality gates.
- Tool and permission assumptions.

An agent may recommend changes outside its ownership, but must not silently take ownership of another specialist's contract.

## 5. Execution model

Use a dependency-aware task graph.

A task may start only when:
- Its inputs are available.
- Its dependencies are complete.
- Its owned paths do not conflict with active tasks.
- Required approvals have been granted.

Parallel execution is allowed only for independent tasks. Shared files and contracts require a designated owner or an explicit integration task.

## 6. Runtime fallback

If the host runtime supports native subagent invocation, the orchestrator may delegate bounded tasks to installed specialists.

If it does not:
- The orchestrator may execute bounded work itself only when its own required capabilities are verified and the task is within the approved project scope.
- If required capabilities are unavailable, block the dependent implementation and report the exact blocker.
- Do not silently substitute planning-only task contracts or dependency graphs for requested implementation; create planning-only artifacts only when the user explicitly asks.
- Never imply that agents were called when they were not.

## 7. Human approval gates

Required gates:
- `mvp_scope`: user approves MVP scope and non-goals.
- `architecture`: user approves material architecture choices and trade-offs.
- `production_deployment`: user explicitly authorizes production deployment.

The orchestrator may continue discovery and preparation while waiting, but must not cross a gate without approval.

## 8. Completion semantics

`completed` means:
- Acceptance criteria are satisfied.
- Verification commands or checks ran.
- Evidence is attached to the task or handoff.
- No unresolved blocker invalidates the result.

An agent response saying "done" is not evidence by itself.

## 9. Distribution topology (v0.4.0)

The Antigravity adapter remains a single plugin in `hd159/ai-agent` and is installed with one `agy plugin install https://github.com/hd159/ai-agent` command. The other runtime adapters are generated project files; see section 10. Canonical source modules live under `modules/<module-id>/`. Team presets are logical composition manifests, not separate plugin distributions.


## 10. Hybrid multi-runtime distribution

The ecosystem uses one canonical repository. The existing Antigravity plugin remains version 0.3.2 for backward compatibility; the shared ecosystem and source modules advance to 0.4.0.

The native adapter builder generates:
- Codex CLI: AGENTS.md, .codex/agents/*.toml, and .agents/skills/.
- GitHub Copilot CLI / supported VS Code agent mode: .github/copilot-instructions.md, .github/agents/*.agent.md, and .agents/skills/.
- Claude Code CLI: CLAUDE.md, .claude/agents/*.md, and .claude/skills/.

The installer merges root instructions inside explicit managed markers, records installer-owned paths under .agent-ecosystem/adapters/, refuses to overwrite unmanaged conflicting profiles or skills, and supports safe uninstall. Generated adapter files are derived artifacts, not new sources of truth.

See [Multi-Platform Adapter Architecture](MULTI-PLATFORM-ADAPTERS.md) for build, validation, runtime boundaries, and versioning.
