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
