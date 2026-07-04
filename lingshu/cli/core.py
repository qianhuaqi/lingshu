"""Core CLI primitives."""

import enum


class ExitCode(enum.IntEnum):
    """Exit codes for CLI commands."""

    SUCCESS = 0
    USAGE_ERROR = 2
    RESOLUTION_ERROR = 3
    CONTRACT_ERROR = 4
    UNSUPPORTED_WORKER = 5
    RUNTIME_FAILURE = 6


class CliError(Exception):
    """Base exception for CLI-level errors."""

    def __init__(self, message: str, exit_code: ExitCode) -> None:
        super().__init__(message)
        self.exit_code = exit_code
