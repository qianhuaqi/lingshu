from __future__ import annotations

import asyncio
import importlib
import sys
from collections.abc import MutableSequence
from typing import Any

import pytest
from lingshu.core.application import ApplicationState, LingShu
from lingshu.core.errors import LifecycleError
from lingshu.db import (
    DatabaseConfig,
    DatabaseConfigurationError,
    DatabaseLifecycleError,
    DatabaseManager,
    DatabaseResource,
)

EventLog = MutableSequence[tuple[str, str]]


class FakeDriver:
    def __init__(
        self,
        events: EventLog,
        *,
        backend: str = "mysql",
        fail_startup: bool = False,
        fail_shutdown: bool = False,
    ) -> None:
        self.backend = backend
        self.events = events
        self.fail_startup = fail_startup
        self.fail_shutdown = fail_shutdown

    async def startup(self, config: DatabaseConfig) -> object:
        self.events.append(("startup", config.name))
        if self.fail_startup:
            raise RuntimeError("startup failed")
        return {"resource": config.name}

    async def shutdown(self, handle: object) -> None:
        resource_name = "<unknown>"
        if isinstance(handle, dict):
            resource = handle.get("resource")
            if isinstance(resource, str):
                resource_name = resource
        self.events.append(("shutdown", resource_name))
        if self.fail_shutdown:
            raise RuntimeError("shutdown failed")


def make_resource(
    name: str,
    events: EventLog,
    *,
    fail_startup: bool = False,
    fail_shutdown: bool = False,
    config_options: dict[str, Any] | None = None,
) -> DatabaseResource:
    return DatabaseResource(
        DatabaseConfig(
            name=name,
            backend=name.split(".", 2)[1],
            dsn="mysql://account-name:super-password@example.internal/customer_db",
            host="example.internal",
            username="account-name",
            password="super-password",
            token="token-value",
            database="customer_db",
            schema="tenant_schema",
            query_text="select * from payroll_private",
            options=config_options or {},
        ),
        FakeDriver(
            events,
            backend=name.split(".", 2)[1],
            fail_startup=fail_startup,
            fail_shutdown=fail_shutdown,
        ),
    )


def test_lingshu_db_property_exposes_database_manager_without_root_exports() -> None:
    import lingshu

    app = LingShu()

    assert isinstance(app.db, DatabaseManager)
    assert app.db.names() == ()
    assert lingshu.__all__ == (
        "HTTPException",
        "LingShu",
        "Request",
        "Response",
    )


def test_add_database_resource_registers_resource_without_starting_driver() -> None:
    events: EventLog = []
    app = LingShu()
    resource = make_resource("db.mysql.main", events)

    registered = app.add_database_resource(resource)

    assert registered is resource
    assert app.db.get("db.mysql.main") is resource
    assert events == []


def test_database_resources_start_and_shutdown_with_application_lifecycle() -> None:
    events: EventLog = []
    app = LingShu()
    app.add_database_resource(make_resource("db.mysql.main", events))
    app.freeze()

    async def scenario() -> None:
        await app.startup()
        await app.shutdown()

    asyncio.run(scenario())

    assert events == [
        ("startup", "db.mysql.main"),
        ("shutdown", "db.mysql.main"),
    ]
    assert app.state is ApplicationState.STOPPED


def test_database_resources_follow_extension_dependency_order() -> None:
    events: EventLog = []
    app = LingShu()
    app.add_database_resource(make_resource("db.mysql.main", events))
    app.add_database_resource(
        make_resource("db.mysql.analytics", events),
        dependencies=("db.mysql.main",),
    )
    app.freeze()

    async def scenario() -> None:
        await app.startup()
        await app.shutdown()

    asyncio.run(scenario())

    assert events == [
        ("startup", "db.mysql.main"),
        ("startup", "db.mysql.analytics"),
        ("shutdown", "db.mysql.analytics"),
        ("shutdown", "db.mysql.main"),
    ]


