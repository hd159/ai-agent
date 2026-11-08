# Changelog

## 0.2.0 — Single-repository distribution

- Consolidated all seven specialist agents, 16 shared skills, and constitution rules into one root-level Antigravity plugin bundle.
- Made `https://github.com/hd159/ai-agent` the only GitHub distribution and installation target.
- Added a deterministic bundle builder that assembles root `plugin.json`, `agents/`, `skills/`, and `rules/` from canonical specialist modules.
- Simplified team installation to one `agy plugin install` command; no separate plugin repositories or manual folder copying are required.
- Updated team, architecture, and distribution documentation to describe a single repository and logical team composition.
- Removed the multi-repository export and publishing pipeline.

## 0.1.0 — Foundation

- Established specialist agent modules for Architecture, UI/UX, Frontend, Backend, Infrastructure, QA, and Team Orchestrator.
- Added shared Agent Skills and a global agent constitution.
- Added SaaS MVP team composition, task/handoff contracts, project templates, and repository validation tooling.
