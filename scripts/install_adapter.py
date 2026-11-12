#!/usr/bin/env python3
"""Safely install or uninstall one or all native adapters in a project workspace."""
from __future__ import annotations

import argparse
from pathlib import Path

from adapter_support import ADAPTERS, install_adapter


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True, choices=("all", *ADAPTERS))
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="Target project directory")
    parser.add_argument("--dry-run", action="store_true", help="Show the install plan without writing files")
    parser.add_argument("--uninstall", action="store_true", help="Remove only files recorded as installer-managed")
    args = parser.parse_args()

    selected = list(ADAPTERS) if args.adapter == "all" else [args.adapter]
    if args.uninstall:
        selected.reverse()

    results = []
    for adapter in selected:
        try:
            result = install_adapter(
                adapter=adapter,
                target=args.target,
                dry_run=args.dry_run,
                uninstall=args.uninstall,
            )
        except Exception as exc:
            print(f"[{adapter}] ADAPTER OPERATION FAILED: {exc}")
            return 1
        results.append(result)
        print(f"[{adapter}]")
        for key in ("installed", "updated", "unchanged", "removed", "conflicts"):
            values = result.get(key, [])
            if values:
                print(f"  {key.upper()}:")
                for value in values:
                    print(f"   - {value}")
        if result.get("message"):
            print(f"  {result['message']}")
        if result.get("registry"):
            print(f"  REGISTRY: {result['registry']}")

    conflicts = [item for result in results for item in result.get("conflicts", [])]
    if args.dry_run:
        print("DRY RUN: no project files were changed")
    if conflicts:
        print("Some files were left untouched. Resolve conflicts and rerun.")
        return 2
    print("ALL REQUESTED ADAPTERS UNINSTALLED" if args.uninstall else "ALL REQUESTED ADAPTERS INSTALLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
