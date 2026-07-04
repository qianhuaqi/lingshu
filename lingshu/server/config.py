"""Server configuration."""

from __future__ import annotations

from dataclasses import dataclass


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
        if self.port < 0 or self.port > 65535:
            raise ValueError("port must be between 0 and 65535")
        if self.max_connections <= 0:
            raise ValueError("max_connections must be positive")
        if self.max_keepalive_requests <= 0:
            raise ValueError("max_keepalive_requests must be positive")
        if self.keepalive_timeout < 0:
            raise ValueError("keepalive_timeout must be non-negative")
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        if self.drain_timeout <= 0:
            raise ValueError("drain_timeout must be positive")
        if self.max_headers_bytes <= 0:
            raise ValueError("max_headers_bytes must be positive")
        if self.max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive")


__all__ = ("ServerConfig",)
