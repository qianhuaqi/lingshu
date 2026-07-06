from __future__ import annotations

import pytest
from lingshu.db import (
    DatabaseConfig,
    DatabaseConfigurationError,
    DatabaseManager,
    DatabaseResource,
)
from tests.db.test_resource import FakeDriver


def test_database_manager_registers_gets_and_lists_names() -> None:
    manager = DatabaseManager()
    resource = DatabaseResource(
        DatabaseConfig(name="db.mysql.main", backend="mysql"),
        FakeDriver("mysql"),
    )

    assert manager.register(resource) is resource
    assert manager.get("db.mysql.main") is resource
    assert manager.names() == ("db.mysql.main",)


def test_database_manager_rejects_duplicate_and_unknown_names() -> None:
    manager = DatabaseManager()
    resource = DatabaseResource(
        DatabaseConfig(name="db.mysql.main", backend="mysql"),
        FakeDriver("mysql"),
    )

    manager.register(resource)

    with pytest.raises(DatabaseConfigurationError) as duplicate:
        manager.register(resource)
    assert duplicate.value.code == "db.configuration.duplicate_resource"

    with pytest.raises(DatabaseConfigurationError) as unknown:
        manager.get("db.mysql.analytics")
    assert unknown.value.code == "db.configuration.unknown_resource"
