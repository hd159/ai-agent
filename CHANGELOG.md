# Changelog

## 0.3.1 — Agent capability auditing and runtime diagnostics

- Verified all seven bundled agents retain unrestricted built-in tool exposure, MCP inheritance, customizations inheritance, and main/subagent selection.
- Added a strict static capability validator covering YAML, bundled skills, shared rules, manifest and source/generated parity.
- Added the capability-smoke-test skill for real file, terminal, skill and connected MCP checks in each Antigravity session.
- Added capability regression tests and CI validation; clarified App agent selection and troubleshooting.
- Preserved user-owned host permission controls; no runtime access claim is made from static validation alone.


## 0.3.0 — Executable quality gates

- Added schema-validated project state, task, plan, team, handoff and independent verification records.
- Added fail-closed task completion and release readiness CLI with Git source-freshness checks.
- Added independent QA evidence mapping and human-approval record validation.
- Added negative regression tests for false completion, stale evidence, missing logs and release gates.
- Updated Orchestrator, QA and verification skills, project bootstrap, CI and user documentation.
- Retained full agent tool access and user-owned execution permissions.
- Release checks validate declared evidence but do not authenticate user approvals or substitute for protected CI.


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
