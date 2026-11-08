# Antigravity Adapter

Antigravity is the first supported runtime. The complete ecosystem is shipped as one installable plugin.

## Install from GitHub

```powershell
agy plugin install https://github.com/hd159/ai-agent
agy plugin list
agy agents
```

This single install includes the Team Orchestrator, Architecture, UI/UX, Frontend, Backend, Infrastructure, and QA agents, all 16 skills, and shared constitution rules.

## Team preset

The `teams/saas-mvp/team.json` file describes logical team membership and workflow. It does not require installing separate repositories. To run the convenience helper from a clone of this repository:

```powershell
python .\scripts\install_team.py --team saas-mvp
```

## Update and uninstall

Run the same GitHub install command again to update the bundle:

```powershell
agy plugin install https://github.com/hd159/ai-agent
agy plugin uninstall ai-agent
```

## Runtime caveat

Native subagent delegation depends on the installed Antigravity runtime and permissions. The Team Orchestrator includes a fallback that creates task contracts when native delegation is unavailable.
