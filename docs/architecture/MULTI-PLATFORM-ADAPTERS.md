# Multi-Platform Adapter Architecture — v0.4.0

## Goal

Keep one canonical AI Agent Ecosystem repository while generating native project configuration for Antigravity, Codex, GitHub Copilot, and Claude Code. Do not maintain independent copies of agent logic or reusable skill procedures.

## Source of truth

- Agent identity, role instructions, and existing Antigravity manifests remain canonical under modules/*/agents/*.md.
- Reusable Agent Skills remain canonical under modules/*/skills/*/SKILL.md.
- The shared constitution remains canonical at modules/agent-constitution/rules/AGENTS.md.
- Project memory, task contracts, handoffs, verification records, and checkpoints remain in the target project's .agent-ecosystem/ directory.
- The Antigravity-specific 13-tool declaration is governed only by contracts/agent-tool-policy.json.

The adapter builder reads the canonical agent frontmatter, removes only the Antigravity-specific Tool access and execution section from the instruction body, and emits the native profile format. It does not copy Antigravity tool names, commandExecutionPolicy, or inheritance fields into other runtimes.

## Native output mapping

| Runtime | Always-on instructions | Specialist agents | Skills |
|---|---|---|---|
| Antigravity | Plugin rules and agent prompts | agents/*.md | skills/*/SKILL.md |
| Codex local clients (CLI, desktop app, IDE extension) | AGENTS.md | .codex/agents/*.toml | .agents/skills/*/SKILL.md |
| Copilot CLI / supported VS Code agent mode / GitHub.com custom agent assignment (no subagent delegation) | .github/copilot-instructions.md | .github/agents/*.agent.md | .github/skills/*/SKILL.md |
| Claude Code CLI | CLAUDE.md | .claude/agents/*.md | .claude/skills/*/SKILL.md |

Codex TOML uses name, description, and developer_instructions. Copilot profiles use native Markdown frontmatter with name, description, and include-custom-instructions: true so Copilot subagents load repository instructions; Claude profiles use name and description. Tool restrictions are omitted from non-Antigravity profiles so each runtime applies its own configured tool and permission policy. Copilot skills use .github/skills to keep adapter-owned skill files isolated when Codex and Copilot are both installed in the same project.

Copilot support is surface-dependent. Custom-agent and skill support does not imply subagent support on every surface; the current feature matrix does not list subagents for GitHub.com. The generated adapter targets Copilot CLI and supported VS Code agent mode.

## Build and validate

~~~powershell
python .\scripts\build_single_plugin.py
python .\scripts\build_adapters.py --adapter all
python .\scripts\validate_adapters.py
python .\scripts\validate_repo.py
python .\scripts\validate_plugin.py
python .\scripts\validate_agent_tools.py
python .\scripts\validate_capabilities.py
python -m unittest discover -s tests -v
~~~

Build output is written to dist/ and is reproducible. The adapter validator builds into a temporary directory and checks native layouts, agent inventories, skill payload parity, and Codex TOML parsing.

## Safe project installation

Use scripts/install_adapter.py with an explicit adapter and target project:

~~~powershell
python .\scripts\install_adapter.py --adapter codex --target ..\my-project --dry-run
python .\scripts\install_adapter.py --adapter codex --target ..\my-project
python .\scripts\install_adapter.py --adapter copilot --target ..\my-project
python .\scripts\install_adapter.py --adapter claude-code --target ..\my-project
~~~

The installer uses explicit managed markers in root instruction files. It records installed paths in .agent-ecosystem/adapters/<adapter>.json. On updates it replaces only registered files; unowned collisions with different content are reported and left untouched. Uninstall removes only registered files and the managed instruction block. Dry-run performs no writes.

## Shared memory and concurrency

All runtimes use the same .agent-ecosystem project-memory contracts. A runtime adapter changes only where instructions, profiles, and skills are placed; it does not fork the memory schema.

The Team Orchestrator remains the single writer of execution/state.json. Specialists return task handoffs. Parallel tasks must have disjoint owned paths or an explicit integration owner. Agents must reconcile current source, task state, decisions, and verification evidence before resuming.

## Capability and security model

- Generated profiles do not grant read/write, shell, network, MCP, image, or delegation capabilities.
- Tool names are runtime-specific and are never copied from the Antigravity 13-tool allowlist.
- Verify read, write, delete, shell, network, MCP, and delegation separately in the exact runtime, surface, workspace, and session.
- Respect sandboxing, approvals, allow/ask/deny rules, organization policies, workspace boundaries, and user authorization.
- Never claim that an agent was invoked or a file was persisted without a successful real operation.

## Compatibility and versioning

- Ecosystem release: 0.4.0.
- Antigravity plugin: remains 0.3.2 for backward compatibility.
- Codex, Copilot, and Claude Code adapter manifests: 0.4.0.
- Canonical module versions track the ecosystem release.
- The root plugin builder reads adapters.antigravity.version rather than assuming every adapter shares the ecosystem version.

## Official runtime references

- Codex: https://learn.chatgpt.com/docs/customization/overview
- Codex subagents: https://learn.chatgpt.com/docs/agent-configuration/subagents
- GitHub Copilot custom agents: https://docs.github.com/en/copilot/concepts/customizations/custom-agents
- GitHub Copilot feature matrix: https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code skills: https://code.claude.com/docs/en/skills
- Agent Skills specification: https://agentskills.io/
