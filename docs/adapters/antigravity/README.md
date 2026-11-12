# Antigravity Adapter — v0.3.2 (backward-compatible)

Antigravity remains the existing first-party plugin adapter. Ecosystem v0.4.0 adds Codex, GitHub Copilot, and Claude Code adapters without changing the Antigravity plugin's version, manifest contract, or installation command.

## Install from GitHub

~~~powershell
agy plugin install https://github.com/hd159/ai-agent
agy plugin list
agy agents
~~~

The root plugin.json intentionally remains version 0.3.2. The shared ecosystem catalog is version 0.4.0; this is not a request to upgrade or reinterpret the Antigravity manifest.

## Team preset

The teams/saas-mvp/team.json file describes logical team membership and workflow. It does not require installing separate repositories.

~~~powershell
python .\scripts\install_team.py --team saas-mvp
~~~

## Runtime contract

All seven Antigravity agent manifests retain the explicit 13 built-in tools, commandExecutionPolicy: auto, mainAgent, subagent, MCP inheritance, and customization inheritance. See contracts/agent-tool-policy.json and docs/AGENT-DIAGNOSTICS.md.

Native delegation and file writes still depend on the active Antigravity runtime, workspace, and host permissions. Run the capability-smoke-test in the exact agent/session/workspace. Static validation does not grant permissions.

## Update and uninstall

Run the same GitHub install command again to update the plugin:

~~~powershell
agy plugin install https://github.com/hd159/ai-agent
agy plugin uninstall ai-agent
~~~
