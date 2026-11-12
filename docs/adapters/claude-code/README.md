# Claude Code Adapter — v0.4.0

The Claude Code adapter generates native project instructions, subagent profiles, and skills from the shared ecosystem sources.

## Generated layout

~~~text
CLAUDE.md
.claude/
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

Agent profiles use YAML frontmatter with name and description followed by the canonical role instructions. The adapter intentionally omits a tools allowlist so Claude Code applies the active runtime's configured tools and permissions.

## Install into a project

From a clone of this ecosystem repository:

~~~powershell
python .\scripts\install_adapter.py --adapter claude-code --target ..\my-project --dry-run
python .\scripts\install_adapter.py --adapter claude-code --target ..\my-project
~~~

The installer merges ecosystem instructions into CLAUDE.md using explicit managed markers, preserves user-authored content, and records installed files in .agent-ecosystem/adapters/claude-code.json. Unmanaged conflicting files are never overwritten.

Update by running the install command again. Uninstall only ecosystem-managed files and the managed instruction block with:

~~~powershell
python .\scripts\install_adapter.py --adapter claude-code --target ..\my-project --uninstall
~~~

## Runtime verification

Start a new Claude Code session in the target project. Verify CLAUDE.md and the custom agents are discovered. Invoke the capability-smoke-test skill. Test read, write, shell, MCP, and Agent delegation separately. A generated agent profile does not grant tool access or override Claude Code permission settings.

## Native references

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code memory and CLAUDE.md](https://code.claude.com/docs/en/memory)
- [Anthropic guidance: CLAUDE.md, skills, hooks, and subagents](https://claude.com/blog/steering-claude-code-skills-hooks-subagents-and-more)
