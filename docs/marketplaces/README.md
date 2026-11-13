# Root-Shared Native Plugin Marketplaces

AI Agent Ecosystem 0.4.0 exposes one canonical component bundle through three native plugin marketplaces:

- Codex: `.agents/plugins/marketplace.json`
- Claude Code: `.claude-plugin/marketplace.json`
- Cursor: `.cursor-plugin/marketplace.json`

All marketplace sources point to the repository root (`./`). The manifests resolve component paths from that same root:

- Agents: `./agents/`
- Skills: `./skills/`
- Rules: `./rules/`

There is no nested `plugins/` component package and no copied agents, skills, or rules under hidden metadata directories.

## Repository layout

```text
ai-agent/
├── plugin.json                         # Antigravity 0.3.2 (unchanged)
├── agents/                             # 7 shared specialist agent profiles
├── skills/                             # 19 shared skills
├── rules/
│   ├── AGENTS.md                       # Antigravity-compatible constitution
│   └── ai-agent-constitution.mdc       # Native Cursor MDC rule
├── .agents/plugins/marketplace.json   # Codex marketplace catalog
├── .codex-plugin/plugin.json          # Codex plugin manifest
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
└── .cursor-plugin/
    ├── plugin.json
    └── marketplace.json
```

The hidden metadata directories contain manifests only:

| Directory | Allowed files |
|---|---|
| `.claude-plugin/` | `plugin.json`, `marketplace.json` |
| `.cursor-plugin/` | `plugin.json`, `marketplace.json` |
| `.codex-plugin/` | `plugin.json` |
| `.agents/plugins/` | `marketplace.json` |

The plugin manifests refer to the root bundle. Component paths are not relative to the hidden metadata directory.

## Build and validate

The single plugin builder is the only component generator. It reads canonical module sources and writes the root `agents/`, `skills/`, and `rules/` directories.

```powershell
python .\scripts\build_single_plugin.py
python .\scripts\build_single_plugin.py --check
python .\scripts\validate_plugin.py
python .\scripts\validate_marketplaces.py
python -m unittest discover -s tests -v
```

The validator fails if a nested `plugins/ai-agent/` or `plugins/ai-agent-ecosystem/` package returns, if component directories appear under hidden metadata directories, or if any manifest stops pointing to the root bundle.

## Codex

The Codex catalog is `.agents/plugins/marketplace.json`. It resolves the local plugin source to the repository root. The root `.codex-plugin/plugin.json` declares `./agents/` and `./skills/`.

In Codex's Add Plugin Marketplace dialog:

| Field | Value |
|---|---|
| Source | `https://github.com/hd159/ai-agent` |
| Git ref | `main` |
| Sparse paths | Leave empty |

For CLI use:

```bash
codex plugin marketplace add hd159/ai-agent --ref main
codex plugin marketplace list
```

Then open `/plugins` and install **AI Agent Ecosystem**.

## Claude Code

Claude Code reads plugin metadata from `.claude-plugin/plugin.json` and the marketplace catalog from `.claude-plugin/marketplace.json`. The catalog entry uses `"source": "./"`.

The plugin manifest declares the shared root component paths. Do not create `.claude-plugin/agents/`, `.claude-plugin/skills/`, or `.claude-plugin/rules/`; those paths would create a second copy and are not the component roots.

Add the GitHub repository as a Claude Code marketplace, then install **ai-agent-ecosystem** from the plugin manager.

## Cursor

Cursor reads `.cursor-plugin/plugin.json` and `.cursor-plugin/marketplace.json`. The marketplace entry uses `"source": "./"`; the plugin manifest points to the shared root `agents/`, `skills/`, and `rules/`.

For Team Marketplace installation:

1. Open the Cursor Dashboard → **Plugins**.
2. Under **Team Marketplaces**, choose **Add Marketplace**.
3. Choose **Import from Repo** and enter `https://github.com/hd159/ai-agent`.
4. Add and review **AI Agent Ecosystem**.
5. In Cursor, open **Customize** and install the plugin.

Cursor Team Marketplace requires Teams or Enterprise. For local plugin testing, use the repository root as the plugin root rather than copying component directories into a separate package.

## Antigravity compatibility

- The root Antigravity `plugin.json` remains version `0.3.2`.
- The root `agents/`, `skills/`, and `rules/AGENTS.md` continue to be generated from canonical module sources.
- `rules/ai-agent-constitution.mdc` is generated alongside the Antigravity rule for Cursor's native MDC format.
- No host permissions, tool access, MCP connectivity, or delegation rights are granted by these manifests.
- Live installation smoke tests are still required in Codex, Claude Code, and Cursor; CI validates manifest shape, root path resolution, and the no-duplication contract.
