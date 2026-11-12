# GitHub Copilot Adapter — v0.4.0

The Copilot adapter generates repository instructions, custom agent profiles, and reusable Agent Skills for GitHub Copilot CLI and supported IDE agent modes.

## Generated layout

~~~text
.github/
  copilot-instructions.md
  agents/
    architecture-agent.agent.md
    backend-agent.agent.md
    frontend-agent.agent.md
    infrastructure-agent.agent.md
    qa-agent.agent.md
    team-orchestrator.agent.md
    uiux-design-agent.agent.md
  skills/
    <skill-name>/
      SKILL.md
~~~

The agent profiles use native Markdown frontmatter with name, description, and include-custom-instructions: true so Copilot subagents receive repository custom instructions. Tool restrictions are intentionally omitted: the active Copilot surface controls which tools are available. Skills use .github/skills, GitHub Copilot's native project-level location. This keeps adapter-owned files isolated when multiple runtimes are installed in one project.

## Install into a project

From a clone of this ecosystem repository:

~~~powershell
python .\scripts\install_adapter.py --adapter copilot --target ..\my-project --dry-run
python .\scripts\install_adapter.py --adapter copilot --target ..\my-project
~~~

The installer merges ecosystem instructions into .github/copilot-instructions.md inside explicit managed markers. It preserves existing content, does not overwrite unmanaged conflicting agent or skill files, and records ownership in .agent-ecosystem/adapters/copilot.json.

Update by running the install command again. Uninstall only ecosystem-managed files and the managed instruction block with:

~~~powershell
python .\scripts\install_adapter.py --adapter copilot --target ..\my-project --uninstall
~~~

## Surface compatibility

Custom agents and Agent Skills are available on supported Copilot surfaces, but feature parity is not universal. The current GitHub feature matrix distinguishes VS Code and Copilot CLI from GitHub.com: GitHub.com supports custom agents and skills but does not list subagent execution. The generated profile is therefore not proof that delegation is available. Verify the exact IDE/CLI surface, version, organization policy, and runtime permissions before dispatch.

## Runtime verification

Start a new Copilot CLI or supported IDE agent session. Confirm repository instructions, custom agents, and skills are discovered. Run capability-smoke-test where available. Verify read, write, shell, MCP, and subagent operations independently. Never infer tool availability from the profile file.

## Native references

- [Copilot custom agents](https://docs.github.com/en/copilot/concepts/customizations/custom-agents)
- [Copilot customization feature matrix](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)
- [Copilot Agent Skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [Copilot CLI custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents)
