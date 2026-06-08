from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import __version__
from .doctor import doctor_repository
from .handoff import collect_handoff_data, write_handoff
from .initializer import init_context_files
from .packer import create_context_pack
from .scanner import format_scan_text, scan_repository
from .syncer import TARGET_PATHS, sync_context
from .utils import resolve_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentctx",
        description="Audit, generate, sync, and package repository context files for AI coding agents.",
    )
    parser.add_argument("--version", action="version", version=f"agentctx {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Audit repository AI context files.")
    scan_parser.add_argument("--root", default=None, help="Repository root to scan. Defaults to current directory.")
    scan_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    scan_parser.add_argument("--fail-under", type=int, default=None, metavar="SCORE", help="Return non-zero if the context score is below SCORE.")
    scan_parser.set_defaults(func=cmd_scan)

    init_parser = subparsers.add_parser("init", help="Generate starter context files.")
    init_parser.add_argument("--root", default=None, help="Repository root. Defaults to current directory.")
    init_parser.add_argument("--all", action="store_true", help="Also create CLAUDE.md, GEMINI.md, Copilot, and Cursor files.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    init_parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing files.")
    init_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    init_parser.set_defaults(func=cmd_init)

    sync_parser = subparsers.add_parser("sync", help="Sync AGENTS.md into tool-specific context files.")
    sync_parser.add_argument("--root", default=None, help="Repository root. Defaults to current directory.")
    sync_parser.add_argument("--from", dest="source", default="AGENTS.md", help="Source context file. Defaults to AGENTS.md.")
    sync_parser.add_argument(
        "--to",
        dest="targets",
        action="append",
        choices=sorted(TARGET_PATHS.keys()),
        help="Target to sync. Can be used multiple times. Defaults to all targets.",
    )
    sync_parser.add_argument("--dry-run", action="store_true", help="Show files that would change without writing.")
    sync_parser.add_argument("--check", action="store_true", help="Return non-zero if generated files are out of sync.")
    sync_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    sync_parser.set_defaults(func=cmd_sync)

    handoff_parser = subparsers.add_parser("handoff", help="Generate a handoff summary from local repository state.")
    handoff_parser.add_argument("--root", default=None, help="Repository root. Defaults to current directory.")
    handoff_parser.add_argument("--output", default="HANDOFF.md", help="Output file. Defaults to HANDOFF.md.")
    handoff_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of writing a file.")
    handoff_parser.set_defaults(func=cmd_handoff)

    pack_parser = subparsers.add_parser("pack", help="Generate PROJECT_CONTEXT.md for an AI coding session.")
    pack_parser.add_argument("--root", default=None, help="Repository root. Defaults to current directory.")
    pack_parser.add_argument("--output", default="PROJECT_CONTEXT.md", help="Output file. Defaults to PROJECT_CONTEXT.md.")
    pack_parser.set_defaults(func=cmd_pack)

    doctor_parser = subparsers.add_parser("doctor", help="Plan or apply safe automatic context repairs.")
    doctor_parser.add_argument("--root", default=None, help="Repository root. Defaults to current directory.")
    doctor_parser.add_argument("--fix", action="store_true", help="Apply safe repairs instead of only showing the plan.")
    doctor_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    doctor_parser.set_defaults(func=cmd_doctor)

    return parser


def cmd_scan(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    result = scan_repository(root)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(format_scan_text(result))
    if args.fail_under is not None and result.score < args.fail_under:
        return 1
    return 1 if any(problem.level == "error" for problem in result.problems) else 0


def cmd_init(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    result = init_context_files(root, include_all=args.all, force=args.force, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.dry_run:
        _print_list("Would create", result["would_create"])
        _print_list("Skipped", result["skipped"])
    else:
        _print_list("Created", result["created"])
        _print_list("Overwritten", result["overwritten"])
        _print_list("Skipped", result["skipped"])
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    try:
        result = sync_context(
            root,
            source=args.source,
            targets=args.targets,
            dry_run=args.dry_run,
            check=args.check,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if args.check:
            if result["out_of_sync"]:
                _print_list("Out of sync", result["out_of_sync"])
            _print_list("Already synced", result["already_synced"])
        elif args.dry_run:
            _print_list("Would update", result["would_update"])
            _print_list("Already synced", result["already_synced"])
        else:
            _print_list("Created", result["created"])
            _print_list("Updated", result["updated"])
            _print_list("Already synced", result["already_synced"])
    return 1 if args.check and result["out_of_sync"] else 0


def cmd_handoff(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    if args.json:
        data = collect_handoff_data(root)
        print(json.dumps(data.to_dict(), indent=2, ensure_ascii=False))
        return 0
    data = write_handoff(root, output=args.output)
    print(f"Wrote {args.output} for {data.repository}.")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    path = create_context_pack(root, output=args.output)
    print(f"Wrote {path.name}.")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    result = doctor_repository(root, fix=args.fix)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if not result["remaining_problems"] else 1
    if args.fix:
        print(f"Score: {result['score_before']}/100 -> {result['score_after']}/100")
        _print_list("Applied", result["applied_actions"])
    else:
        print(f"Score: {result['score_before']}/100")
        _print_list("Planned safe repairs", result["planned_actions"])
        if not result["planned_actions"]:
            print("No safe automatic repairs needed.")
    return 0 if not result["remaining_problems"] else 1


def _print_list(title: str, values: List[str]) -> None:
    if not values:
        return
    print(f"{title}:")
    for value in values:
        print(f"  - {value}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
