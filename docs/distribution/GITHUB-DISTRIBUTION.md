# Single-repository GitHub distribution

## Distribution contract

`hd159/ai-agent` is the only GitHub repository and the only installable Antigravity plugin. Its root contains `module.json`, `agents/`, `skills/`, and `rules/`. The nested `modules/<module-id>/` folders are canonical source modules, not separate distribution repositories.

Install or update the complete ecosystem:

```powershell
agy plugin install https://github.com/hd159/ai-agent
```

Uninstall:

```powershell
agy plugin uninstall ai-agent
```

## Build and validate

```powershell
python .\scripts\build_single_plugin.py
python .\scripts\validate_repo.py
python .\scripts\validate_plugin.py
python .\scripts\build_single_plugin.py --check
```

The bundle builder copies every specialist agent, every skill, and shared constitution rules to the root plugin structure. It rejects duplicate agent or skill names. Generated root directories must be committed with their source modules so Antigravity can install the repository directly.

## Team installation helper

```powershell
python .\scripts\install_team.py --team saas-mvp
```

The helper validates the selected logical team preset and installs the one repository exactly once. The team preset does not map to separate GitHub repositories.

## Release boundary

- One repository: `https://github.com/hd159/ai-agent`.
- One Antigravity plugin ID: `ai-agent`.
- Seven specialist agents, 16 skills, and shared rules bundled together.
- No per-agent GitHub repositories, no repo fan-out, and no local plugin-folder copy step.
