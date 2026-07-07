from __future__ import annotations

from collections.abc import Mapping

import pytest
from lingshu.server.config import ServerConfig


def test_server_config_defaults_are_valid_and_redacted() -> None:
    config = ServerConfig()

    public = config.redacted()
    assert isinstance(public, Mapping)
    assert public["server"]["host"] == "127.0.0.1"  # type: ignore[index]
    assert public["server"]["port"] == 8000  # type: ignore[index]
    assert public["server"]["request_timeout"] == "<internal>"  # type: ignore[index]
    assert public["server"]["max_body_bytes"] == "<internal>"  # type: ignore[index]

    internal = config.redacted(include_internal=True)
    assert internal["server"]["request_timeout"] == 30.0  # type: ignore[index]
    assert internal["server"]["max_body_bytes"] == 1048576  # type: ignore[index]


def test_server_config_redacted_view_is_immutable() -> None:
    rendered = ServerConfig().redacted()

    with pytest.raises(TypeError):
        rendered["server"] = {}  # type: ignore[index]

    with pytest.raises(TypeError):
        rendered["server"]["port"] = 1  # type: ignore[index]


def test_server_config_rejects_invalid_values_without_echoing_host() -> None:
    bad_host = "SECRET\nexample"

    with pytest.raises(ValueError) as exc:
        ServerConfig(host=bad_host)

    rendered = str(exc.value)
    assert "SECRET" not in rendered
    assert "example" not in rendered
    assert "control-free" in rendered


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"port": 70000}, "port must be between 0 and 65535"),
        ({"max_connections": 0}, "max_connections must be positive"),
        ({"max_keepalive_requests": 0}, "max_keepalive_requests must be positive"),
        ({"keepalive_timeout": -1.0}, "keepalive_timeout must be a non-negative"),
        ({"request_timeout": 0.0}, "request_timeout must be positive"),
        ({"drain_timeout": 0.0}, "drain_timeout must be positive"),
        ({"max_headers_bytes": 0}, "max_headers_bytes must be positive"),
        ({"max_body_bytes": 0}, "max_body_bytes must be positive"),
    ],
)
def test_server_config_validation_matrix(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        ServerConfig(**kwargs)  # type: ignore[arg-type]
