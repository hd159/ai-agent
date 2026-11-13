# Architecture Decisions

## ADR-001: One installable plugin, modular source

**Status:** Accepted

All specialist agents, skills, and shared rules are distributed from one GitHub repository as one Antigravity plugin. Source remains modular under `modules/`; `scripts/build_single_plugin.py` generates the root-level runtime bundle. This avoids repository fan-out and keeps installation to one native `agy plugin install` command.

## ADR-002: Shared skills are separate from agent identity

**Status:** Accepted

Skills remain separate portable procedures in the source modules and are bundled once into the root plugin. Agents can reference the same skill library without duplicating content.

## ADR-003: Team presets are declarative

**Status:** Accepted

A team preset selects agent roles and workflow stages. It is not a distributed scheduler and does not install remote plugin dependencies.


## ADR authoring policy: 3-Gate filter

Every candidate project ADR under `.agent-ecosystem/artifacts/` or `.agent-ecosystem/execution/decisions/` must pass all three gates before a standalone file is created:

1. **Reversibility:** Is the decision costly or difficult to reverse later?
2. **Surprise:** Is the choice non-obvious (would a future engineer wonder why this path was taken)?
3. **Trade-off:** Were there genuine competing alternatives with material trade-offs?

**Rule:** If any of the three gates is missing, skip creating a standalone ADR file and record a concise note in `PROJECT_CONTEXT.md` instead.

Capture agreed domain terms immediately in `PROJECT_CONTEXT.md` or the existing `GLOSSARY.md`; keep canonical terminology consistent across UI labels, API payloads, events, and database schemas.
