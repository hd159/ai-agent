# Native Runtime Adapters

AI Agent Ecosystem 0.4.0 has one canonical source repository and native adapters for multiple coding-agent runtimes.

| Adapter | Native instructions | Native specialist agents | Native skills |
|---|---|---|---|
| Antigravity 0.3.2 | Plugin rules | Plugin agents | Plugin skills |
| Codex local clients 0.4.0 | AGENTS.md | .codex/agents/*.toml | .agents/skills |
| GitHub Copilot 0.4.0 | .github/copilot-instructions.md | .github/agents/*.agent.md | .github/skills |
| Claude Code 0.4.0 | CLAUDE.md | .claude/agents/*.md | .claude/skills |
| Cursor 0.4.0 | .cursor/rules/ai-agent-ecosystem.mdc | .cursor/agents/*.md | .cursor/skills |

Build all non-Antigravity bundles with python scripts/build_adapters.py --adapter all. Validate them with python scripts/validate_adapters.py. Build the dual Codex/Cursor marketplace package with python scripts/build_marketplace_components.py and validate it with python scripts/validate_marketplaces.py.

Install all native adapters into an existing project with python scripts/install_adapter.py --adapter all --target <project-path>, or select one adapter with --adapter codex, --adapter copilot, --adapter claude-code, or --adapter cursor. Run with --dry-run first. The installer preserves existing root instructions, skips conflicting unowned files, and records ownership for safe updates and uninstall. Cursor's MDC rule is a dedicated managed file (not a merged block) so its required frontmatter stays at the start.

Marketplace catalogs:
- Codex: `.agents/plugins/marketplace.json`
- Cursor: `.cursor-plugin/marketplace.json`
- Shared package: `plugins/ai-agent-ecosystem/`
- [Dual Marketplace Installation Guide](../marketplaces/README.md)

See:
- [Codex](codex/README.md)
- [GitHub Copilot](copilot/README.md)
- [Claude Code](claude-code/README.md)
- [Cursor](cursor/README.md)
- [Antigravity](antigravity/README.md)
- [Adapter architecture](../architecture/MULTI-PLATFORM-ADAPTERS.md)
