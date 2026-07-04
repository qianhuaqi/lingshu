"""Application target resolution and loading."""

import importlib
import inspect

from lingshu.cli.core import CliError, ExitCode
from lingshu.core.application import LingShu


def load_target(target: str, is_factory: bool) -> LingShu:
    """Resolve and load a LingShu application from a module:attribute string."""
    if ":" not in target:
        raise CliError(
            f"Invalid target '{target}': must be in format 'module:attribute'",
            ExitCode.RESOLUTION_ERROR,
        )

    module_name, sep, attr_name = target.partition(":")
    if not module_name or not attr_name or ":" in attr_name:
        raise CliError(
            f"Invalid target '{target}': malformed module or attribute name",
            ExitCode.RESOLUTION_ERROR,
        )

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise CliError(
            f"Could not import module '{module_name}': {e}",
            ExitCode.RESOLUTION_ERROR,
        ) from e

    if not hasattr(module, attr_name):
        raise CliError(
            f"Module '{module_name}' has no attribute '{attr_name}'",
            ExitCode.RESOLUTION_ERROR,
        )

    obj = getattr(module, attr_name)

    if is_factory:
        if not callable(obj):
            raise CliError(
                f"Factory target '{target}' is not callable",
                ExitCode.RESOLUTION_ERROR,
            )
        if inspect.iscoroutinefunction(obj):
            raise CliError(
                f"Factory target '{target}' is an async function, which is not supported",
                ExitCode.RESOLUTION_ERROR,
            )

        try:
            sig = inspect.signature(obj)
            sig.bind()
        except TypeError as e:
            raise CliError(
                f"Factory target '{target}' must take 0 arguments",
                ExitCode.RESOLUTION_ERROR,
            ) from e

        try:
            app = obj()
        except Exception as e:
            raise CliError(
                f"Factory target '{target}' raised an exception during execution: {e}",
                ExitCode.CONTRACT_ERROR,
            ) from e
    else:
        app = obj

    if not isinstance(app, LingShu):
        raise CliError(
            f"Target '{target}' did not resolve to a LingShu instance (got {type(app).__name__})",
            ExitCode.RESOLUTION_ERROR,
        )

    return app
