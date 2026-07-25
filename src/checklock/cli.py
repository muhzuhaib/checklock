from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .scanner import InputError, load_snapshot, load_workflows, scan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="checklock", description="Find required-check deadlocks in GitHub Actions workflows.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan_parser = subparsers.add_parser("scan", help="scan workflow files against a required-check snapshot")
    scan_parser.add_argument("--required-checks", type=Path, required=True, help="JSON required-check snapshot")
    scan_parser.add_argument("--workflows", type=Path, default=Path(".github/workflows"), help="workflow directory")
    scan_parser.add_argument("--format", choices=("human", "json"), default="human")
    return parser


def _human(findings: list[dict[str, object]]) -> str:
    if not findings:
        return "No required-check deadlock risks found."
    lines = []
    for finding in findings:
        location = finding["path"] or "snapshot"
        if finding["line"]:
            location = f"{location}:{finding['line']}"
        lines.append(f"{finding['severity'].upper()} {finding['code']} {location} — {finding['message']}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        merge_queue, checks = load_snapshot(args.required_checks)
        findings = scan(merge_queue, checks, load_workflows(args.workflows))
    except InputError as exc:
        print(f"checklock: error: {exc}")
        return 2
    rendered = [finding.to_dict() for finding in findings]
    print(json.dumps(rendered, indent=2) if args.format == "json" else _human(rendered))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
