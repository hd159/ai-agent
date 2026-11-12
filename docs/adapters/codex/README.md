# Codex Adapter — v0.4.0

The Codex adapter generates native project-scoped configuration for local Codex clients that discover project AGENTS.md, .codex/agents/, and .agents/skills/ (CLI, desktop app, and IDE extension). Verify the exact client version and workspace discovery behavior after installation.

## Generated layout

~~~text
AGENTS.md
.codex/
  agents/
    architecture-agent.toml
    backend-agent.toml
    frontend-agent.toml
    infrastructure-agent.toml
    qa-agent.toml
    team-orchestrator.toml
    uiux-design-agent.toml
.agents/
  skills/
    <skill-name>/
      SKILL.md
~~~

Each custom agent TOML contains the native required fields: name, description, and developer_instructions. The adapter does not copy Antigravity frontmatter or its 13-tool allowlist into Codex. Codex controls the tools and permissions available to each session.

## Install into a project

From a clone of this ecosystem repository:

~~~powershell
python .\scripts\install_adapter.py --adapter codex --target ..\my-project --dry-run
python .\scripts\install_adapter.py --adapter codex --target ..\my-project
~~~

The installer:
- Adds the ecosystem instructions to AGENTS.md inside explicit managed markers.
- Installs the seven custom agents and all reusable skills.
- Preserves existing user-authored AGENTS.md content.
- Never overwrites an unmanaged agent or skill file with different content.
- Records owned files in .agent-ecosystem/adapters/codex.json.

Update by running the install command again. Remove only ecosystem-managed files and instruction blocks with:

~~~powershell
python .\scripts\install_adapter.py --adapter codex --target ..\my-project --uninstall
~~~

## Runtime verification

Start a new Codex CLI session in the target project. Confirm that AGENTS.md is loaded, inspect the available custom agents, and run the capability-smoke-test skill. Test read, write, shell, MCP, and delegation independently. A generated TOML profile does not enable a permission or guarantee that a subagent can be spawned.

Current local Codex releases expose subagent workflows in the desktop app, CLI, and IDE extension. Custom project agents are loaded from .codex/agents/. Verify the exact client version and permissions in the active session.

## Native references

- [Codex customization overview](https://learn.chatgpt.com/docs/customization/overview)
- [Codex custom subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex AGENTS.md prompting guidance](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
