#!/usr/bin/env python3
"""Install the complete AI Agent Ecosystem from its single GitHub repository."""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://github.com/hd159/ai-agent"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team", default="saas-mvp", help="Team preset to activate/document (default: saas-mvp)")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"GitHub plugin repository URL (default: {DEFAULT_URL})")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without executing it")
    parser.add_argument("--no-preflight", action="store_true", help="Skip git ls-remote availability check")
    args = parser.parse_args()

    team_path = ROOT / "teams" / args.team / "team.json"
    if not team_path.is_file():
        print(f"ERROR: team preset not found: {team_path}")
        return 2
    team = json.loads(team_path.read_text(encoding="utf-8"))
    if not args.url.startswith("https://github.com/"):
        print("ERROR: --url must be an https://github.com/<owner>/<repo> URL")
        return 2

    agy = shutil.which("agy")
    git = shutil.which("git")
    if not agy and not args.dry_run:
        print("ERROR: 'agy' CLI not found. Install and authenticate Antigravity CLI first.")
        return 2
    if not args.no_preflight and not args.dry_run:
        if not git:
            print("ERROR: 'git' is required for repository preflight. Install Git or pass --no-preflight.")
            return 2
        result = subprocess.run([git, "ls-remote", "--exit-code", args.url, "HEAD"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: GitHub repository is not reachable or has no HEAD: {args.url}")
            if result.stderr.strip(): print(result.stderr.strip())
            return 3

    command = [agy or "agy", "plugin", "install", args.url]
    print("Installing the complete AI Agent Ecosystem as ONE Antigravity plugin.")
    print(f"Team preset: {team['name']} ({args.team})")
    print(f"Included agents: {len(team.get('members', [])) + 1} (including Team Orchestrator)")
    print(f"Repository: {args.url}")
    print("> " + subprocess.list2cmdline(command))
    if args.dry_run:
        print("Dry run complete. No plugin was installed.")
        return 0

    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print("ERROR: Antigravity plugin installation failed.")
        return result.returncode
    subprocess.run([agy, "plugin", "list"], check=False)
    print("\nInstalled one plugin containing all specialist agents, shared skills, and rules.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
