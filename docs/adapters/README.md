# Native Runtime Adapters

AI Agent Ecosystem 0.4.0 has one canonical source repository and native adapters for multiple coding-agent runtimes.

| Adapter | Native instructions | Native specialist agents | Native skills |
|---|---|---|---|
| Antigravity 0.3.2 | Plugin rules | Plugin agents | Plugin skills |
| Codex local clients 0.4.0 | AGENTS.md | .codex/agents/*.toml | .agents/skills |
| GitHub Copilot 0.4.0 | .github/copilot-instructions.md | .github/agents/*.agent.md | .github/skills |
| Claude Code 0.4.0 | CLAUDE.md | .claude/agents/*.md | .claude/skills |

Build all non-Antigravity bundles with python scripts/build_adapters.py --adapter all. Validate them with python scripts/validate_adapters.py.

Install an adapter into an existing project with python scripts/install_adapter.py --adapter codex, copilot, or claude-code --target <project-path>. Run with --dry-run first. The installer preserves existing root instructions, skips conflicting unowned files, and records ownership for safe updates and uninstall.

See:
- [Codex](codex/README.md)
- [GitHub Copilot](copilot/README.md)
- [Claude Code](claude-code/README.md)
- [Antigravity](antigravity/README.md)
- [Adapter architecture](../architecture/MULTI-PLATFORM-ADAPTERS.md)
