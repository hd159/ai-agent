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
- The distribution unit is the complete ecosystem: one GitHub repository and one root-level Antigravity plugin.
- `scripts/build_single_plugin.py` assembles root `plugin.json`, `agents/`, `skills/`, and `rules/` from canonical source modules.
- Generated bundle files are committed so `agy plugin install https://github.com/hd159/ai-agent` works without a local build step.

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
commandExecutionPolicy: sandbox
inheritMcp: true
inheritCustomizations: true
---
```

The body must define:
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

The complete installable plugin uses one Semantic Version. Source modules are versioned with the ecosystem release and do not publish independently.

- PATCH: instruction corrections.
- MINOR: backward-compatible capabilities.
- MAJOR: incompatible contract or behavior changes.

## 6. Compatibility

Canonical skills should avoid host-specific tool names. Put runtime-specific invocation details in `adapters/<platform>/`.

The Antigravity plugin manifests and agent frontmatter are platform-specific by design.


## 7. Single-repository GitHub distribution contract

- `https://github.com/hd159/ai-agent` is the only GitHub distribution target.
- The repository root contains the installable `plugin.json`, `agents/`, `skills/`, and `rules/` directories.
- Nested `modules/<module-id>/` folders are canonical source modules and are not separate Antigravity plugin repositories.
- `scripts/build_single_plugin.py` deterministically generates the root plugin bundle; use `--check` in CI to detect stale generated files.
- All specialist agents and shared capabilities are installed together with one `agy plugin install https://github.com/hd159/ai-agent` command.
- Team manifests are logical composition contracts; they do not install separate repositories or act as a distributed scheduler.
