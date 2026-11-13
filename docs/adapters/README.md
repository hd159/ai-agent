# Native Runtime Adapters

AI Agent Ecosystem 0.4.0 has one canonical source repository, one generated root bundle, and native adapters for multiple coding-agent runtimes.

| Adapter | Native instructions | Native specialist agents | Native skills |
|---|---|---|---|
| Antigravity 0.3.2 | Plugin rules | Plugin agents | Plugin skills |
| Codex local clients 0.4.0 | AGENTS.md | .codex/agents/*.toml | .agents/skills |
| GitHub Copilot 0.4.0 | .github/copilot-instructions.md | .github/agents/*.agent.md | .github/skills |
| Claude Code 0.4.0 | CLAUDE.md | .claude/agents/*.md | .claude/skills |
| Cursor 0.4.0 | .cursor/rules/ai-agent-ecosystem.mdc | .cursor/agents/*.md | .cursor/skills |

Build all non-Antigravity bundles with `python scripts/build_adapters.py --adapter all`. Validate them with `python scripts/validate_adapters.py`. Build the shared root plugin bundle with `python scripts/build_single_plugin.py` and validate marketplace metadata with `python scripts/validate_marketplaces.py`.

Install all native adapters into an existing project with `python scripts/install_adapter.py --adapter all --target <project-path>`, or select one adapter with `--adapter codex`, `--adapter copilot`, `--adapter claude-code`, or `--adapter cursor`. Run with `--dry-run` first. The installer preserves existing root instructions, skips conflicting unowned files, and records ownership for safe updates and uninstall. Cursor's MDC rule is a dedicated managed file (not a merged block) so its required frontmatter stays at the start.

## Marketplace manifests

All marketplace catalogs resolve the canonical root bundle using `"source": "./"`:

- Claude Code: `.claude-plugin/marketplace.json`
- Codex core-plugins: reuses `.claude-plugin/marketplace.json` and root `.codex-plugin/plugin.json`
- GitHub Copilot CLI: reuses `.claude-plugin/plugin.json`
- Cursor: `.cursor-plugin/marketplace.json`
- Antigravity: root `plugin.json`

There is no `plugins/` package mirror and no `.agents/plugins/marketplace.json`. The Codex root manifest declares `./agents/` and `./skills/`; current Codex core-plugins consumes the skill path, while native custom agent profiles are provided by the Codex adapter.

See the [Root-Shared Native Plugin Marketplaces](../marketplaces/README.md) guide for details.

## Runtime adapter guides

- [Codex](codex/README.md)
- [GitHub Copilot](copilot/README.md)
- [Claude Code](claude-code/README.md)
- [Cursor](cursor/README.md)
- [Antigravity](antigravity/README.md)
- [Adapter architecture](../architecture/MULTI-PLATFORM-ADAPTERS.md)
