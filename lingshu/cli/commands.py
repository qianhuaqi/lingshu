"""CLI commands implementation."""

import asyncio
import sys

from lingshu.cli.core import CliError, ExitCode
from lingshu.cli.target import load_target
from lingshu.server import ServerConfig, serve


def check(target: str, is_factory: bool) -> int:
    """Validate a LingShu application without starting a server."""
    try:
        app = load_target(target, is_factory)
        app.freeze()
    except CliError as e:
        print(f"Error: {e}", file=sys.stderr)
        return e.exit_code
    except Exception as e:
        print(f"Error validating application: {e}", file=sys.stderr)
        return ExitCode.CONTRACT_ERROR

    return ExitCode.SUCCESS


def run(target: str, is_factory: bool, workers: int, host: str, port: int) -> int:
    """Run a LingShu application using the native HTTP/1.1 server."""
    if workers > 1:
        print(f"Error: Multi-worker is not supported (requested {workers})", file=sys.stderr)
        return ExitCode.UNSUPPORTED_WORKER

    try:
        app = load_target(target, is_factory)
        app.freeze()
    except CliError as e:
        print(f"Error: {e}", file=sys.stderr)
        return e.exit_code
    except Exception as e:
        print(f"Error validating application: {e}", file=sys.stderr)
        return ExitCode.CONTRACT_ERROR

    config = ServerConfig(host=host, port=port)

    try:
        asyncio.run(serve(app, config))
    except (KeyboardInterrupt, asyncio.CancelledError):
        # Safe cleanup handled by serve()'s context manager or internally
        pass
    except Exception as e:
        print(f"Server runtime error: {e}", file=sys.stderr)
        return ExitCode.RUNTIME_FAILURE

    return ExitCode.SUCCESS
