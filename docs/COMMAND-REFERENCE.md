# Command Reference

This page covers Antigravity CLI commands, native adapter build/install commands, repository validation, and natural-language agent prompts.

## 1. Antigravity plugin commands

Run from PowerShell or an Antigravity CLI terminal:

| Command | Purpose |
|---|---|
| agy plugin install https://github.com/hd159/ai-agent | Install the complete plugin |
| agy plugin list | List installed plugins |
| agy agents | List discovered agents |
| agy plugin list --json | Inspect installed plugin status, version and installation path |
| agy --agent team-orchestrator | Start Team Orchestrator as the primary CLI agent |
| agy plugin uninstall ai-agent | Uninstall the plugin |

Update by running the same install command again:

~~~powershell
agy plugin install https://github.com/hd159/ai-agent
~~~

The plugin install command does not clone the ai-agent source repository into your current directory. Clone the repository separately if you need its Python bootstrap/build/validation scripts.

## 2. Project bootstrap

From a local clone of ai-agent:

~~~powershell
python .\scripts\init_project.py --team saas-mvp --target ..\my-saas-app
~~~

Arguments:

- --team: required team preset directory under teams/. Current preset: saas-mvp.
- --target: required path to the target application repository.

The script creates .agent-ecosystem, copies the team and project/artifact templates, writes plan.json and state.json, and creates task, handoff, session, and decision folders. It copies a session template; it does not perform source-code discovery, architecture analysis, task decomposition, or agent dispatch.

Safety behavior:
- Creates the target directory if it does not exist.
- Populates an absent or empty .agent-ecosystem directory.
- Refuses to overwrite a non-empty .agent-ecosystem directory.
- Does not delete or replace existing project memory.

## 3. Plugin development and validation

Run these commands from the ai-agent repository root.

Build the installable root bundle from canonical modules:

~~~powershell
python .\scripts\build_single_plugin.py
~~~

Check that generated files are current without modifying them:

~~~powershell
python .\scripts\build_single_plugin.py --check
~~~

Validate source structure, module/team references, and schemas:

~~~powershell
python .\scripts\validate_repo.py
~~~

Validate generated plugin manifest and agent/skill metadata:

~~~powershell
python .\scripts\validate_plugin.py
~~~

Validate the Antigravity 13-tool allowlist and runtime policy:

~~~powershell
python .\scripts\validate_agent_tools.py
python .\scripts\validate_capabilities.py
~~~

Validate native Codex, Copilot, and Claude Code adapter layouts, agent profiles, and skill parity:

~~~powershell
python .\scripts\validate_adapters.py
~~~

Run all checks:

~~~powershell
python .\scripts\build_single_plugin.py --check
python .\scripts\validate_repo.py
python .\scripts\validate_plugin.py
python .\scripts\validate_agent_tools.py
python .\scripts\validate_capabilities.py
python .\scripts\build_adapters.py --adapter all
python .\scripts\validate_adapters.py
python -m unittest discover -s tests -v
~~~

Requirements: Python 3.10+.

## 4. Native runtime adapters (v0.4)

Build native Codex, Copilot, and Claude Code bundles from the canonical agent and skill sources:

~~~powershell
python .\scripts\build_adapters.py --adapter all
python .\scripts\build_adapters.py --adapter codex
python .\scripts\validate_adapters.py
~~~

Install an adapter into a target project. Run dry-run first:

~~~powershell
python .\scripts\install_adapter.py --adapter codex --target ..\my-project --dry-run
python .\scripts\install_adapter.py --adapter codex --target ..\my-project
python .\scripts\install_adapter.py --adapter copilot --target ..\my-project
python .\scripts\install_adapter.py --adapter claude-code --target ..\my-project
~~~

Update by repeating the install command. Uninstall only files recorded as managed by the adapter installer:

~~~powershell
python .\scripts\install_adapter.py --adapter codex --target ..\my-project --uninstall
~~~

The installer preserves existing root instruction content with managed markers, refuses to overwrite unmanaged conflicting agent/skill files, and records owned paths under .agent-ecosystem/adapters/. Use --dry-run to preview changes without writing.

See [Native Runtime Adapters](adapters/README.md) for runtime-specific locations and limitations.

## 5. Optional one-command installer helper

~~~powershell
python .\scripts\install_team.py --team saas-mvp --dry-run
python .\scripts\install_team.py --team saas-mvp
~~~

This validates the logical team preset and calls one Antigravity plugin install command. It does not initialize a product repository or copy project memory.

Other options:

- --url: alternative GitHub plugin URL; must be an HTTPS GitHub repository URL.
- --no-preflight: skip the git ls-remote repository reachability check.
- --dry-run: print the command without installing.

## 6. Natural-language prompts (not CLI commands)

Use Team Orchestrator in the Antigravity agent picker:

| Prompt | Purpose |
|---|---|
| Initialize this project | Discover the repository and bootstrap project context |
| Resume this project | Reconcile persistent memory and source state |
| Show project status | Report completed, active, blocked, and next tasks |
| Plan and implement this feature | Run feature workflow |
| Investigate and fix this bug | Run root-cause and regression workflow |
| Review current architecture | Request architecture delta review |
| Checkpoint this session | Persist state and session journal |

These are example prompts, not slash commands. In Antigravity App, select the primary agent via the agent selector, not the `@` menu. In the CLI, use `agy --agent team-orchestrator` or `/agents`. CLI `@` only messages an existing subagent. See [Agent Diagnostics](AGENT-DIAGNOSTICS.md).

## 7. Common Windows path mistake

If PowerShell is currently at C:\Users\ADMIN, this command will fail because scripts/init_project.py is not in that directory:

~~~powershell
python .\scripts\init_project.py
~~~

Change to the ai-agent clone first, or invoke the script with its absolute path:

~~~powershell
cd "$env:USERPROFILE\Desktop\project_1\ai-agent"
python .\scripts\init_project.py --team saas-mvp --target "$env:USERPROFILE\Desktop\project_1\certvault"
~~~

## 8. Generated-file ownership

Canonical agent source files live under modules/<module>/agents/. The root agents/ directory is generated. Skills and rules at the root are also generated. Edit canonical sources, run build_single_plugin.py, and validate the generated bundle. Do not hand-edit generated files.

## 9. Quality gate commands (v0.3)

```powershell
python -m pip install -r requirements-dev.txt

python .\scripts\quality_gate.py validate --project "C:\work\my-product"
python .\scripts\quality_gate.py task --project "C:\work\my-product" --task-id BE-001
python .\scripts\quality_gate.py release --project "C:\work\my-product"

python -m unittest discover -s tests -v
```

`validate` checks every completed task and canonical project state; `task` verifies an independent QA record for one in-review/completed task; `release` requires all tasks completed and recorded mandatory approvals. See [Quality Gates](QUALITY-GATES.md). A passing artifact check is not a substitute for independently executed CI checks or actual human approval.

## 10. Full capability checks

~~~powershell
python -m pip install -r requirements-dev.txt
python .\scripts\validate_capabilities.py
~~~

Invoke `/capability-smoke-test` in a fresh Antigravity session for each of the seven agents to check real file read/write, terminal, skill, and connected MCP operations. In Codex, Copilot, and Claude Code, run the same skill where supported and verify read, write, shell, MCP, and delegation independently. Static validation does not grant access or prove runtime execution.
