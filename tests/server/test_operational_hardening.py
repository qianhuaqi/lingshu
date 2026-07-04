from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Any

from lingshu import LingShu, Response
from lingshu.core.time import SystemMonotonicClock
from lingshu.http.message import HTTPVersion
from lingshu.http.response import ResponseState
from lingshu.runtime.scope import Scope, ScopeKind
from lingshu.server import Server, ServerConfig
from lingshu.server.protocol import HttpConnection


class ClosingWriter:
    def __init__(self) -> None:
        self.closed = False
        self.waited = False

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        self.waited = True


class FailingWriter:
    def get_extra_info(self, name: str) -> object:
        return None

    def writelines(self, lines: list[bytes]) -> None:
        del lines

    def write(self, data: bytes) -> None:
        del data

    async def drain(self) -> None:
        raise BrokenPipeError("writer failed SECRET_DETAIL")

    def close(self) -> None:
        raise BrokenPipeError("close failed SECRET_DETAIL")


def _server_config(**overrides: Any) -> ServerConfig:
    values: dict[str, object] = {
        "host": "127.0.0.1",
        "port": 0,
        "keepalive_timeout": 0.2,
        "request_timeout": 0.2,
        "drain_timeout": 0.2,
    }
    values.update(overrides)
    return ServerConfig(**values)  # type: ignore[arg-type]


async def _server_endpoint(server: Server) -> tuple[str, int]:
    assert server._server is not None
    sock = server._server.sockets[0]
    host, port = sock.getsockname()
    return str(host), int(port)


async def _wait_for_no_connections(server: Server) -> None:
    for _ in range(50):
        if not server._connections:
            return
        await asyncio.sleep(0.01)
    assert not server._connections


def test_not_ready_connection_is_closed_without_scope_leak() -> None:
    async def run() -> None:
        app = LingShu()
        app.freeze()
        server = Server(app, _server_config())
        writer = ClosingWriter()

        await server._handle_connection(asyncio.StreamReader(), writer)  # type: ignore[arg-type]

        assert writer.closed is True
        assert writer.waited is True
        assert not server._connections
        assert server._app_scope is None

    asyncio.run(run())


def test_client_disconnect_before_headers_releases_connection() -> None:
    async def run() -> None:
        app = LingShu()
        app.freeze()
        server = Server(app, _server_config())
        await server.startup()
        host, port = await _server_endpoint(server)

        _reader, writer = await asyncio.open_connection(host, port)
        writer.write(b"GET /partial")
        await writer.drain()
        writer.close()
        with suppress(Exception):
            await writer.wait_closed()

        await _wait_for_no_connections(server)
        await server.close()

    asyncio.run(run())


def test_incomplete_body_times_out_with_safe_response() -> None:
    async def run() -> None:
        app = LingShu()
        app.freeze()
        server = Server(app, _server_config(request_timeout=0.05))
        await server.startup()
        host, port = await _server_endpoint(server)

        reader, writer = await asyncio.open_connection(host, port)
        writer.write(
            b"POST /upload HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"Content-Length: 10\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"x"
        )
        await writer.drain()

        response = await reader.read()
        text = response.decode("latin-1")
        assert "HTTP/1.1 408 Request Timeout" in text
        assert "Traceback" not in text
        assert "SECRET" not in text

        writer.close()
        with suppress(Exception):
            await writer.wait_closed()
        await server.close()

    asyncio.run(run())


def test_drain_and_close_are_idempotent() -> None:
    async def run() -> None:
        app = LingShu()
        app.freeze()
        server = Server(app, _server_config())
        await server.startup()

        await server.drain()
        await server.drain()
        await server.close()
        await server.close()

        assert server._server is None
        assert server._app_scope is None
        assert not server._connections

    asyncio.run(run())


def test_writer_failure_during_response_commit_is_safe() -> None:
    async def run() -> None:
        app = LingShu()
        app.freeze()
        conn_scope = Scope.application(clock=SystemMonotonicClock()).create_child(
            ScopeKind.CONNECTION
        )
        writer = FailingWriter()
        connection = HttpConnection(
            app,
            _server_config(),
            conn_scope,
            asyncio.StreamReader(),
            writer,  # type: ignore[arg-type]
        )
        response = Response.text("body that will not be sent")

        await connection._commit_response(response, HTTPVersion.HTTP_1_1)
        connection.close()

        assert response.state is ResponseState.ABORTED

    asyncio.run(run())
