#!/usr/bin/env python3
"""Shared, dependency-free builders and safe installer for native agent adapters."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ("codex", "copilot", "claude-code")
BEGIN_MARKER = "<!-- BEGIN AI AGENT ECOSYSTEM MANAGED INSTRUCTIONS -->"
END_MARKER = "<!-- END AI AGENT ECOSYSTEM MANAGED INSTRUCTIONS -->"

LAYOUTS = {
    "codex": {"instructions": "AGENTS.md", "agents": ".codex/agents", "skills": ".agents/skills", "extension": ".toml"},
    "copilot": {"instructions": ".github/copilot-instructions.md", "agents": ".github/agents", "skills": ".github/skills", "extension": ".agent.md"},
    "claude-code": {"instructions": "CLAUDE.md", "agents": ".claude/agents", "skills": ".claude/skills", "extension": ".md"},
}

RUNTIME_NOTES = {
    "codex": (
        "## Runtime execution and delegation\n"
        "- Use Codex native subagent spawning only when the current Codex session exposes it.\n"
        "- Give each delegated task one owner, bounded paths, explicit acceptance criteria, and a handoff contract.\n"
        "- Do not invent tool names or claim a subagent was invoked without a real invocation.\n"
        "- Agent profiles do not grant filesystem, shell, network, MCP, or approval permissions.\n"
    ),
    "copilot": (
        "## Runtime execution and delegation\n"
        "- Custom-agent and subagent support varies by Copilot surface and version. Probe the current surface before relying on delegation.\n"
        "- Copilot CLI and supported IDE agent modes may delegate; GitHub.com surfaces do not all expose subagent execution.\n"
        "- Do not invent tool names or claim a subagent was invoked without a real invocation.\n"
        "- Agent profiles do not grant filesystem, shell, network, MCP, or approval permissions.\n"
    ),
    "claude-code": (
        "## Runtime execution and delegation\n"
        "- Use Claude Code's native Agent mechanism only when it is exposed and authorized in the current session.\n"
        "- Give each delegated task one owner, bounded paths, explicit acceptance criteria, and a handoff contract.\n"
        "- Do not invent tool names or claim a subagent was invoked without a real invocation.\n"
        "- Agent profiles do not grant filesystem, shell, network, MCP, or approval permissions.\n"
    ),
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_agent(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError(f"{path}: unterminated YAML frontmatter")

    lines = text[4:end].splitlines()
    name = ""
    description = ""
    for index, line in enumerate(lines):
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip("\"'")
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            if value in (">-", ">", "|", "|-"):
                parts = []
                for continuation in lines[index + 1:]:
                    if continuation and not continuation[0].isspace():
                        break
                    if continuation.strip():
                        parts.append(continuation.strip())
                description = " ".join(parts)
            else:
                description = value.strip("\"'")
            break

    if not name or not description:
        raise ValueError(f"{path}: name and description are required")
    body = text[end + 4:].lstrip("\r\n")
    body = _strip_antigravity_runtime_section(body)
    if not body.strip():
        raise ValueError(f"{path}: agent instructions are empty after adapter normalization")
    return name, description, body.rstrip() + "\n"


def _strip_antigravity_runtime_section(body: str) -> str:
    """Remove only the Antigravity-specific tool declaration explanation."""
    output = []
    skipping = False
    for line in body.splitlines():
        if line.strip() == "## Tool access and execution":
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            output.append(line)
    return "\n".join(output).strip() + "\n"


def _agent_sources(root: Path) -> list[tuple[str, str, str, str]]:
    policy = _read_json(root / "contracts/agent-tool-policy.json")
    expected = set(policy.get("agents", []))
    result = []
    for path in sorted((root / "modules").glob("*/agents/*.md")):
        name, description, body = _parse_agent(path)
        if name != path.stem:
            raise ValueError(f"{path}: frontmatter name does not match filename")
        result.append((name, description, body, path.as_posix()))
    found = {item[0] for item in result}
    if found != expected:
        raise ValueError(
            f"Agent inventory mismatch: missing={sorted(expected - found)}, "
            f"unexpected={sorted(found - expected)}"
        )
    return result


def _skill_sources(root: Path) -> list[Path]:
    paths = sorted((root / "modules").glob("*/skills/*/SKILL.md"))
    names = [path.parent.name for path in paths]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate skill directory names across canonical modules")
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Missing skill file: {path}")
    return paths


def _common_instructions(root: Path, adapter: str) -> str:
    rule_path = root / "modules/agent-constitution/rules/AGENTS.md"
    if not rule_path.is_file():
        raise FileNotFoundError(f"Missing canonical constitution: {rule_path}")
    constitution = rule_path.read_text(encoding="utf-8").strip()
    skill_root = LAYOUTS[adapter]["skills"]
    return (
        f"# AI Agent Ecosystem — {adapter}\n\n"
        "<!-- Generated from hd159/ai-agent. Edit canonical source, then rebuild. -->\n\n"
        f"{constitution}\n\n"
        "## Persistent project memory\n\n"
        "- When the target project contains .agent-ecosystem/, read PROJECT_CONTEXT.md, team.json, "
        "execution/state.json, execution/plan.json, relevant task contracts, unresolved handoffs, "
        "and the newest relevant session checkpoint before resuming work.\n"
        "- Treat current source and reproducible checks as implementation evidence. Reconcile conflicts "
        "between source, approved architecture/ADRs, task contracts, and execution state explicitly.\n"
        "- The Team Orchestrator is the single writer of shared execution/state.json; specialists return "
        "handoffs instead of concurrently overwriting the shared snapshot.\n"
        "- Do not create project memory or claim persistence unless the user requested initialization or "
        "the task requires it and real write access has been verified.\n"
        "- Never store credentials, access tokens, private keys, or secrets in project memory.\n\n"
        "## Skills and capability preflight\n\n"
        f"- Discover reusable procedures under {skill_root}/ and load only the relevant SKILL.md files.\n"
        "- Before implementation, dispatch, shell execution, network access, MCP use, or persistence, "
        "derive the task's required capabilities and verify each using real operations in this session.\n"
        "- Use the capability-smoke-test skill when available. Distinguish available, denied, not exposed, "
        "not configured, not required, and not tested. A read success does not prove write or shell access.\n"
        "- If a required capability is not verified, block only the dependent work, continue safe independent "
        "analysis, and report the exact missing capability and remediation. Never bypass host security or approvals.\n\n"
        "## Delegation and completion\n\n"
        "- Use native runtime delegation only after confirming the current session exposes and authorizes it. "
        "Never simulate a subagent run or infer delegation from an installed profile.\n"
        "- If delegation is unavailable, the orchestrator may execute bounded work itself only when its own "
        "required capabilities are verified and the work is within the user's approved project scope. Otherwise "
        "mark the dependent task blocked. Do not silently substitute planning-only artifacts for requested implementation.\n"
        "- Keep one accountable owner per task, declare dependencies and owned paths, and avoid concurrent edits "
        "to shared files. Verify acceptance criteria with actual tests or checks before reporting completion.\n"
        "- Preserve user changes and existing project instructions. Ask before destructive, production-impacting, "
        "or out-of-scope actions.\n"
    )


def _render_agent(adapter: str, name: str, description: str, body: str) -> str:
    instructions = body.rstrip() + "\n\n" + RUNTIME_NOTES[adapter]
    if adapter == "codex":
        return (
            f'name = {json.dumps(name, ensure_ascii=False)}\n'
            f'description = {json.dumps(description, ensure_ascii=False)}\n'
            f'developer_instructions = {json.dumps(instructions, ensure_ascii=False)}\n'
        )
    copilot_custom_instructions = "include-custom-instructions: true\n" if adapter == "copilot" else ""
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        f"{copilot_custom_instructions}"
        "---\n\n"
        f"{instructions}"
    )


def build_adapter(root: Path, adapter: str, destination: Path) -> dict:
    if adapter not in ADAPTERS:
        raise ValueError(f"Unsupported adapter '{adapter}'. Choose from: {', '.join(ADAPTERS)}")
    if destination.is_symlink():
        raise ValueError(f"Refusing to replace a symlink build destination: {destination}")
    if destination.exists():
        if not destination.is_dir():
            raise ValueError(f"Build destination is not a directory: {destination}")
        existing_files = list(destination.iterdir())
        if existing_files:
            existing_manifest = destination / "adapter.json"
            if not existing_manifest.is_file():
                raise ValueError(f"Refusing to replace an unmanaged build directory: {destination}")
            if _read_json(existing_manifest).get("adapter") != adapter:
                raise ValueError(f"Build directory belongs to another adapter: {destination}")
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    catalog = _read_json(root / "ecosystem.json")
    adapter_info = catalog.get("adapters", {}).get(adapter)
    if not isinstance(adapter_info, dict) or not adapter_info.get("version"):
        raise ValueError(f"ecosystem.json is missing adapters.{adapter}.version")

    layout = LAYOUTS[adapter]
    instructions_path = destination / layout["instructions"]
    instructions_path.parent.mkdir(parents=True, exist_ok=True)
    instructions_path.write_text(_common_instructions(root, adapter), encoding="utf-8", newline="\n")

    agents = _agent_sources(root)
    agent_dir = destination / layout["agents"]
    agent_dir.mkdir(parents=True, exist_ok=True)
    for name, description, body, _source in agents:
        target = agent_dir / f"{name}{layout['extension']}"
        target.write_text(_render_agent(adapter, name, description, body), encoding="utf-8", newline="\n")

    skills = _skill_sources(root)
    skill_dir = destination / layout["skills"]
    skill_dir.mkdir(parents=True, exist_ok=True)
    for skill_file in skills:
        target = skill_dir / skill_file.parent.name
        shutil.copytree(skill_file.parent, target)

    manifest = {
        "schema_version": "1.0.0",
        "ecosystem_version": catalog["version"],
        "adapter": adapter,
        "adapter_version": adapter_info["version"],
        "instructions_file": layout["instructions"],
        "agent_directory": layout["agents"],
        "skill_directory": layout["skills"],
        "agents": [item[0] for item in agents],
        "skills": [path.parent.name for path in skills],
        "tool_policy": "Runtime-native tools and host permissions are not granted by generated profiles.",
    }
    (destination / "adapter.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    return {"adapter": adapter, "agents": len(agents), "skills": len(skills), "version": adapter_info["version"]}


def build_all_adapters(root: Path, output_root: Path) -> list[dict]:
    output_root.mkdir(parents=True, exist_ok=True)
    return [build_adapter(root, adapter, output_root / adapter) for adapter in ADAPTERS]


def _managed_block(incoming: str, newline: str) -> str:
    normalized = incoming.replace("\r\n", "\n").replace("\n", newline)
    body = normalized.strip("\r\n")
    return f"{BEGIN_MARKER}{newline}{body}{newline}{END_MARKER}"


def _merge_managed_block(
    existing: str,
    incoming: str,
    prefix_newline_added: bool | None = None,
) -> tuple[str, bool]:
    newline = "\r\n" if "\r\n" in existing else "\n"
    block = _managed_block(incoming, newline)
    has_begin = BEGIN_MARKER in existing
    has_end = END_MARKER in existing
    if has_begin != has_end:
        raise ValueError("Existing managed instruction file has an incomplete ownership marker pair")
    if has_begin:
        start = existing.index(BEGIN_MARKER)
        end = existing.index(END_MARKER, start) + len(END_MARKER)
        return existing[:start] + block + existing[end:], bool(prefix_newline_added)
    if existing:
        added = not existing.endswith(("\n", "\r"))
        separator = newline if added else ""
        return existing + separator + block + newline, added
    return block + newline, False


def _remove_managed_block(
    existing: str,
    prefix_newline_added: bool = False,
) -> tuple[str, bool]:
    has_begin = BEGIN_MARKER in existing
    has_end = END_MARKER in existing
    if not has_begin and not has_end:
        return existing, False
    if has_begin != has_end:
        raise ValueError("Existing managed instruction file has an incomplete ownership marker pair")
    newline = "\r\n" if "\r\n" in existing else "\n"
    start = existing.index(BEGIN_MARKER)
    end = existing.index(END_MARKER, start) + len(END_MARKER)
    prefix = existing[:start]
    suffix = existing[end:]
    if suffix == newline:
        suffix = ""
    if prefix_newline_added and prefix.endswith(newline):
        prefix = prefix[:-len(newline)]
    return prefix + suffix, True


def _is_managed_relative(adapter: str, relative: str) -> bool:
    layout = LAYOUTS[adapter]
    return (
        relative == layout["instructions"]
        or relative.startswith(layout["agents"].rstrip("/") + "/")
        or relative.startswith(layout["skills"].rstrip("/") + "/")
    )


def _safe_target(target: Path, relative: str) -> Path:
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts or "\\" in relative or "\x00" in relative:
        raise ValueError(f"Unsafe generated path: {relative}")
    if rel.parts and ":" in rel.parts[0]:
        raise ValueError(f"Unsafe generated path: {relative}")
    candidate = target.joinpath(*rel.parts)
    cursor = target
    for index, part in enumerate(rel.parts):
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"Generated path contains a symlink: {relative}")
        if index < len(rel.parts) - 1 and cursor.exists() and not cursor.is_dir():
            raise ValueError(f"Generated path parent is not a directory: {relative}")
    resolved = candidate.resolve(strict=False)
    if resolved != target and target not in resolved.parents:
        raise ValueError(f"Generated path escapes target through a symlink: {relative}")
    return candidate


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _cleanup_empty_parents(path: Path, stop: Path) -> None:
    parent = path.parent
    while parent != stop and stop in parent.parents and parent.exists():
        try:
            parent.rmdir()
        except OSError:
            break
        parent = parent.parent


def install_adapter(
    adapter: str,
    target: Path,
    root: Path = ROOT,
    dry_run: bool = False,
    uninstall: bool = False,
) -> dict:
    if adapter not in ADAPTERS:
        raise ValueError(f"Unsupported adapter '{adapter}'. Choose from: {', '.join(ADAPTERS)}")
    target = target.resolve()
    if target.exists() and not target.is_dir():
        raise ValueError(f"Target project path is not a directory: {target}")
    if not target.exists() and not dry_run and not uninstall:
        target.mkdir(parents=True, exist_ok=True)
    registry = _safe_target(target, f".agent-ecosystem/adapters/{adapter}.json")

    if uninstall:
        if not registry.is_file():
            return {"adapter": adapter, "removed": [], "conflicts": [], "message": "No installer registry found"}
        if registry.is_symlink():
            raise ValueError("Installer registry is a symlink; refusing to follow it")
        previous = _read_json(registry)
        if previous.get("adapter") != adapter:
            raise ValueError("Installer registry adapter identity mismatch")
        removed = []
        conflicts = []
        for relative in previous.get("managed_files", []):
            if not _is_managed_relative(adapter, relative):
                conflicts.append(f"{relative}: registry path is outside adapter-owned locations; left untouched")
                continue
            path = _safe_target(target, relative)
            if not path.exists():
                continue
            if path.is_symlink():
                conflicts.append(f"{relative}: symlink detected; left untouched")
                continue
            if relative == previous.get("instructions_file"):
                try:
                    updated, changed = _remove_managed_block(
                        path.read_bytes().decode("utf-8"),
                        bool(previous.get("instruction_prefix_newline_added", False)),
                    )
                except ValueError as exc:
                    conflicts.append(f"{relative}: {exc}")
                    continue
                if changed:
                    if not dry_run:
                        _write_text(path, updated)
                    removed.append(relative + " (managed block)")
                else:
                    conflicts.append(f"{relative}: ownership markers missing; left untouched")
            else:
                if not path.is_file():
                    conflicts.append(f"{relative}: managed path is no longer a regular file; left untouched")
                    continue
                if not dry_run:
                    path.unlink()
                removed.append(relative)
                if not dry_run:
                    _cleanup_empty_parents(path, target)
        if not dry_run and not conflicts:
            registry.unlink(missing_ok=True)
            _cleanup_empty_parents(registry, target)
        return {"adapter": adapter, "removed": removed, "conflicts": conflicts}

    if registry.is_symlink():
        raise ValueError("Installer registry is a symlink; refusing to follow it")
    with tempfile.TemporaryDirectory(prefix=f"ai-agent-{adapter}-") as temporary:
        bundle = Path(temporary) / adapter
        build_adapter(root, adapter, bundle)
        old_registry = _read_json(registry) if registry.is_file() else {}
        if old_registry and old_registry.get("adapter") != adapter:
            raise ValueError("Installer registry adapter identity mismatch")
        old_files = set(old_registry.get("managed_files", []))
        instruction_file = LAYOUTS[adapter]["instructions"]
        instruction_prefix_newline_added = False
        managed_files = []
        installed = []
        updated = []
        unchanged = []
        conflicts = []

        source_files = sorted(path for path in bundle.rglob("*") if path.is_file() and path.name != "adapter.json")
        current_relatives = {path.relative_to(bundle).as_posix() for path in source_files}
        # Preflight every parent path before the first write so a malformed project
        # directory cannot leave a partially installed, unregistered adapter.
        for relative in current_relatives:
            _safe_target(target, relative)

        for source in source_files:
            relative = source.relative_to(bundle).as_posix()
            destination = _safe_target(target, relative)
            if destination.is_symlink():
                conflicts.append(f"{relative}: symlink detected; left untouched")
                continue
            if relative == instruction_file:
                if destination.exists() and not destination.is_file():
                    conflicts.append(f"{relative}: destination exists and is not a regular file; left untouched")
                    continue
                existing = destination.read_bytes().decode("utf-8") if destination.is_file() else ""
                try:
                    merged, instruction_prefix_newline_added = _merge_managed_block(
                        existing,
                        source.read_text(encoding="utf-8"),
                        old_registry.get("instruction_prefix_newline_added"),
                    )
                except ValueError as exc:
                    conflicts.append(f"{relative}: {exc}")
                    continue
                existed_before = destination.is_file()
                if merged == existing:
                    unchanged.append(relative)
                else:
                    if not dry_run:
                        _write_text(destination, merged)
                    (updated if existed_before else installed).append(relative)
                managed_files.append(relative)
                continue

            new_bytes = source.read_bytes()
            if destination.exists():
                if relative in old_files:
                    if not destination.is_file():
                        conflicts.append(f"{relative}: managed path is no longer a regular file; left untouched")
                        continue
                    if destination.read_bytes() == new_bytes:
                        unchanged.append(relative)
                    else:
                        if not dry_run:
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source, destination)
                        updated.append(relative)
                    managed_files.append(relative)
                elif destination.is_file() and destination.read_bytes() == new_bytes:
                    unchanged.append(relative)
                    managed_files.append(relative)
                else:
                    conflicts.append(f"{relative}: exists and is not managed by this installer; left untouched")
            else:
                if not dry_run:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                installed.append(relative)
                managed_files.append(relative)

        stale = old_files - current_relatives
        for relative in sorted(stale):
            if not _is_managed_relative(adapter, relative):
                conflicts.append(f"{relative}: stale registry path is outside adapter-owned locations; left untouched")
                continue
            path = _safe_target(target, relative)
            if not path.exists():
                continue
            if path.is_symlink():
                conflicts.append(f"{relative}: symlink detected; left untouched")
                continue
            if relative == old_registry.get("instructions_file"):
                try:
                    updated_text, changed = _remove_managed_block(
                        path.read_bytes().decode("utf-8"),
                        bool(old_registry.get("instruction_prefix_newline_added", False)),
                    )
                except ValueError as exc:
                    conflicts.append(f"{relative}: {exc}")
                    continue
                if changed and not dry_run:
                    _write_text(path, updated_text)
            else:
                if not dry_run:
                    path.unlink()
                    _cleanup_empty_parents(path, target)

        if not dry_run:
            registry.parent.mkdir(parents=True, exist_ok=True)
            registry_data = {
                "schema_version": "1.0.0",
                "adapter": adapter,
                "adapter_version": _read_json(bundle / "adapter.json")["adapter_version"],
                "instructions_file": instruction_file,
                "instruction_prefix_newline_added": instruction_prefix_newline_added,
                "managed_files": sorted(managed_files),
            }
            _write_text(registry, json.dumps(registry_data, indent=2) + "\n")

        return {
            "adapter": adapter,
            "installed": installed,
            "updated": updated,
            "unchanged": unchanged,
            "conflicts": conflicts,
            "registry": registry.relative_to(target).as_posix(),
            "dry_run": dry_run,
        }
