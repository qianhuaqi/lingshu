"""Database configuration contracts with redacted diagnostics."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from lingshu.core.errors import SafeDetails, freeze_safe_details

from .errors import DatabaseConfigurationError

_RESOURCE_NAME_PATTERN = re.compile(r"^db\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_BACKEND_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    """Import-safe database resource configuration.

    Sensitive fields are intentionally omitted from ``repr`` and ``safe_details``.
    """

    name: str
    backend: str
    dsn: str | None = field(default=None, repr=False)
    host: str | None = field(default=None, repr=False)
    port: int | None = field(default=None, repr=False)
    username: str | None = field(default=None, repr=False)
    password: str | None = field(default=None, repr=False)
    token: str | None = field(default=None, repr=False)
    database: str | None = field(default=None, repr=False)
    schema: str | None = field(default=None, repr=False)
    query_text: str | None = field(default=None, repr=False)
    options: MappingProxyType[str, Any] = field(
        default_factory=lambda: MappingProxyType({}),
        repr=False,
    )

    def __post_init__(self) -> None:
        if _RESOURCE_NAME_PATTERN.fullmatch(self.name) is None:
            raise DatabaseConfigurationError(
                "db.configuration.invalid_resource_name",
                "Database resource names must use the db.<backend>.<name> form.",
                safe_details={"name": self.name},
            )
        if _BACKEND_PATTERN.fullmatch(self.backend) is None:
            raise DatabaseConfigurationError(
                "db.configuration.invalid_backend",
                "Database backend names must be lowercase identifiers.",
                safe_details={"name": self.name},
            )
        name_backend = self.name.split(".", 2)[1]
        if name_backend != self.backend:
            raise DatabaseConfigurationError(
                "db.configuration.backend_name_mismatch",
                "Database resource name backend must match the configured backend.",
                safe_details={"name": self.name, "backend": self.backend},
            )
        if self.port is not None and not 1 <= self.port <= 65535:
            raise DatabaseConfigurationError(
                "db.configuration.invalid_port",
                "Database ports must be between 1 and 65535.",
                safe_details={"name": self.name, "backend": self.backend},
            )
        object.__setattr__(self, "options", MappingProxyType(dict(self.options)))

    @property
    def safe_details(self) -> SafeDetails:
        """Return coarse diagnostics with no connection secrets or topology."""

        return freeze_safe_details(
            {
                "name": self.name,
                "backend": self.backend,
                "has_dsn": self.dsn is not None,
                "has_host": self.host is not None,
                "has_port": self.port is not None,
                "has_username": self.username is not None,
                "has_password": self.password is not None,
                "has_token": self.token is not None,
                "has_database": self.database is not None,
                "has_schema": self.schema is not None,
                "has_query_text": self.query_text is not None,
                "options_count": len(self.options),
            }
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, backend={self.backend!r}, "
            f"safe_details={dict(self.safe_details)!r})"
        )


__all__ = ("DatabaseConfig",)
