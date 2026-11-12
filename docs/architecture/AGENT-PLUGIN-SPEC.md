# Agent, Plugin Bundle, and Skill Specification

## 1. Definitions

| Concept | Definition |
|---|---|
| Agent | An independent specialist identity with mission, boundaries, and deliverables. |
| Plugin | A versioned distribution unit for one or more agents, skills, rules, MCP servers, or hooks. |
| Skill | A portable procedure that teaches an agent how to perform a bounded class of work. |
| Team | A project-specific composition of agents and workflow stages. |
| Orchestrator | The coordinator that composes a team, dispatches work, resolves dependencies, and integrates results. |

## 2. Packaging rules

- Specialist agents remain modular canonical source files under `modules/<module-id>/agents/`.
- Shared skills remain canonical under the appropriate source module's `skills/` directory.
- Universal rules remain canonical under `modules/agent-constitution/rules/`.
- The canonical distribution unit is one GitHub repository. Antigravity remains a root-level installable plugin; Codex, Copilot, and Claude Code receive generated native project adapters.
- `scripts/build_single_plugin.py` assembles the backward-compatible Antigravity root bundle.
- `scripts/build_adapters.py` generates native Codex, Copilot, and Claude Code layouts from the same agent and skill sources.
- Native project files are installed with `scripts/install_adapter.py`; generated `dist/` output is not a second source of truth.

## 3. Agent frontmatter (Antigravity)

Use the official Antigravity agent fields where supported:

```yaml
---
name: backend-agent
description: >-
  Designs and implements backend services. Delegate API, domain logic,
  database, and backend testing tasks to this specialist.
model: inherit
mainAgent: true
subagent: true
commandExecutionPolicy: auto
tools:
  - read_file
  - write_file
  - edit_file
  - run_command
  - define_subagent
  - invoke_subagent
  - manage_subagents
  - manage_task
  - schedule
  - search_web
  - send_message
  - generate_image
  - ask_question
inheritMcp: true
inheritCustomizations: true
---
```

The Antigravity frontmatter must retain the exact 13-tool list from contracts/agent-tool-policy.json and commandExecutionPolicy: auto. This frontmatter is not portable to Codex, Copilot, or Claude Code; adapters generate native profiles for those runtimes. The body must define:
1. Identity and mission.
2. Responsibilities.
3. Boundaries and escalation conditions.
4. Required inputs.
5. Expected outputs.
6. Working procedure.
7. Handoff format.
8. Quality gates.
9. Security and privacy constraints.

## 4. Portable skill format

Skills use a directory with `SKILL.md` and optional `scripts/`, `references/`, and `assets/`.

Required frontmatter:
- `name`
- `description`

The `name` must match the skill directory and use lowercase kebab-case.

Skill body should include:
- When to use.
- When not to use.
- Required inputs.
- Procedure.
- Output contract.
- Verification.
- Failure modes and escalation.

## 5. Versioning

The ecosystem and its canonical source modules use one Semantic Version. Runtime adapters declare their own versions in `ecosystem.json` because a backward-compatible host plugin may intentionally remain pinned while the shared core advances.

- Ecosystem v0.4.0: canonical contracts, shared agent instructions, skills, installers, and validators.
- Antigravity adapter v0.3.2: remains pinned to preserve the existing plugin manifest and install workflow.
- Codex, Copilot, and Claude Code adapters v0.4.0: native profiles generated from the shared source.
- PATCH: instruction corrections.
- MINOR: backward-compatible capabilities.
- MAJOR: incompatible contract or behavior changes.

## 6. Compatibility

Canonical skills should avoid host-specific tool names. Put runtime-specific invocation details in `adapters/<platform>/`.

The Antigravity plugin manifests and agent frontmatter are platform-specific by design.


## 7. Single-repository GitHub distribution contract

- `https://github.com/hd159/ai-agent` is the only canonical GitHub distribution target.
- The repository root retains the backward-compatible Antigravity plugin files.
- Nested `modules/<module-id>/` folders remain canonical source modules and are not separate plugin repositories.
- `scripts/build_single_plugin.py` deterministically generates the Antigravity bundle; use `--check` in CI to detect stale files.
- `scripts/build_adapters.py` deterministically generates native Codex, Copilot, and Claude Code project layouts.
- `scripts/install_adapter.py` safely merges native files into an existing project, records owned paths, and supports uninstall without overwriting unmanaged files.
- Team manifests are logical composition contracts; they do not install separate repositories or act as a distributed scheduler.


See [Multi-Platform Adapter Architecture](MULTI-PLATFORM-ADAPTERS.md) for native formats, installer safety, shared project memory, and runtime-specific capability boundaries.
