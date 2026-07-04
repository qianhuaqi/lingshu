"""Tests for the native single-worker HTTP/1.1 server."""

import asyncio
from collections.abc import AsyncIterator

import pytest
from lingshu import LingShu, Request, Response
from lingshu.server import Server, ServerConfig

# Use a random open port for tests by binding to 0
_TEST_CONFIG = ServerConfig(
    host="127.0.0.1",
    port=0,
    keepalive_timeout=0.5,
    request_timeout=0.5,
    drain_timeout=0.5,
)


@pytest.fixture
def app() -> LingShu:
    return LingShu()


@pytest.fixture
async def server(app: LingShu) -> AsyncIterator[Server]:
    srv = Server(app, _TEST_CONFIG)
    await srv.startup()
    try:
        yield srv
    finally:
        await srv.close()


def test_server_startup_and_close(app: LingShu) -> None:
    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        assert srv._server.is_serving()
        await srv.close()
        assert srv._server is None

    asyncio.run(run())


def test_server_drain(app: LingShu) -> None:
    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        await srv.drain()
        # Server should stop accepting connections
        # Server should stop accepting connections
        await srv.close()

    asyncio.run(run())


def test_basic_http_request(app: LingShu) -> None:
    async def run() -> None:
        @app.get("/hello")
        async def hello(request: Request) -> Response:
            return Response.text("world")

        app.freeze()

        srv = Server(app, _TEST_CONFIG)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        reader, writer = await asyncio.open_connection(host, port)

        writer.write(b"GET /hello HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        response_text = response_data.decode("latin-1")
        assert "HTTP/1.1 200 OK" in response_text
        assert "world" in response_text

        await srv.close()

    asyncio.run(run())


def test_request_body(app: LingShu) -> None:
    async def run() -> None:
        @app.post("/echo")
        async def echo(request: Request) -> Response:
            body = await request.body.read()
            return Response.bytes(body)

        app.freeze()

        srv = Server(app, _TEST_CONFIG)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        reader, writer = await asyncio.open_connection(host, port)

        request_lines = [
            b"POST /echo HTTP/1.1\r\n",
            b"Host: localhost\r\n",
            b"Content-Length: 5\r\n",
            b"Connection: close\r\n",
            b"\r\n",
            b"hello",
        ]
        writer.writelines(request_lines)
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        response_text = response_data.decode("latin-1")
        assert "HTTP/1.1 200 OK" in response_text
        assert "hello" in response_text

        await srv.close()

    asyncio.run(run())


def test_keep_alive(app: LingShu) -> None:
    async def run() -> None:
        @app.get("/")
        async def index(request: Request) -> Response:
            return Response.text("ok")

        app.freeze()

        srv = Server(app, _TEST_CONFIG)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        reader, writer = await asyncio.open_connection(host, port)

        writer.write(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        await writer.drain()

        # Read first response until headers end (we know it's small)
        await reader.readuntil(b"ok")

        # Send second request on same connection
        writer.write(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        response_text = response_data.decode("latin-1")
        assert "HTTP/1.1 200 OK" in response_text
        assert "ok" in response_text

        await srv.close()

    asyncio.run(run())


def test_bad_request(app: LingShu) -> None:
    async def run() -> None:
        app.freeze()

        srv = Server(app, _TEST_CONFIG)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        reader, writer = await asyncio.open_connection(host, port)

        # Invalid request line
        writer.write(b"INVALID\r\n\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        response_text = response_data.decode("latin-1")
        assert "HTTP/1.1 400 Bad Request" in response_text

        await srv.close()

    asyncio.run(run())


def test_oversized_body(app: LingShu) -> None:
    async def run() -> None:
        @app.post("/")
        async def index(request: Request) -> Response:
            return Response.text("ok")

        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        reader, writer = await asyncio.open_connection(host, port)

        # max_body_bytes is 1048576, we send 2000000
        writer.write(b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 2000000\r\n\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        assert b"HTTP/1.1 413" in response_data
        await srv.close()

    asyncio.run(run())


def test_oversized_header(app: LingShu) -> None:
    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        reader, writer = await asyncio.open_connection(host, port)

        # max_headers_bytes is 8192
        big_header = b"X-Big: " + (b"A" * 70000) + b"\r\n"
        writer.write(b"GET / HTTP/1.1\r\nHost: localhost\r\n" + big_header + b"\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        assert b"HTTP/1.1 431" in response_data
        await srv.close()

    asyncio.run(run())


def test_oversized_request_line(app: LingShu) -> None:
    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        reader, writer = await asyncio.open_connection(host, port)

        big_target = b"/" + (b"A" * 70000)
        writer.write(b"GET " + big_target + b" HTTP/1.1\r\nHost: localhost\r\n\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        assert b"HTTP/1.1 414" in response_data
        await srv.close()

    asyncio.run(run())


def test_duplicate_content_length(app: LingShu) -> None:
    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        reader, writer = await asyncio.open_connection(host, port)

        writer.write(
            b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\nContent-Length: 5\r\n\r\n"
        )
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        assert b"HTTP/1.1 400" in response_data
        await srv.close()

    asyncio.run(run())


def test_transfer_encoding_rejected(app: LingShu) -> None:
    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        reader, writer = await asyncio.open_connection(host, port)

        writer.write(b"POST / HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        assert b"HTTP/1.1 400" in response_data
        await srv.close()

    asyncio.run(run())


def test_handler_timeout(app: LingShu) -> None:
    async def run() -> None:
        @app.get("/sleep")
        async def sleep(request: Request) -> Response:
            await asyncio.sleep(2.0)
            return Response.text("ok")

        app.freeze()
        srv = Server(app, _TEST_CONFIG)  # request_timeout=0.5
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        reader, writer = await asyncio.open_connection(host, port)

        writer.write(b"GET /sleep HTTP/1.1\r\nHost: localhost\r\n\r\n")
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        assert b"HTTP/1.1 408" in response_data
        await srv.close()

    asyncio.run(run())


def test_keepalive_connection_id(app: LingShu) -> None:
    async def run() -> None:
        ids = []

        @app.get("/")
        async def index(request: Request) -> Response:
            ids.append(request.connection_id)
            return Response.text("ok")

        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        reader, writer = await asyncio.open_connection(host, port)

        writer.write(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        await writer.drain()
        await reader.readuntil(b"ok")

        writer.write(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer.drain()
        await reader.read()
        writer.close()
        await writer.wait_closed()

        assert len(ids) == 2
        assert ids[0] == ids[1]
        await srv.close()

    asyncio.run(run())


def test_startup_failure_cleanup(app: LingShu, monkeypatch: pytest.MonkeyPatch) -> None:
    async def run() -> None:
        from typing import Any

        async def mock_start_server(*args: Any, **kwargs: Any) -> Any:
            raise OSError("mock bind failure")

        monkeypatch.setattr(asyncio, "start_server", mock_start_server)
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        with pytest.raises(OSError, match="mock bind failure"):
            await srv.startup()
        assert srv._server is None
        assert srv._app_scope is None
        await srv.close()
        await srv.close()  # repeated close is safe

    asyncio.run(run())


def test_server_drain_timeout(app: LingShu) -> None:
    async def run() -> None:
        @app.get("/slow")
        async def slow(request: Request) -> Response:
            await asyncio.sleep(2.0)
            return Response.text("slow")

        app.freeze()
        # drain_timeout < 2.0 to trigger timeout
        srv_config = ServerConfig(
            host="127.0.0.1",
            port=0,
            drain_timeout=0.2,
            request_timeout=3.0,
            keepalive_timeout=1.0,
        )
        srv = Server(app, srv_config)
        await srv.startup()
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        # Start a background request
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(b"GET /slow HTTP/1.1\r\nHost: localhost\r\n\r\n")
        await writer.drain()

        # Wait slightly to ensure server picks it up
        await asyncio.sleep(0.1)
        assert len(srv._connections) == 1

        # Drain, which should time out because handler takes 2.0s, drain takes 0.2s
        await srv.drain()

        # The drain should have closed the connections forcefully due to timeout
        assert len(srv._connections) == 0

        with pytest.raises(asyncio.IncompleteReadError):
            await reader.readexactly(100)

        writer.close()
        await writer.wait_closed()
        await srv.close()

    asyncio.run(run())
