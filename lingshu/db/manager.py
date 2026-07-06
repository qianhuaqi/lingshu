"""Database resource registry."""

from __future__ import annotations

from .errors import DatabaseConfigurationError
from .resource import DatabaseResource


class DatabaseManager:
    """Small registry for named database resources."""

    __slots__ = ("_resources",)

    def __init__(self) -> None:
        self._resources: dict[str, DatabaseResource] = {}

    def register(self, resource: DatabaseResource) -> DatabaseResource:
        if resource.name in self._resources:
            raise DatabaseConfigurationError(
                "db.configuration.duplicate_resource",
                "Database resource names must be unique.",
                safe_details=resource.safe_details,
            )
        self._resources[resource.name] = resource
        return resource

    def get(self, name: str) -> DatabaseResource:
        try:
            return self._resources[name]
        except KeyError as exc:
            raise DatabaseConfigurationError(
                "db.configuration.unknown_resource",
                "Database resource is not registered.",
                safe_details={"name": name},
                cause=exc,
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._resources)


__all__ = ("DatabaseManager",)
