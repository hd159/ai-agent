# Changelog

## 0.4.0 — Hybrid multi-runtime adapters

- Add native Codex local-client, GitHub Copilot CLI / VS Code / GitHub.com custom-agent, and Claude Code adapters generated from the existing canonical agent and skill sources.
- Preserve the Antigravity plugin at version 0.3.2, including the explicit 13-tool manifest, commandExecutionPolicy: auto, and existing install command.
- Add native agent profile generation: Codex TOML, Copilot Markdown agent profiles, and Claude Code subagents.
- Generate native instruction files and install all 19 shared skills into each runtime's supported project skill directory.
- Add safe project installer with dry-run, managed instruction blocks, conflict protection, update ownership registry, and uninstall.
- Add native adapter validation and cross-platform installer tests.
- Expand CI validation to Windows, macOS, and Linux across Python 3.10, 3.11, and 3.12.
- Keep project memory and task/handoff/verification contracts shared across runtimes.

## 0.3.2 — Explicit Antigravity runtime tool access

- Declare the exact 13 built-in Antigravity tools in all seven canonical agent manifests.
- Set commandExecutionPolicy: auto while preserving mainAgent, subagent, MCP and customization inheritance.
- Update static validators and regression tests to enforce the explicit tool contract and UTF-8-safe file reads.
- Document the live runtime finding: omitting tools on subagents yields a six-tool read-only baseline.
- Rebuild and validate the single-plugin root bundle from canonical modules.


## Unreleased — Fail-closed runtime capability preflight

- Require task-specific real tool probes before implementation, dispatch, terminal work, or project-memory writes.
- Gate dependent tasks when required capabilities are denied, not exposed, not configured, or untested; allow safe independent read-only analysis.
- Standardize capability evidence states and require re-probing in the exact agent/session/workspace after environment changes.
- Clarify that the framework detects and gates missing permissions but cannot grant or bypass host authorization.


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
