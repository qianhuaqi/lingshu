"""Database foundation error contracts."""

from __future__ import annotations

from collections.abc import Mapping

from lingshu.core.errors import FatalScope, LingShuError


class DatabaseError(LingShuError):
    """Base class for database foundation failures."""

    def __init__(
        self,
        code: str,
        safe_message: str,
        *,
        safe_details: Mapping[str, object] | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            code,
            safe_message,
            fatal_scope=FatalScope.OPERATION,
            safe_details=safe_details,
            cause=cause,
        )


class DatabaseConfigurationError(DatabaseError):
    """Invalid database foundation configuration."""


class DatabaseLifecycleError(DatabaseError):
    """Invalid database resource lifecycle transition."""


__all__ = (
    "DatabaseConfigurationError",
    "DatabaseError",
    "DatabaseLifecycleError",
)
