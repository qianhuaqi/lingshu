from __future__ import annotations

import asyncio

import pytest
from lingshu.db import (
    DatabaseConfig,
    DatabaseConfigurationError,
    DatabaseLifecycleError,
    DatabaseResource,
)


class FakeDriver:
    def __init__(self, backend: str) -> None:
        self.backend = backend
        self.startup_calls: list[DatabaseConfig] = []
        self.shutdown_calls: list[object] = []

    async def startup(self, config: DatabaseConfig) -> object:
        self.startup_calls.append(config)
        return {"resource": config.name}

    async def shutdown(self, handle: object) -> None:
        self.shutdown_calls.append(handle)


def test_database_resource_registration_does_not_start_driver() -> None:
    driver = FakeDriver("mysql")
    resource = DatabaseResource(
        DatabaseConfig(name="db.mysql.main", backend="mysql"),
        driver,
    )

    assert resource.name == "db.mysql.main"
    assert resource.backend == "mysql"
    assert resource.started is False
    assert driver.startup_calls == []
    assert driver.shutdown_calls == []


def test_database_resource_startup_and_shutdown_delegate_to_driver() -> None:
    driver = FakeDriver("mysql")
    config = DatabaseConfig(name="db.mysql.main", backend="mysql")
    resource = DatabaseResource(config, driver)

    async def scenario() -> None:
        await resource.startup()

        assert resource.started is True
        assert driver.startup_calls == [config]
        assert resource.safe_details["state"] == "started"

        await resource.shutdown()

        assert resource.started is False
        assert driver.shutdown_calls == [{"resource": "db.mysql.main"}]
        assert resource.safe_details["state"] == "stopped"

    asyncio.run(scenario())


def test_database_resource_rejects_invalid_lifecycle_transitions() -> None:
    resource = DatabaseResource(
        DatabaseConfig(name="db.mysql.main", backend="mysql"),
        FakeDriver("mysql"),
    )

    async def scenario() -> None:
        await resource.startup()
        with pytest.raises(DatabaseLifecycleError) as second_start:
            await resource.startup()
        assert second_start.value.code == "db.lifecycle.invalid_startup_state"

    asyncio.run(scenario())


def test_database_resource_requires_matching_driver_backend() -> None:
    with pytest.raises(DatabaseConfigurationError) as mismatch:
        DatabaseResource(
            DatabaseConfig(name="db.mysql.main", backend="mysql"),
            FakeDriver("redis"),
        )
    assert mismatch.value.code == "db.configuration.backend_mismatch"
