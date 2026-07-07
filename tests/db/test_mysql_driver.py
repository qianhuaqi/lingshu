from __future__ import annotations

import asyncio
import importlib
import sys
from typing import Any

import pytest
from lingshu.core.application import LingShu
from lingshu.db import DatabaseConfigurationError, DatabaseLifecycleError, mysql
from lingshu.db.config import DatabaseConfig


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


def test_mysql_resource_is_registered_inertly_and_started_with_app_lifecycle() -> None:
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


def test_mysql_driver_startup_failure_is_wrapped_during_app_startup() -> None:
    async def fail_connect(_: DatabaseConfig) -> object:
        raise RuntimeError("connect failed")

    app = LingShu()
    app.add_database_resource(
        mysql.make_mysql_resource(
            DatabaseConfig(name="db.mysql.main", backend="mysql"),
            driver=mysql.MySQLDriver(connect=fail_connect, shutdown=_fake_shutdown),
        )
    )
    app.freeze()

    async def scenario() -> None:
        with pytest.raises(DatabaseLifecycleError) as exc_info:
            await app.startup()
        assert exc_info.value.code == "db.lifecycle.startup_failed"

    asyncio.run(scenario())


def test_mysql_driver_uses_configured_host_defaults_for_aiomysql_connect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_connect(**kwargs: object) -> object:
        captured["kwargs"] = kwargs
        return {"kwargs": kwargs}

    captured: dict[str, object] = {}

    class FakeAiomysql:
        connect = staticmethod(fake_connect)

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
        await app.db.get("db.mysql.main").startup()
        await app.db.get("db.mysql.main").shutdown()

    asyncio.run(scenario())

    assert captured["kwargs"]["host"] == "db.example"
    assert captured["kwargs"]["port"] == 3306
    assert captured["kwargs"]["user"] == "user"
    assert captured["kwargs"]["password"] == "secret"
    assert captured["kwargs"]["db"] == "mysql_db"
    assert "database" not in captured["kwargs"]
