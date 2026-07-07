from __future__ import annotations

import asyncio
import importlib
import sys
from typing import Any

import pytest
from lingshu.core.application import LingShu
from lingshu.db import DatabaseConfigurationError, DatabaseLifecycleError, mysql
from lingshu.db.config import DatabaseConfig


class _FakeRawPool:
    def __init__(self, *, async_ops: bool = True) -> None:
        self.async_ops = async_ops
        self.acquire_called = False
        self.release_called = False
        self.closed = False
        self.acquired_connection = object()
        self.released_connection: object | None = None

    async def acquire(self) -> object:
        self.acquire_called = True
        return self.acquired_connection

    async def release(self, connection: object) -> None:
        self.release_called = True
        self.released_connection = connection

    def close(self) -> None:
        self.closed = True


async def _fake_connect(_: DatabaseConfig) -> object:
    return {"connected": True}


async def _fake_shutdown(handle: object) -> None:
    if isinstance(handle, dict):
        handle["closed"] = True


def test_import_lingshu_db_mysql_is_import_safe_without_aiomysql() -> None:
    sys.modules.pop("aiomysql", None)

    if "lingshu.db.mysql" in sys.modules:
        importlib.reload(sys.modules["lingshu.db.mysql"])
    module = importlib.import_module("lingshu.db.mysql")

    assert module.MySQLDriver is not None
    assert module.MySQLDriver().backend == "mysql"
    assert "aiomysql" not in sys.modules


def test_mysql_resource_registration_is_inert(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*_: object, **__: object) -> object:
        raise AssertionError("default startup should not run during registration")

    class FakeAiomysql:
        create_pool = staticmethod(fail_if_called)

    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: FakeAiomysql())

    config = DatabaseConfig(name="db.mysql.main", backend="mysql")
    app = LingShu()
    app.add_database_resource(mysql.make_mysql_resource(config))
    app.freeze()

    assert True


def test_mysql_resource_is_started_with_app_startup_and_shutdown_uses_fake_hooks() -> None:
    config = DatabaseConfig(name="db.mysql.main", backend="mysql")
    app = LingShu()
    events: list[tuple[str, str | bool]] = []

    async def fake_connect(cfg: DatabaseConfig) -> object:
        events.append(("startup", cfg.name))
        return await _fake_connect(cfg)

    async def fake_shutdown(handle: object) -> None:
        await _fake_shutdown(handle)
        closed = handle.get("closed") if isinstance(handle, dict) else False
        events.append(("shutdown", bool(closed)))

    app.add_database_resource(
        mysql.make_mysql_resource(
            config,
            driver=mysql.MySQLDriver(
                connect=fake_connect,
                shutdown=fake_shutdown,
            ),
        )
    )
    assert events == []
    app.freeze()

    async def scenario() -> None:
        await app.startup()
        await app.shutdown()

    asyncio.run(scenario())

    assert events == [
        ("startup", "db.mysql.main"),
        ("shutdown", True),
    ]


def test_mysql_driver_startup_returns_pool_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_pool = _FakeRawPool()

    async def fake_create_pool(**_: object) -> _FakeRawPool:
        return raw_pool

    class FakeAiomysql:
        create_pool = staticmethod(fake_create_pool)

    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: FakeAiomysql())

    driver = mysql.MySQLDriver()
    config = DatabaseConfig(
        name="db.mysql.main",
        backend="mysql",
        dsn="mysql://user:secret@db.example/mysql_db",
    )

    async def scenario() -> None:
        handle = await driver.startup(config)
        assert isinstance(handle, mysql._MySQLPoolHandle)
        assert hasattr(handle, "acquire")
        assert hasattr(handle, "release")
        assert hasattr(handle, "close")
        assert handle._pool is raw_pool

    asyncio.run(scenario())


def test_mysql_pool_handle_acquire_calls_raw_pool_acquire(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_pool = _FakeRawPool()
    adapter = mysql._MySQLPoolHandle(raw_pool)
    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: object())

    async def scenario() -> None:
        conn = await adapter.acquire()
        assert raw_pool.acquire_called is True
        assert conn is raw_pool.acquired_connection

    asyncio.run(scenario())


