"""Minimal optional MySQL database extension boundary.

The class in this module provides a tiny, import-safe integration point that can
later be replaced by a full driver implementation.
"""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Awaitable, Callable
from typing import Any
from urllib.parse import urlsplit

from lingshu.db.config import DatabaseConfig
from lingshu.db.driver import DatabaseDriver
from lingshu.db.errors import DatabaseConfigurationError
from lingshu.db.resource import DatabaseResource

_ConnectCallable = Callable[[DatabaseConfig], Awaitable[object]]
_ShutdownCallable = Callable[[object], Awaitable[None]]


def _load_aiomysql() -> Any:
    """Load the optional aiomysql dependency."""

    try:
        return importlib.import_module("aiomysql")
    except ModuleNotFoundError as exc:
        raise DatabaseConfigurationError(
            "db.mysql.missing_dependency",
            "Optional MySQL dependency 'aiomysql' is not installed.",
            safe_details={"backend": "mysql"},
        ) from exc


def _parse_dsn(dsn: str) -> dict[str, str | int | None]:
    parsed = urlsplit(dsn)
    if parsed.scheme and parsed.scheme not in {"mysql", "mysql+aiomysql"}:
        raise DatabaseConfigurationError(
            "db.mysql.invalid_dsn",
            "MySQL DSN must use mysql scheme.",
            safe_details={"backend": "mysql", "dsn_scheme": parsed.scheme or ""},
        )

    return {
        "host": parsed.hostname,
        "port": parsed.port,
        "user": parsed.username,
        "password": parsed.password,
        "db": parsed.path.removeprefix("/") if parsed.path else None,
    }


def _build_connection_kwargs(config: DatabaseConfig) -> dict[str, object]:
    values: dict[str, object] = {}
    if config.dsn is not None:
        values.update(_parse_dsn(config.dsn))

    fallback = {
        "host": config.host,
        "port": config.port,
        "user": config.username,
        "password": config.password,
        "db": config.database,
    }
    for key, value in fallback.items():
        if key not in values and value is not None:
            values[key] = value

    return {k: v for k, v in values.items() if v is not None}


class _MySQLPoolHandle:
    """Adapter around an `aiomysql` pool handle.

    This wrapper keeps the raw pool object internal and exposes only the minimum
    acquire/release/close boundary needed by the current phase.
    """

    def __init__(self, pool: object) -> None:
        self._pool = pool

    async def acquire(self) -> object:
        acquire_callable = getattr(self._pool, "acquire", None)
        if not callable(acquire_callable):
            raise DatabaseConfigurationError(
                "db.mysql.pool_acquire_unavailable",
                "aiomysql pool handle does not provide 'acquire'.",
                safe_details={"backend": "mysql"},
            )

        result = acquire_callable()
        if inspect.isawaitable(result):
            return await result
        return result

    async def release(self, connection: object) -> None:
        release_callable = getattr(self._pool, "release", None)
        if not callable(release_callable):
            raise DatabaseConfigurationError(
                "db.mysql.pool_release_unavailable",
                "aiomysql pool handle does not provide 'release'.",
                safe_details={"backend": "mysql"},
            )

        result = release_callable(connection)
        if inspect.isawaitable(result):
            await result

    async def close(self) -> None:
        close_callable = getattr(self._pool, "close", None)
        if callable(close_callable):
            result = close_callable()
            if inspect.isawaitable(result):
                await result
        wait_closed_callable = getattr(self._pool, "wait_closed", None)
        if callable(wait_closed_callable):
            wait_result = wait_closed_callable()
            if inspect.isawaitable(wait_result):
                await wait_result


async def _default_connect(config: DatabaseConfig) -> object:
    aiomysql = _load_aiomysql()
    kwargs = _build_connection_kwargs(config)
    if "host" not in kwargs:
        raise DatabaseConfigurationError(
            "db.mysql.missing_connection_target",
            "MySQL connection target is not fully configured.",
            safe_details={"backend": config.backend, "name": config.name},
        )
    kwargs.setdefault("port", 3306)
    create_pool = getattr(aiomysql, "create_pool", None)
    if not callable(create_pool):
        raise DatabaseConfigurationError(
            "db.mysql.pool_unavailable",
            "aiomysql client module does not provide 'create_pool'.",
            safe_details={"backend": config.backend, "name": config.name},
        )
    result = create_pool(**kwargs)
    if inspect.isawaitable(result):
        result = await result
    return _MySQLPoolHandle(result)


async def _default_shutdown(handle: object) -> None:
    close_callable = getattr(handle, "close", None)
    if callable(close_callable):
        result = close_callable()
        if inspect.isawaitable(result):
            await result


class MySQLDriver(DatabaseDriver):
    """Small driver boundary that accepts minimal MySQL startup/shutdown hooks."""

    @property
    def backend(self) -> str:
        return "mysql"

    def __init__(
        self,
        *,
        connect: _ConnectCallable | None = None,
        shutdown: _ShutdownCallable | None = None,
    ) -> None:
        self._connect = connect or _default_connect
        self._shutdown = shutdown or _default_shutdown

    async def startup(self, config: DatabaseConfig) -> object:
        return await self._connect(config)

    async def shutdown(self, handle: object) -> None:
        await self._shutdown(handle)


def make_mysql_resource(
    config: DatabaseConfig,
    *,
    driver: DatabaseDriver | None = None,
) -> DatabaseResource:
    """Build a `DatabaseResource` using the `lingshu.db` contracts."""

    return DatabaseResource(config=config, driver=driver or MySQLDriver())


__all__ = (
    "MySQLDriver",
    "make_mysql_resource",
)
