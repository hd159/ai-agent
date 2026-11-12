#!/usr/bin/env python3
"""Build native Codex, GitHub Copilot, and Claude Code adapter bundles."""
from __future__ import annotations

import argparse
from pathlib import Path

from adapter_support import ADAPTERS, ROOT, build_adapter, build_all_adapters


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", choices=("all", *ADAPTERS), default="all")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        if args.adapter == "all":
            results = build_all_adapters(ROOT, output)
        else:
            results = [build_adapter(ROOT, args.adapter, output / args.adapter)]
    except Exception as exc:
        print(f"ADAPTER BUILD FAILED: {exc}")
        return 1
    for result in results:
        print(
            f"BUILT {result['adapter']}: version={result['version']}, "
            f"agents={result['agents']}, skills={result['skills']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
