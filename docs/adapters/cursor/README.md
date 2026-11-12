# Cursor Adapter — v0.4.0

The Cursor adapter generates native Cursor project rules, custom subagents, and Agent Skills from the canonical AI Agent Ecosystem sources.

## Generated layout

~~~text
.cursor/
  rules/
    ai-agent-ecosystem.mdc
  agents/
    architecture-agent.md
    backend-agent.md
    frontend-agent.md
    infrastructure-agent.md
    qa-agent.md
    team-orchestrator.md
    uiux-design-agent.md
  skills/
    <skill-name>/
      SKILL.md
~~~

The project rule uses native MDC frontmatter:

~~~yaml
---
description: Shared AI Agent Ecosystem instructions for this project
alwaysApply: true
---
~~~

Each custom subagent uses Markdown YAML frontmatter with `name` and `description`, followed by the canonical role instructions. All 19 shared skills are installed into `.cursor/skills/`, Cursor's native project skill directory.

## Install into a project

From a clone of this ecosystem repository:

~~~powershell
python .\scripts\install_adapter.py --adapter cursor --target ..\my-project --dry-run
python .\scripts\install_adapter.py --adapter cursor --target ..\my-project
~~~

Install all four non-Antigravity adapters together:

~~~powershell
python .\scripts\install_adapter.py --adapter all --target ..\my-project --dry-run
python .\scripts\install_adapter.py --adapter all --target ..\my-project
~~~

The installer treats `ai-agent-ecosystem.mdc` as a dedicated, exclusively managed rule file. MDC frontmatter must remain at the start of the file, so it is not merged into a user-authored rule. If that exact path already exists and is not registered to this installer, it is left untouched and reported as a conflict. Put your own rules in separate `.mdc` files.

Update by running the install command again. Uninstall only ecosystem-managed files with:

~~~powershell
python .\scripts\install_adapter.py --adapter cursor --target ..\my-project --uninstall
~~~

The installer preserves other Cursor rules, agents, skills, and project files.

## Runtime behavior

Cursor supports subagents in the Editor, CLI, and Cloud Agents. The seven generated profiles are discovered from `.cursor/agents/` and can be invoked by name (for example, `/team-orchestrator`) or selected by the parent agent for delegation.

Subagents start with a clean context. The parent must include the relevant task background, constraints, owned paths, acceptance criteria, and decisions in the delegation prompt. Do not assume that the subagent has the parent's conversation history.

Cursor Agent Skills are available from `.cursor/skills/` and can be invoked by slash command or attached as context. The adapter keeps this directory separate from Codex, Copilot, and Claude installer-owned skill locations so all runtimes can coexist in one project.

## Runtime verification

Open the target project in Cursor and start a fresh Agent session. Confirm:
1. `ai-agent-ecosystem.mdc` appears as an always-applied project rule.
2. The seven custom agents are discoverable under `.cursor/agents/`.
3. The 19 skills are discoverable under `.cursor/skills/`.
4. The `capability-smoke-test` skill verifies read, write, shell, MCP, and delegation separately.

Generated profiles do not grant tool access or bypass Cursor's permissions, sandboxing, approval prompts, or organization policies. Static validation is not proof of live runtime execution.

## Native references

- [Cursor project rules](https://cursor.com/docs/rules)
- [Cursor custom subagents](https://cursor.com/docs/subagents)
- [Cursor Agent Skills](https://cursor.com/help/customization/skills)
- [Cursor CLI](https://cursor.com/docs/cli)
