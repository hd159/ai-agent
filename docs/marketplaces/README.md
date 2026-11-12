# Dual Native Plugin Marketplaces

AI Agent Ecosystem 0.4.0 now publishes one GitHub repository through two separate native marketplace catalogs:

- Codex: `.agents/plugins/marketplace.json`
- Cursor: `.cursor-plugin/marketplace.json`

Both catalogs install the same package directory, `plugins/ai-agent-ecosystem/`, which contains platform-specific manifests and shared skill payloads. This keeps the Antigravity root `plugin.json` untouched.

## Package layout

```text
ai-agent/
├── .agents/plugins/marketplace.json
├── .cursor-plugin/marketplace.json
└── plugins/ai-agent-ecosystem/
    ├── .codex-plugin/plugin.json
    ├── .cursor-plugin/plugin.json
    ├── agents/                 # Cursor custom agents (7)
    ├── rules/                  # Cursor MDC rule (alwaysApply)
    └── skills/                 # Shared portable skills (19)
```

The package is generated from `modules/*/agents/*.md`, `modules/*/skills/*/SKILL.md`, and the shared constitution. Run:

```powershell
python .\scripts\build_marketplace_components.py
python .\scripts\build_marketplace_components.py --check
python .\scripts\validate_marketplaces.py
```

The builder owns only generated files under `plugins/ai-agent-ecosystem/agents`, `rules`, `skills`, and its ownership marker. It refuses to replace an unmanaged directory or delete unowned files.

## Install in Codex

### Codex desktop / Plugins Directory

In the Add plugin marketplace dialog, use:

| Field | Value |
|---|---|
| Source | `https://github.com/hd159/ai-agent` |
| Git ref | `main` |
| Sparse paths | **Leave empty** |

Do not set Sparse paths to `plugins/ai-agent-ecosystem`. The marketplace catalog is at the repository-level path `.agents/plugins/marketplace.json`; the catalog itself points to the nested plugin package using a Git subdirectory source.

After adding the marketplace, open the Plugins Directory, select **AI Agent Ecosystem**, and install the plugin.

### Codex CLI

```bash
codex plugin marketplace add hd159/ai-agent --ref main
codex plugin marketplace list
```

Open the Codex plugin browser with `/plugins`, find **AI Agent Ecosystem**, and install it. Use the documented marketplace upgrade command to refresh the source:

```bash
codex plugin marketplace upgrade ai-agent-ecosystem
```

### Codex capability boundary

The Codex plugin package exposes the 19 reusable skills. The current Codex plugin manifest contract does not provide Cursor-style `agents` or `rules` component declarations. Therefore installing the Codex marketplace plugin does **not** automatically install the seven Codex custom-agent TOML profiles or the project's `AGENTS.md`.

To install the complete Codex native project adapter as well:

```powershell
python .\scripts\install_adapter.py --adapter codex --target "D:\Projects\MyProject" --dry-run
python .\scripts\install_adapter.py --adapter codex --target "D:\Projects\MyProject"
```

This is additive: the marketplace plugin provides reusable skills; the native adapter provides project instructions and `.codex/agents/*.toml`.

## Install in Cursor

### Team marketplace

Cursor Team and Enterprise support team marketplaces. To import this repository:

1. Open the Cursor Dashboard and go to **Plugins**.
2. Under **Team Marketplaces**, choose **Add Marketplace**.
3. Choose **Import from Repo** and enter `https://github.com/hd159/ai-agent`.
4. Add and review **AI Agent Ecosystem** in the marketplace.
5. Configure marketplace access and installation mode.
6. In Cursor, open **Customize**, find the plugin, and select **Install**.

The Cursor marketplace catalog is `.cursor-plugin/marketplace.json`. Its entry points to `plugins/ai-agent-ecosystem/`, whose `.cursor-plugin/plugin.json` declares the seven agents, shared rule, and skills.

### Local development / individual use

For local plugin testing, Cursor documents `~/.cursor/plugins/local`. On Windows, one approach is:

```powershell
git clone https://github.com/hd159/ai-agent.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.cursor\plugins\local" | Out-Null
Copy-Item -Recurse ".\ai-agent\plugins\ai-agent-ecosystem" "$env:USERPROFILE\.cursor\plugins\local\ai-agent-ecosystem"
```

Restart Cursor or run **Developer: Reload Window**, then open **Customize** and verify the plugin's agents, rules, and skills. Local plugin imports may be restricted by organization policy.

Public Cursor Marketplace listing is a separate submission/review process; a repository marketplace manifest does not automatically publish the plugin to Cursor's public directory.

## Compatibility and security

- Antigravity remains on plugin version 0.3.2; the root `plugin.json` is unchanged.
- Ecosystem and native plugin packages remain at version 0.4.0.
- Codex receives the shared skills only through its supported plugin package surface.
- Cursor receives 7 specialist agents, 1 always-applied MDC rule, and 19 skills.
- Neither plugin manifest grants shell, filesystem, network, MCP, delegation, or approval permissions.
- Host permissions and approval policies remain controlled by each application.
- Marketplace manifests and generated package content are validated in CI. Live installation still needs a smoke test in each host application.

## Official format references

- [Codex plugin packaging and marketplace metadata](https://developers.openai.com/plugins/build/plugins)
- [Cursor plugins and marketplaces](https://cursor.com/docs/plugins)
- [Cursor plugin manifest reference](https://prod.cursor.com/docs/reference/plugins)
