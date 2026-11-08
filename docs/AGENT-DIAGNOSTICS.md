# Agent discovery and runtime diagnostics

These checks distinguish two separate issues: App agent lookup and unavailable write/terminal tools.

## 1. `@team-orchestrator` shows `No matching results`

In the **Antigravity App**, `@` searches files, folders, rules and conversations. It is NOT the primary custom-agent selector. Subagents do not appear in the App `@` menu. Use the **agent selector**, or open **Customizations > Installed > ai-agent > Agents**.

In the **Antigravity CLI**, choose a primary agent with `agy --agent team-orchestrator` or with `/agents`. CLI `@` can message an already-existing subagent, not select a new primary agent.

Official reference: https://antigravity.google/docs/at-mentions

## 2. Check plugin loading

Run these in PowerShell:

~~~powershell
agy plugin list --json
agy agents
~~~

Confirm that `ai-agent` is installed/enabled and that `team-orchestrator` appears among available agents. If absent, check the plugin details and reinstall:

~~~powershell
agy plugin install https://github.com/hd159/ai-agent
agy plugin list --json
agy agents
~~~

Restart/reload Antigravity and start a **new conversation** after reinstalling; an existing conversation may retain its previous agent configuration.

To check a local clone's plugin packaging (not runtime tool activation):

~~~powershell
agy plugin validate --strict C:\Users\ADMIN\Desktop\project_1\ai-agent
~~~

## 3. Smoke-test actual tools

Open the product repository as a local workspace, start a **new** conversation with Team Orchestrator, and send:

~~~text
Capability smoke test. Do not modify application source code.
1. Use an actual file-edit tool to create .agent-ecosystem/CAPABILITY_TEST.tmp containing 'ok'.
2. Use an actual file-read tool to read its contents back.
3. Use an actual terminal tool to run Get-Location and git status --short.
4. Delete only CAPABILITY_TEST.tmp.
5. Report each tool actually invoked and its result or exact host error.
Do not replace execution with a proposed script or a code block.
~~~

A claim that the tool is unavailable without an attempted action is not conclusive. Do not assume that selecting Turbo grants tools excluded by the agent runtime.

Repeat the same smoke test in a new session with the **default built-in agent**, using exactly the same workspace and permission settings.

## 4. Interpret the result

| Observation | Likely scope | Next check |
|---|---|---|
| App `@` has no matching agent | Expected App mention behavior | Use the agent selector, not `@` |
| `agy agents` does not list the plugin agent | Plugin discovery, disabled plugin or stale installation | `agy plugin list --json`, plugin Agents tab, reinstall/reload |
| Built-in agent writes but plugin agent cannot | Plugin agent or session toolset | Inspect installed agent frontmatter and tool call logs |
| Neither built-in nor plugin agent writes | Host permissions or workspace access | Confirm local workspace and project/global permissions |
| CLI works but App does not | App session or plugin activation | Start a new App conversation and inspect App plugin details |
| Write/terminal tool exists but is denied | Actual host policy | Review permission prompt, sandbox or workspace rules |

## 5. Tool metadata is not a runtime test

This plugin intentionally omits the `tools` frontmatter field. The Antigravity **Build plugins** documentation says bundled agents without a `tools` list receive all built-in tools; the separate **Custom subagents** reference lists a different default for its subagent interface. A read-only session may indicate a surface-specific difference, old loaded definition, or other host limitation. Do not claim a definite root cause until the runtime tools and installed plugin copy are inspected.

References: https://antigravity.google/docs/build-plugins and https://antigravity.google/docs/subagents

The user controls allow/ask/deny, sandbox, workspace access, and other host execution permissions. Those settings do not alter which tools were exposed to the session.

## 6. Diagnostics to collect

- Output of `agy plugin list --json` and `agy agents` (redact personal paths).
- Whether `team-orchestrator` is selectable in the App.
- Whether the built-in agent passes the same smoke test.
- The first exact file-edit/terminal tool call or denial, if present.
- The Antigravity App/CLI version and local-vs-remote workspace type.

Never include tokens, passwords or other secrets in diagnostic outputs.
