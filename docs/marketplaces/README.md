# One Root Bundle, Multiple Native Marketplaces

AI Agent Ecosystem uses one canonical generated bundle at the repository root. Antigravity, Claude Code, Codex core-plugins, GitHub Copilot CLI, and Cursor resolve their supported components from the same `agents/`, `skills/`, and `rules/` directories. There is no nested `plugins/` package and no duplicate component tree.

## Canonical repository layout

```text
ai-agent/
├── plugin.json                         # Antigravity root manifest (0.3.2)
├── agents/                             # 7 generated agent profiles
├── skills/                             # 19 generated skills
├── rules/
│   ├── AGENTS.md                       # shared constitution
│   └── ai-agent-constitution.mdc       # Cursor-native always-on rule
├── .claude-plugin/
│   ├── plugin.json                     # Claude Code + Copilot CLI
│   └── marketplace.json                # also discovered by Codex core-plugins
├── .codex-plugin/
│   └── plugin.json                     # Codex root plugin manifest
├── .cursor-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── modules/                            # canonical source files
└── scripts/
    └── build_single_plugin.py
```

The hidden metadata directories contain manifests only. All component paths are relative to the repository root.

## Marketplace manifest map

| Runtime | Marketplace catalog | Plugin manifest | Source |
|---|---|---|---|
| Antigravity | Root plugin discovery | `plugin.json` | Repository root |
| Claude Code | `.claude-plugin/marketplace.json` | `.claude-plugin/plugin.json` | `./` |
| Codex core-plugins | `.claude-plugin/marketplace.json` | `.codex-plugin/plugin.json` | `./` |
| GitHub Copilot CLI | Claude-format plugin metadata | `.claude-plugin/plugin.json` | Repository root |
| Cursor | `.cursor-plugin/marketplace.json` | `.cursor-plugin/plugin.json` | `./` |

### Claude Code and GitHub Copilot CLI

The Claude-format plugin manifest points to root `./agents/` and `./skills/`. The marketplace entry uses `"source": "./"`.

### Codex core-plugins

Current Codex core-plugins scans `.claude-plugin/marketplace.json` as a supported marketplace catalog and resolves a local source of `"./"` to the repository root. It also recognizes the root plugin manifest under `.codex-plugin/plugin.json`.

The root Codex manifest declares both `"agents": "./agents/"` and `"skills": "./skills/"` so the shared root contract is explicit. The current Codex core plugin manifest parser consumes the `skills` component; it does not currently map the `agents` field into custom subagent profiles. Install the native Codex agent profiles with the existing adapter when custom subagents are needed:

```powershell
python .\scripts\install_adapter.py --adapter codex --target "D:\Projects\MyProject" --dry-run
python .\scripts\install_adapter.py --adapter codex --target "D:\Projects\MyProject"
```

This installs `.codex/agents/*.toml` and project `AGENTS.md` from canonical sources; it does not create a second plugin bundle.

The repository intentionally does not keep `.agents/plugins/marketplace.json`. Codex discovers the shared Claude-format marketplace catalog directly.

### Cursor

Cursor reads `.cursor-plugin/plugin.json` and `.cursor-plugin/marketplace.json`. The marketplace source is `"./"`; the plugin manifest resolves root `./agents/`, `./skills/`, and `./rules/`.

The `rules/ai-agent-constitution.mdc` file is generated from the canonical constitution source with native MDC frontmatter and `alwaysApply: true`.

For Cursor Team Marketplace installation:

1. Open the Cursor Dashboard → **Plugins**.
2. Under **Team Marketplaces**, choose **Add Marketplace**.
3. Choose **Import from Repo** and enter `https://github.com/hd159/ai-agent`.
4. Add and review **AI Agent Ecosystem**.
5. In Cursor, open **Customize** and install the plugin.

Cursor Team Marketplace requires Teams or Enterprise.

## Build and validate

All source edits belong in `modules/`, scripts, contracts, docs, and tests. Generated root components are synchronized by the single builder:

```powershell
python .\scripts\build_single_plugin.py
python .\scripts\build_single_plugin.py --check
python .\scripts\validate_repo.py
python .\scripts\validate_plugin.py
python .\scripts\validate_agent_tools.py
python .\scripts\validate_capabilities.py
python .\scripts\validate_marketplaces.py
python -m unittest discover -s tests -v
```

The builder generates only:

- `plugin.json`
- `.codex-plugin/plugin.json`
- `agents/`
- `skills/`
- `rules/AGENTS.md`
- `rules/ai-agent-constitution.mdc`

The marketplace validator rejects:

- Any `plugins/` directory or duplicated agent/skill/rule bundle.
- Any `.agents/` marketplace catalog.
- Component directories inside `.claude-plugin/`, `.codex-plugin/`, or `.cursor-plugin/`.
- Marketplace sources that do not resolve to the repository root.
- Root generated files that differ from canonical `modules/` sources.

## Compatibility and safety

- Antigravity root `plugin.json` remains version `0.3.2`.
- Runtime plugin manifests do not grant host permissions, shell access, MCP connectivity, or delegation rights.
- The Codex `agents` manifest field documents the shared root component path; use the native Codex adapter for custom agent profiles until Codex core-plugins supports that component.
- CI validates static manifest shape and source/generated parity. Live marketplace installation smoke tests are still required in each host.

## Upstream packaging references

- [obra/superpowers](https://github.com/obra/superpowers) — root `skills/` bundle, root `.codex-plugin/plugin.json`, and Claude-format marketplace source `./`.
- [mattpocock/skills](https://github.com/mattpocock/skills) — root skill bundle and Claude-format marketplace source `./`.
- [Codex marketplace resolver](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/marketplace.rs).
- [Codex plugin manifest parser](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/manifest.rs).
