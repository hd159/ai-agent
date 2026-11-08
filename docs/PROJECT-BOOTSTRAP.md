# Project Bootstrap

Use this guide when adding AI Agent Ecosystem to a new or existing application repository.

## 1. Prerequisites

- Antigravity installed and authenticated.
- AI Agent Ecosystem plugin installed.
- Git and Python 3.10+ if using the repository bootstrap script.
- The target application repository available locally.
- The target application's root opened as the active Antigravity workspace.

Important: installing the plugin does not clone the ai-agent source repository. The Python initialization script lives in the ai-agent Git clone.

## 2. Choose the correct path

| Project state | Action |
|---|---|
| New/empty repository, no .agent-ecosystem | Initialize once |
| Existing application, no project memory | Initialize, then run read-only discovery |
| Non-empty .agent-ecosystem exists | Resume/reconcile; do not initialize again |
| Empty .agent-ecosystem exists | Bootstrap script can populate it |
| Partial or valuable project memory exists | Preserve it and reconcile manually; do not delete it |

## 3. Option A — Initialize using Python

Clone ai-agent once to a tools/workspace folder:

~~~powershell
$workspace = "$env:USERPROFILE\Desktop\project_1"
git clone https://github.com/hd159/ai-agent.git "$workspace\ai-agent"
~~~

Initialize the target application:

~~~powershell
python "$workspace\ai-agent\scripts\init_project.py" --team saas-mvp --target "$workspace\certvault"
~~~

The script:
- Creates the target directory if missing.
- Copies the selected team preset.
- Copies PROJECT_CONTEXT.md and artifact templates.
- Creates execution/plan.json and execution/state.json.
- Creates tasks, handoffs, sessions, and decisions folders.
- Copies a session template and execution README.

The script does not scan source code, recover old architecture documents, run tests, create implementation task contracts, or dispatch agents. Those steps happen after opening the product repository in Antigravity and starting Team Orchestrator.

If the command says it cannot find scripts/init_project.py, check the current directory or use the absolute script path. Run it from the ai-agent clone, not from the product directory or the user's home directory.

## 4. Option B — Ask Team Orchestrator to initialize

Open the product repository in Antigravity and select Team Orchestrator:

~~~text
Initialize project memory in this repository.

First inspect whether .agent-ecosystem already exists.
If it contains useful files, preserve them and reconcile instead of
overwriting. If it is absent or empty, create the standard project
memory structure and copy the SaaS MVP team configuration.

Inspect the repository and fill stable project context only with facts
verified from source or existing documentation. Mark recovered facts,
assumptions, and unknowns distinctly.

Do not modify application source code. Do not dispatch implementation
tasks. Read back every created file and report what was persisted.
~~~

This path requires the selected agent to have workspace file tools and host permission to write in the active workspace.

## 5. Existing project discovery

After initialization, run a read-only onboarding:

~~~text
Perform existing-project discovery.

1. Inspect Git branch, HEAD, and working tree.
2. Read project documentation and configuration.
3. Identify frontend, backend, data, ETL, infrastructure, integrations,
   authentication, authorization, and deployment boundaries.
4. Reconcile documented claims against source code.
5. Record the current architecture and module inventory.
6. Identify risks, technical debt, unknowns, and stale documentation.
7. Recommend the next work in priority order.

Do not implement code or claim tests passed unless they were executed.
~~~

For an existing audit, import it as a historical artifact. Preserve the original score, findings, source commit, date, and rubric. Do not silently rewrite its claims or assume roadmap items are implemented.

## 6. Verify bootstrap

From the product repository:

~~~powershell
Test-Path .\.agent-ecosystem\PROJECT_CONTEXT.md
Test-Path .\.agent-ecosystem\team.json
Test-Path .\.agent-ecosystem\execution\plan.json
Test-Path .\.agent-ecosystem\execution\state.json
Get-ChildItem .\.agent-ecosystem -Force
~~~

Then ask Orchestrator to read the files back and reconcile them against the source repository.

## 7. Git and privacy

Project memory is designed to be versioned with the application repository. Commit it only if allowed by project policy. Keep secrets, access tokens, private keys, passwords, production data, and sensitive personal information out of memory files.

Do not initialize the same non-empty project memory twice. Resume and update it instead.