def test_mysql_pool_handle_release_calls_raw_pool_release(monkeypatch: pytest.MonkeyPatch) -> None:
    raw_pool = _FakeRawPool()
    adapter = mysql._MySQLPoolHandle(raw_pool)
    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: object())

    async def scenario() -> None:
        connection = object()
        await adapter.release(connection)
        assert raw_pool.release_called is True
        assert raw_pool.released_connection is connection

    asyncio.run(scenario())


def test_mysql_driver_shutdown_closes_pool_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_pool = _FakeRawPool()

    async def fake_create_pool(**_: object) -> _FakeRawPool:
        return raw_pool

    class FakeAiomysql:
        create_pool = staticmethod(fake_create_pool)

    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: FakeAiomysql())
    app = LingShu()
    app.add_database_resource(
        mysql.make_mysql_resource(
            DatabaseConfig(
                name="db.mysql.main",
                backend="mysql",
                dsn="mysql://user:secret@db.example/mysql_db",
            )
        )
    )
    app.freeze()

    async def scenario() -> None:
        await app.startup()
        assert raw_pool.closed is False
        await app.shutdown()
        assert raw_pool.closed is True

    asyncio.run(scenario())


def test_mysql_pool_handle_without_acquire_raises_configuration_error() -> None:
    class _RawNoAcquire:
        close_called = False

        def close(self) -> None:
            self.close_called = True

    raw_pool = _RawNoAcquire()
    adapter = mysql._MySQLPoolHandle(raw_pool)

    async def scenario() -> None:
        with pytest.raises(DatabaseConfigurationError) as exc_info:
            await adapter.acquire()

        assert exc_info.value.code == "db.mysql.pool_acquire_unavailable"
        assert "dsn" not in exc_info.value.safe_details
        assert "host" not in exc_info.value.safe_details
        assert "user" not in exc_info.value.safe_details
        assert "password" not in exc_info.value.safe_details
        assert "database" not in exc_info.value.safe_details

    asyncio.run(scenario())


def test_mysql_pool_handle_without_release_raises_configuration_error() -> None:
    class _RawNoRelease:
        close_called = False

        def close(self) -> None:
            self.close_called = True

        async def acquire(self) -> object:
            return object()

    raw_pool = _RawNoRelease()
    adapter = mysql._MySQLPoolHandle(raw_pool)

    async def scenario() -> None:
        connection = object()
        with pytest.raises(DatabaseConfigurationError) as exc_info:
            await adapter.release(connection)

        assert exc_info.value.code == "db.mysql.pool_release_unavailable"
        assert "dsn" not in exc_info.value.safe_details
        assert "host" not in exc_info.value.safe_details
        assert "user" not in exc_info.value.safe_details
        assert "password" not in exc_info.value.safe_details
        assert "database" not in exc_info.value.safe_details

    asyncio.run(scenario())


def test_mysql_driver_optional_dependency_is_required_at_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_import_module(_: str) -> Any:
        raise ModuleNotFoundError("No module named 'aiomysql'")

    monkeypatch.setattr(mysql.importlib, "import_module", missing_import_module)
    driver = mysql.MySQLDriver()
    config = DatabaseConfig(name="db.mysql.main", backend="mysql")

    with pytest.raises(DatabaseConfigurationError) as exc_info:
        asyncio.run(driver.startup(config))

    assert exc_info.value.code == "db.mysql.missing_dependency"


@pytest.mark.parametrize(
    "dsn",
    ["mysql://user:secret@db.example/mysql_db", "mysql+aiomysql://user:secret@db.example/mysql_db"],
)
def test_parse_supported_mysql_dsn_schemes(dsn: str) -> None:
    assert mysql._parse_dsn(dsn)