def test_database_startup_failure_rolls_back_started_resources() -> None:
    events: EventLog = []
    app = LingShu()
    app.add_database_resource(make_resource("db.mysql.main", events))
    app.add_database_resource(
        make_resource("db.mysql.analytics", events, fail_startup=True),
        dependencies=("db.mysql.main",),
    )
    app.freeze()

    async def scenario() -> None:
        with pytest.raises(DatabaseLifecycleError) as exc_info:
            await app.startup()
        assert exc_info.value.code == "db.lifecycle.startup_failed"

    asyncio.run(scenario())

    assert events == [
        ("startup", "db.mysql.main"),
        ("startup", "db.mysql.analytics"),
        ("shutdown", "db.mysql.main"),
    ]
    assert app.state is ApplicationState.FROZEN


def test_database_shutdown_failure_uses_existing_suppress_and_continue_behavior() -> None:
    events: EventLog = []
    app = LingShu()
    app.add_database_resource(make_resource("db.mysql.main", events))
    app.add_database_resource(
        make_resource("db.mysql.analytics", events, fail_shutdown=True),
        dependencies=("db.mysql.main",),
    )
    app.freeze()

    async def scenario() -> None:
        await app.startup()
        await app.shutdown()

    asyncio.run(scenario())

    assert events == [
        ("startup", "db.mysql.main"),
        ("startup", "db.mysql.analytics"),
        ("shutdown", "db.mysql.analytics"),
        ("shutdown", "db.mysql.main"),
    ]
    assert app.state is ApplicationState.STOPPED


def test_duplicate_database_resource_rejected_without_polluting_extension_plan() -> None:
    events: EventLog = []
    app = LingShu()
    app.add_database_resource(make_resource("db.mysql.main", events))

    with pytest.raises(DatabaseConfigurationError) as exc_info:
        app.add_database_resource(make_resource("db.mysql.main", events))

    assert exc_info.value.code == "db.configuration.duplicate_resource"
    plan = app.freeze()
    assert plan.extension_plan.startup_order == ("db.mysql.main",)


def test_database_resource_registration_after_freeze_does_not_mutate_manager() -> None:
    events: EventLog = []
    app = LingShu()
    app.freeze()

    with pytest.raises(LifecycleError) as exc_info:
        app.add_database_resource(make_resource("db.mysql.late", events))

    assert exc_info.value.code == "lifecycle.frozen"
    with pytest.raises(DatabaseConfigurationError) as unknown:
        app.db.get("db.mysql.late")
    assert unknown.value.code == "db.configuration.unknown_resource"


def test_unknown_database_resource_uses_manager_configuration_error() -> None:
    app = LingShu()

    with pytest.raises(DatabaseConfigurationError) as exc_info:
        app.db.get("db.mysql.missing")

    assert exc_info.value.code == "db.configuration.unknown_resource"


def test_database_lifecycle_diagnostics_do_not_leak_sensitive_configuration() -> None:
    events: EventLog = []
    resource = make_resource(
        "db.mysql.main",
        events,
        fail_startup=True,
        config_options={"ssl_ca": "/private/ca.pem"},
    )
    app = LingShu()
    app.add_database_resource(resource)
    app.freeze()

    async def scenario() -> DatabaseLifecycleError:
        with pytest.raises(DatabaseLifecycleError) as exc_info:
            await app.startup()
        return exc_info.value

    error = asyncio.run(scenario())
    public_strings = (
        repr(resource),
        str(error),
        repr(dict(error.safe_details)),
        repr(dict(resource.safe_details)),
        repr(events),
    )

    for secret in (
        "mysql://",
        "example.internal",
        "account-name",
        "super-password",
        "token-value",
        "customer_db",
        "tenant_schema",
        "payroll_private",
        "/private/ca.pem",
    ):
        assert all(secret not in value for value in public_strings)


def test_import_lingshu_and_lingshu_db_do_not_import_database_clients() -> None:
    import lingshu

    lingshu_db = importlib.import_module("lingshu.db")

    assert hasattr(lingshu, "LingShu")
    assert hasattr(lingshu_db, "DatabaseManager")
    for client in ("aiomysql", "motor", "pymongo", "pymysql", "redis"):
        assert client not in sys.modules
