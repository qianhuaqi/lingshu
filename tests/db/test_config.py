from __future__ import annotations

from types import MappingProxyType

import pytest
from lingshu.db import DatabaseConfig, DatabaseConfigurationError


def test_database_config_redacts_sensitive_values_from_repr_and_safe_details() -> None:
    config = DatabaseConfig(
        name="db.mysql.main",
        backend="mysql",
        dsn="mysql://user:secret@example.internal/private",
        host="example.internal",
        port=3306,
        username="private-user",
        password="private-password",
        token="private-token",
        database="private-db",
        schema="private-schema",
        query_text="select * from private_table",
        options=MappingProxyType({"ssl_ca": "/private/ca.pem"}),
    )

    rendered = repr(config) + repr(config.safe_details)

    for secret in (
        "mysql://",
        "secret",
        "example.internal",
        "private-user",
        "private-password",
        "private-token",
        "private-db",
        "private-schema",
        "private_table",
        "/private/ca.pem",
    ):
        assert secret not in rendered

    assert config.safe_details["name"] == "db.mysql.main"
    assert config.safe_details["backend"] == "mysql"
    assert config.safe_details["has_dsn"] is True
    assert config.safe_details["has_host"] is True
    assert config.safe_details["has_password"] is True
    assert config.safe_details["options_count"] == 1


def test_database_config_validates_resource_name_backend_and_port() -> None:
    with pytest.raises(DatabaseConfigurationError) as bad_name:
        DatabaseConfig(name="mysql.main", backend="mysql")
    assert bad_name.value.code == "db.configuration.invalid_resource_name"

    with pytest.raises(DatabaseConfigurationError) as bad_backend:
        DatabaseConfig(name="db.mysql.main", backend="MySQL")
    assert bad_backend.value.code == "db.configuration.invalid_backend"

    with pytest.raises(DatabaseConfigurationError) as bad_port:
        DatabaseConfig(name="db.mysql.main", backend="mysql", port=70000)
    assert bad_port.value.code == "db.configuration.invalid_port"
