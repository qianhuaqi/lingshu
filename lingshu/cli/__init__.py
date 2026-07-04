"""LingShu command-line interface."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from lingshu._version import get_version
from lingshu.cli.commands import check, run
from lingshu.cli.core import ExitCode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lingshu")
    parser.add_argument(
        "--version",
        action="store_true",
        dest="show_version",
        help="show the installed LingShu version and exit",
    )

    subparsers = parser.add_subparsers(dest="command", help="available commands")

    # version
    subparsers.add_parser("version", help="show version and exit")

    # check
    check_parser = subparsers.add_parser("check", help="validate an application")
    check_parser.add_argument("target", help="target application (module:attribute)")
    check_parser.add_argument(
        "--factory",
        action="store_true",
        help="treat target as a factory function",
    )

    # run
    run_parser = subparsers.add_parser("run", help="run an application")
    run_parser.add_argument("target", help="target application (module:attribute)")
    run_parser.add_argument(
        "--factory",
        action="store_true",
        help="treat target as a factory function",
    )
    run_parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="number of worker processes (default: 1)",
    )
    run_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="bind host (default: 127.0.0.1)",
    )
    run_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="bind port (default: 8000)",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = _build_parser()
    namespace = parser.parse_args(argv)

    if namespace.show_version or namespace.command == "version":
        print(f"lingshu {get_version()}")
        return ExitCode.SUCCESS

    if namespace.command == "check":
        return check(namespace.target, namespace.factory)

    if namespace.command == "run":
        return run(
            namespace.target,
            namespace.factory,
            namespace.workers,
            namespace.host,
            namespace.port,
        )

    parser.print_help()
    return ExitCode.USAGE_ERROR


__all__ = ["main", "ExitCode"]
