"""Minimal optional MySQL database extension boundary."""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, cast
from urllib.parse import urlsplit

from lingshu.db.config import DatabaseConfig
from lingshu.db.driver import DatabaseDriver
from lingshu.db.errors import DatabaseConfigurationError
from lingshu.db.resource import DatabaseResource

_ConnectCallable = Callable[[DatabaseConfig], Awaitable[object]]
_ShutdownCallable = Callable[[object], Awaitable[None]]


class _MySQLCursor(Protocol):
    def execute(self, sql: str, params: object | None = None) -> object | Awaitable[object]: ...

    def fetchone(self) -> object | Awaitable[object]: ...

    def fetchall(self) -> object | Awaitable[object]: ...

    def close(self) -> object | Awaitable[None]: ...


class _MySQLConnection(Protocol):
    def cursor(self) -> object | Awaitable[object]: ...


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


async def _maybe_await(value: object) -> object:
    if inspect.isawaitable(value):
        return await value
    return value


class _MySQLPoolHandle:
    """Internal adapter around an `aiomysql` pool handle."""

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
        return await _maybe_await(acquire_callable())

    async def release(self, connection: object) -> None:
        release_callable = getattr(self._pool, "release", None)
        if not callable(release_callable):
            raise DatabaseConfigurationError(
                "db.mysql.pool_release_unavailable",
                "aiomysql pool handle does not provide 'release'.",
                safe_details={"backend": "mysql"},
            )
        await _maybe_await(release_callable(connection))

    async def _close_cursor(self, cursor: object) -> None:
        close_callable = getattr(cursor, "close", None)
        if callable(close_callable):
            await _maybe_await(close_callable())

    async def close(self) -> None:
        close_callable = getattr(self._pool, "close", None)
        if callable(close_callable):
            await _maybe_await(close_callable())
        wait_closed_callable = getattr(self._pool, "wait_closed", None)
        if callable(wait_closed_callable):
            await _maybe_await(wait_closed_callable())

    async def _execute_internal(
        self,
        sql: str,
        params: object | None,
        *,
        fetch: str | None = None,
    ) -> object:
        connection = None
        cursor = None
        primary_error = False
        cursor_close_error: BaseException | None = None
        release_error: BaseException | None = None
        try:
            connection = cast(_MySQLConnection, await self.acquire())
            cursor = cast(_MySQLCursor, await _maybe_await(connection.cursor()))
            execute_result = await _maybe_await(cursor.execute(sql, params))
            if fetch == "one":
                return await _maybe_await(cursor.fetchone())
            if fetch == "all":
                rows = await _maybe_await(cursor.fetchall())
                if isinstance(rows, tuple | list):
                    return list(rows)
                return rows
            return execute_result
        except BaseException:
            primary_error = True
            raise
        finally:
            if cursor is not None:
                try:
                    await self._close_cursor(cursor)
                except BaseException as exc:
                    cursor_close_error = exc
            if connection is not None:
                try:
                    await self.release(connection)
                except BaseException as exc:
                    release_error = exc
            if not primary_error:
                if cursor_close_error is not None:
                    raise cursor_close_error
                if release_error is not None:
                    raise release_error

    async def execute(self, sql: str, params: object | None = None) -> object:
        return await self._execute_internal(sql, params)

    async def fetch_one(self, sql: str, params: object | None = None) -> object | None:
        return await self._execute_internal(sql, params, fetch="one")

    async def fetch_all(self, sql: str, params: object | None = None) -> object:
        return await self._execute_internal(sql, params, fetch="all")


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
    pool = await _maybe_await(create_pool(**kwargs))
    return _MySQLPoolHandle(pool)


async def _default_shutdown(handle: object) -> None:
    close_callable = getattr(handle, "close", None)
    if callable(close_callable):
        await _maybe_await(close_callable())


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
