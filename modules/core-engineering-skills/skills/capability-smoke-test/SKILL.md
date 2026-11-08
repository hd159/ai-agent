---
name: capability-smoke-test
description: >-
  Check actual Antigravity agent file-edit, terminal, MCP and skills access.
  Use to diagnose missing tools or read-only custom agents in a real session.
---

# Capability Smoke Test

Use actual tool invocations, never inferred capabilities based on metadata.
The skill does not grant host permissions and must not alter user settings.

1. Report active agent name, workspace and installed plugin version if known.
2. Create .agent-ecosystem/CAPABILITY_TEST.tmp containing 'ok' with a real
   file-edit tool; read it back; remove only that test file.
3. Invoke a real terminal tool with git status --short and Get-Location
   (Windows) or pwd (POSIX). Report tool name, exit code and result.
4. Reading this SKILL.md validates this skill, not all other skills.
5. If an MCP server is connected, invoke one authorized read-only tool.
   If no server/tool is exposed, record 'not connected' or 'not exposed',
   not a test pass.
6. If Team Orchestrator has invoke_subagent, optionally delegate a safe
   read-only task to one specialist and collect an actual handoff.
7. Repeat this test in a fresh session for each of the seven primary agents.
   One agent's success does not prove every agent can execute tools.
8. Summarize attempted, successful, denied and unavailable capabilities
   without inventing calls or changing host security preferences.
