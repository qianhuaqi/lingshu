"""Server configuration."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

_MAX_HOST_LENGTH: Final[int] = 253


def _has_control(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def _require_host(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("host must be a string")
    if not value:
        raise ValueError("host must be non-empty")
    if len(value) > _MAX_HOST_LENGTH or _has_control(value):
        raise ValueError("host must be bounded and control-free")
    return value


def _require_port(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("port must be an integer")
    if value < 0 or value > 65535:
        raise ValueError("port must be between 0 and 65535")
    return value


def _require_positive_integer(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _require_non_negative_float(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{name} must be numeric")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise ValueError(f"{name} must be a non-negative finite number")
    return normalized


def _require_positive_float(name: str, value: object) -> float:
    normalized = _require_non_negative_float(name, value)
    if normalized <= 0:
        raise ValueError(f"{name} must be positive")
    return normalized


@dataclass(frozen=True, slots=True)
class ServerConfig:
    """Configuration for the single-worker HTTP/1.1 server."""

    host: str = "127.0.0.1"
    port: int = 8000
    max_connections: int = 1000
    max_keepalive_requests: int = 100
    keepalive_timeout: float = 5.0
    request_timeout: float = 30.0
    drain_timeout: float = 10.0
    max_headers_bytes: int = 65536
    max_body_bytes: int = 1048576  # 1MB

    def __post_init__(self) -> None:
        _require_host(self.host)
        _require_port(self.port)
        _require_positive_integer("max_connections", self.max_connections)
        _require_positive_integer("max_keepalive_requests", self.max_keepalive_requests)
        _require_non_negative_float("keepalive_timeout", self.keepalive_timeout)
        _require_positive_float("request_timeout", self.request_timeout)
        _require_positive_float("drain_timeout", self.drain_timeout)
        _require_positive_integer("max_headers_bytes", self.max_headers_bytes)
        _require_positive_integer("max_body_bytes", self.max_body_bytes)

    def redacted(self, *, include_internal: bool = False) -> Mapping[str, object]:
        """Return a safe diagnostic view of static server configuration."""

        public: dict[str, object] = {
            "host": self.host,
            "port": self.port,
        }
        if include_internal:
            public.update(
                {
                    "max_connections": self.max_connections,
                    "max_keepalive_requests": self.max_keepalive_requests,
                    "keepalive_timeout": self.keepalive_timeout,
                    "request_timeout": self.request_timeout,
                    "drain_timeout": self.drain_timeout,
                    "max_headers_bytes": self.max_headers_bytes,
                    "max_body_bytes": self.max_body_bytes,
                }
            )
        else:
            public.update(
                {
                    "max_connections": "<internal>",
                    "max_keepalive_requests": "<internal>",
                    "keepalive_timeout": "<internal>",
                    "request_timeout": "<internal>",
                    "drain_timeout": "<internal>",
                    "max_headers_bytes": "<internal>",
                    "max_body_bytes": "<internal>",
                }
            )
        return MappingProxyType({"server": MappingProxyType(public)})


__all__ = ("ServerConfig",)
