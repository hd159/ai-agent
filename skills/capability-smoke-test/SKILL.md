---
name: capability-smoke-test
description: >-
  Preflight actual Antigravity file, terminal, MCP and delegation capabilities
  before implementation; diagnose missing or denied tools without guessing.
---

# Runtime Capability Preflight

Run this before dispatching or starting any task that needs workspace writes,
terminal execution, external services, or agent delegation. Re-run when the
workspace, agent, session, or permission context changes.

## 1. Derive the task capability contract

Translate the requested work into required operations, not assumed tool names:

- read_workspace: inspect existing files and project state
- write_workspace: create or modify project files
- delete_workspace: remove files (only when explicitly in scope)
- terminal: run commands, tests, builds, git and package managers
- network: access required external endpoints
- mcp:<server>/<operation>: use a named connected MCP capability
- delegate: invoke a specialist/subagent
- persist_state: write project memory, task contracts and checkpoints

Mark each as required or optional and explain why. Never require a capability
that the task does not need. Treat destructive operations separately.

## 2. Probe actual runtime capabilities

Use the actual host tools available in this session. Do not infer availability
from YAML, plugin metadata, model choice, another agent's session, or docs.

- Read: inspect a known project file.
- Write: create .agent-ecosystem/CAPABILITY_TEST.tmp with 'ok', read it back,
  then delete only that exact test file. Do not overwrite an existing file.
- Terminal: run Get-Location and git status --short on Windows, or pwd
  and git status --short on POSIX.
- MCP: invoke one harmless authorized read-only operation for each MCP server
  required by this task. If none is required, mark not_required.
- Delegation: only test if the plan requires a specialist; confirm a real
  invocation and handoff, not just agent discoverability.

If the workspace directory or .agent-ecosystem does not exist, do not create
project structure solely for this probe unless a real write tool is available
and the task authorizes creating it. Never use a destructive probe.

## 3. Record evidence with precise states

For every capability, record one of:

- available_verified: real invocation succeeded
- exposed_but_denied: tool exists and host returned a permission/approval denial
- not_exposed: no matching tool is present in this runtime
- not_configured: required MCP/server/credential integration is absent
- not_required: task does not need this capability
- not_tested: no real probe was possible

Include the actual tool name (if exposed), operation, result/error text,
workspace scope, and timestamp where available. Never convert not_tested into
available, or infer write access from successful reads.

## 4. Gate execution before dispatch

- If a required capability is not available_verified, do not dispatch or
  start the dependent implementation task.
- Continue independent read-only analysis when safe; mark implementation
  blocked with a machine-readable blocker listing the exact capability,
  observed state, and remediation.
- Ask the user to enable/approve the relevant host permission, connect the
  required MCP server, open the correct workspace, or select a runtime that
  exposes the capability. Give exact UI/CLI guidance only when known.
- Re-run only the failed probe after the user changes the environment.
- Do not attempt to bypass allow/ask/deny rules, sandboxing, workspace
  boundaries, or approval prompts.

## 5. Keep task requirements and results durable

Add required capabilities to the task contract's inputs/verification or
capability_requirements field only if the schema supports it; otherwise record
them in the task description and handoff without inventing schema fields.
Persist the preflight result and blocker in the project execution state when
write access is verified. If persistence is unavailable, explicitly say that
no project state was written.

## 6. Report honestly

Separate: declared capability, tool exposed, operation attempted, host
authorization, and successful outcome. A proposed command is not an executed
command. A generated code block is not a file write. A tool error is evidence,
not a reason to claim the task completed.

## 7. Agent/session coverage

A successful probe applies only to the current agent, session, workspace and
permission context. Repeat for each specialist in a fresh session when that
specialist will perform writes or terminal operations. Do not infer one
agent's access from another agent's success.
