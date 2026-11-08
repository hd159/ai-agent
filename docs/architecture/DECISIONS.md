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
