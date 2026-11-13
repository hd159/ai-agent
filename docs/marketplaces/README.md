# Root-Shared Native Plugin Marketplaces

AI Agent Ecosystem 0.4.0 exposes one canonical root bundle to Claude Code and Cursor, plus the smallest Codex-specific package required by Codex's marketplace path rules.

Marketplaces:

- Codex: `.agents/plugins/marketplace.json`
- Claude Code: `.claude-plugin/marketplace.json`
- Cursor: `.cursor-plugin/marketplace.json`

## Repository layout

```text
ai-agent/
├── plugin.json                         # Antigravity 0.3.2
├── agents/                             # 7 canonical root agents
├── skills/                             # 19 canonical root skills
├── rules/
│   ├── AGENTS.md                       # Antigravity-compatible constitution
│   └── ai-agent-constitution.mdc       # Native Cursor MDC rule
├── .claude-plugin/                     # metadata only
│   ├── plugin.json
│   └── marketplace.json
├── .cursor-plugin/                     # metadata only
│   ├── plugin.json
│   └── marketplace.json
├── .agents/plugins/marketplace.json   # Codex catalog
└── plugins/ai-agent/                   # Codex-required subdirectory only
    ├── .codex-plugin/plugin.json
    └── skills/                         # Codex-required mirror of root skills
```

Claude Code and Cursor manifests resolve `./agents/`, `./skills/`, and `./rules/` from the repository root. Their hidden metadata directories contain only the two manifests.

### Why the Codex exception exists

Codex repo marketplaces require a local plugin source in a strict subdirectory such as `./plugins/ai-agent`; the current resolver rejects `.` and `./` as the repository root. In addition, the Codex plugin manifest defines a `skills` component, not `agents` or `rules`.

Therefore:

- `plugins/ai-agent/` is retained because Codex path validation requires it.
- It contains only `.codex-plugin/plugin.json` and the required `skills/` mirror.
- No agent or rule files are duplicated into the Codex package.
- Codex specialist agents are installed separately as native `.codex/agents/*.toml` through the existing project adapter.
- No component directories are ever copied into `.claude-plugin/` or `.cursor-plugin/`.

## Build and validate

`build_single_plugin.py` is the only component builder. It reads canonical module sources, builds the root Antigravity/Claude/Cursor bundle, and creates the minimal Codex skills package from the root skills.

```powershell
python .\scripts\build_single_plugin.py
python .\scripts\build_single_plugin.py --check
python .\scripts\validate_plugin.py
python .\scripts\validate_marketplaces.py
python -m unittest discover -s tests -v
```

The validators fail if:

- Any component directory appears under `.claude-plugin/` or `.cursor-plugin/`.
- A nested `plugins/ai-agent-ecosystem/` package returns.
- `plugins/ai-agent/` contains agents or rules, or its skills diverge from the root skills.
- A Claude/Cursor manifest stops resolving components from the root.
- The Codex marketplace points to the repository root instead of `./plugins/ai-agent`.

## Claude Code

Claude Code reads `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. The marketplace entry uses `"source": "./"`. Component paths in the plugin manifest resolve from the repository root:

- `agents: "./agents/"`
- `skills: "./skills/"`
- `rules: "./rules/"`

Do not create `.claude-plugin/agents/`, `.claude-plugin/skills/`, or `.claude-plugin/rules/`.

Add `https://github.com/hd159/ai-agent` as a Claude Code marketplace, then install **ai-agent-ecosystem** from the plugin manager.

## Cursor

Cursor reads `.cursor-plugin/plugin.json` and `.cursor-plugin/marketplace.json`. The marketplace entry uses `"source": "./"`; the plugin manifest points directly to the root `agents/`, `skills/`, and `rules/`.

For Team Marketplace installation:

1. Open the Cursor Dashboard → **Plugins**.
2. Under **Team Marketplaces**, choose **Add Marketplace**.
3. Choose **Import from Repo** and enter `https://github.com/hd159/ai-agent`.
4. Add and review **AI Agent Ecosystem**.
5. In Cursor, open **Customize** and install the plugin.

Cursor Team Marketplace requires Teams or Enterprise.

## Codex

The Codex marketplace catalog is `.agents/plugins/marketplace.json`. It points to `./plugins/ai-agent`, because Codex does not accept a repository-root local plugin source.

The Codex package manifest is `plugins/ai-agent/.codex-plugin/plugin.json`. It declares `skills: "./skills/"` and contains only the 19 skills mirrored from the root bundle.

In Codex's Add Plugin Marketplace dialog:

| Field | Value |
|---|---|
| Source | `https://github.com/hd159/ai-agent` |
| Git ref | `main` |
| Sparse paths | Leave empty |

CLI:

```bash
codex plugin marketplace add hd159/ai-agent --ref main
codex plugin marketplace list
```

Then open `/plugins` and install **ai-agent**.

Codex plugin manifests do not declare custom agent or rule directories. Install the specialist agent profiles and project instructions with the native adapter:

```powershell
python .\scripts\install_adapter.py --adapter codex --target "D:\Projects\MyProject" --dry-run
python .\scripts\install_adapter.py --adapter codex --target "D:\Projects\MyProject"
```

This installs `.codex/agents/*.toml` and `AGENTS.md` without pretending those are plugin components.

## Antigravity compatibility

- The root Antigravity `plugin.json` remains version `0.3.2`.
- Root `agents/`, `skills/`, and `rules/AGENTS.md` continue to be generated from canonical module sources.
- `rules/ai-agent-constitution.mdc` is generated alongside the Antigravity rule for Cursor.
- The Codex skills mirror is the only generated component duplicate and exists solely because of Codex marketplace path validation.
- Manifests do not grant host permissions, tool access, MCP connectivity, or delegation rights.
- CI validates manifest paths, package inventory, root-source equality, and duplication boundaries. Live installation smoke tests are still required in all three runtimes.

## Format references

- [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Codex marketplace path resolution](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/marketplace.rs)
- [Claude Code plugins](https://docs.anthropic.com/en/docs/claude-code/plugins)
- [Cursor plugins](https://cursor.com/docs/plugins)
