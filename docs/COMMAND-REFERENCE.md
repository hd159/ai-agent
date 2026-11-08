# Command Reference

This page distinguishes Antigravity CLI commands, repository maintenance scripts, and natural-language agent prompts.

## 1. Antigravity plugin commands

Run from PowerShell or an Antigravity CLI terminal:

| Command | Purpose |
|---|---|
| agy plugin install https://github.com/hd159/ai-agent | Install the complete plugin |
| agy plugin list | List installed plugins |
| agy agents | List discovered agents |
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

Validate full built-in tool access, MCP inheritance, host-managed execution policy, and source/generated parity:

~~~powershell
python .\scripts\validate_agent_tools.py
~~~

Run all checks:

~~~powershell
python .\scripts\build_single_plugin.py --check
python .\scripts\validate_repo.py
python .\scripts\validate_plugin.py
python .\scripts\validate_agent_tools.py
~~~

Requirements: Python 3.10+.

## 4. Optional one-command installer helper

~~~powershell
python .\scripts\install_team.py --team saas-mvp --dry-run
python .\scripts\install_team.py --team saas-mvp
~~~

This validates the logical team preset and calls one Antigravity plugin install command. It does not initialize a product repository or copy project memory.

Other options:

- --url: alternative GitHub plugin URL; must be an HTTPS GitHub repository URL.
- --no-preflight: skip the git ls-remote repository reachability check.
- --dry-run: print the command without installing.

## 5. Natural-language prompts (not CLI commands)

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

These are examples, not slash commands. Use the agent picker or supported @agent syntax to address a custom agent.

## 6. Common Windows path mistake

If PowerShell is currently at C:\Users\ADMIN, this command will fail because scripts/init_project.py is not in that directory:

~~~powershell
python .\scripts\init_project.py
~~~

Change to the ai-agent clone first, or invoke the script with its absolute path:

~~~powershell
cd "$env:USERPROFILE\Desktop\project_1\ai-agent"
python .\scripts\init_project.py --team saas-mvp --target "$env:USERPROFILE\Desktop\project_1\certvault"
~~~

## 7. Generated-file ownership

Canonical agent source files live under modules/<module>/agents/. The root agents/ directory is generated. Skills and rules at the root are also generated. Edit canonical sources, run build_single_plugin.py, and validate the generated bundle. Do not hand-edit generated files.

## 8. Quality gate commands (v0.3)

\`\`\`powershell
python -m pip install -r requirements-dev.txt

python .\scripts\quality_gate.py validate --project "C:\work\my-product"
python .\scripts\quality_gate.py task --project "C:\work\my-product" --task-id BE-001
python .\scripts\quality_gate.py release --project "C:\work\my-product"

python -m unittest discover -s tests -v
\`\`\`

\`validate\` checks every completed task and canonical project state; \`task\` verifies an independent QA record for one in-review/completed task; \`release\` requires all tasks completed and recorded mandatory approvals. See [Quality Gates](QUALITY-GATES.md). A passing artifact check is not a substitute for independently executed CI checks or actual human approval.