def test_mysql_driver_rejects_unsupported_asyncmy_dsn_scheme(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_load_aiomysql() -> object:
        return object()

    monkeypatch.setattr(mysql, "_load_aiomysql", fake_load_aiomysql)
    driver = mysql.MySQLDriver()
    config = DatabaseConfig(
        name="db.mysql.main",
        backend="mysql",
        dsn="mysql+asyncmy://user:secret@db.example/mysql_db",
    )

    with pytest.raises(DatabaseConfigurationError) as exc_info:
        asyncio.run(driver.startup(config))

    assert exc_info.value.code == "db.mysql.invalid_dsn"
    assert exc_info.value.safe_details["dsn_scheme"] == "mysql+asyncmy"
    assert "dsn" not in exc_info.value.safe_details
    assert "host" not in exc_info.value.safe_details
    assert "user" not in exc_info.value.safe_details
    assert "password" not in exc_info.value.safe_details
    assert "database" not in exc_info.value.safe_details


def test_mysql_driver_startup_failure_is_wrapped_during_app_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_create_pool(**_: object) -> object:
        raise RuntimeError("create pool failed")

    class FakeAiomysql:
        create_pool = staticmethod(fail_create_pool)

    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: FakeAiomysql())
    app = LingShu()
    app.add_database_resource(
        mysql.make_mysql_resource(
            DatabaseConfig(
                name="db.mysql.main",
                backend="mysql",
                dsn="mysql://user:secret@db.example/mysql_db",
            ),
            driver=mysql.MySQLDriver(),
        )
    )
    app.freeze()

    async def scenario() -> None:
        with pytest.raises(DatabaseLifecycleError) as exc_info:
            await app.startup()
        assert exc_info.value.code == "db.lifecycle.startup_failed"

    asyncio.run(scenario())


def test_app_startup_uses_aiomysql_create_pool_and_shutdown_calls_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    raw_pool = _FakeRawPool()

    async def fake_create_pool(**kwargs: object) -> _FakeRawPool:
        captured["kwargs"] = kwargs
        return raw_pool

    class FakeAiomysql:
        create_pool = staticmethod(fake_create_pool)

    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: FakeAiomysql())
    app = LingShu()
    app.add_database_resource(
        mysql.make_mysql_resource(
            DatabaseConfig(
                name="db.mysql.main",
                backend="mysql",
                dsn="mysql://user:secret@db.example/mysql_db",
            )
        )
    )
    app.freeze()

    async def scenario() -> None:
        await app.startup()
        await app.shutdown()

    asyncio.run(scenario())

    assert captured["kwargs"]["db"] == "mysql_db"
    assert "database" not in captured["kwargs"]
    assert raw_pool.closed is True


def test_mysql_driver_without_create_pool_raises_pool_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeNoPoolAiomysql:
        pass

    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: FakeNoPoolAiomysql())

    driver = mysql.MySQLDriver()
    config = DatabaseConfig(
        name="db.mysql.main",
        backend="mysql",
        dsn="mysql://u:p@db.example/d",
    )

    with pytest.raises(DatabaseConfigurationError) as exc_info:
        asyncio.run(driver.startup(config))

    assert exc_info.value.code == "db.mysql.pool_unavailable"
    assert "dsn" not in exc_info.value.safe_details
    assert "host" not in exc_info.value.safe_details
    assert "user" not in exc_info.value.safe_details
    assert "password" not in exc_info.value.safe_details
    assert "database" not in exc_info.value.safe_details


def test_mysql_driver_uses_configured_host_defaults_for_aiomysql_create_pool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_create_pool(**kwargs: object) -> _FakeRawPool:
        captured["kwargs"] = kwargs
        return _FakeRawPool()

    captured: dict[str, object] = {}

    class FakeAiomysql:
        create_pool = staticmethod(fake_create_pool)

    monkeypatch.setattr(mysql, "_load_aiomysql", lambda: FakeAiomysql())

    config = DatabaseConfig(
        name="db.mysql.main",
        backend="mysql",
        dsn="mysql://user:secret@db.example/mysql_db",
    )
    app = LingShu()
    app.add_database_resource(
        mysql.make_mysql_resource(
            config,
            driver=mysql.MySQLDriver(),
        )
    )
    app.freeze()

    async def scenario() -> None:
        resource = app.db.get("db.mysql.main")
        await resource.startup()
        await resource.shutdown()

    asyncio.run(scenario())

    assert captured["kwargs"]["host"] == "db.example"
    assert captured["kwargs"]["port"] == 3306
    assert captured["kwargs"]["user"] == "user"
    assert captured["kwargs"]["password"] == "secret"
    assert captured["kwargs"]["db"] == "mysql_db"
    assert "database" not in captured["kwargs"]
