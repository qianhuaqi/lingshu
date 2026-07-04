"""End-to-end integration tests for the LingShu framework."""

import asyncio
import json

import pytest
from lingshu import LingShu, Request, Response
from lingshu.server import Server, ServerConfig

_TEST_CONFIG = ServerConfig(
    host="127.0.0.1",
    port=0,
    keepalive_timeout=0.5,
    request_timeout=1.0,
    drain_timeout=0.5,
)

@pytest.fixture
def app() -> LingShu:
    return LingShu()

def test_full_request_response_cycle(app: LingShu) -> None:
    """Test a full request/response cycle including middleware and route parameters."""
    events = []

    async def add_custom_header(request: Request, call_next) -> Response:
        events.append("middleware_in")
        response = await call_next()
        response.add_header("X-E2E-Status", "passed")
        events.append("middleware_out")
        return response

    app.add_middleware(add_custom_header)

    @app.post("/items/{item_id}")
    async def process_item(request: Request) -> Response:
        events.append("handler")
        item_id = request.path_params["item_id"]
        body_bytes = await request.body.read()
        body_str = body_bytes.decode("utf-8")
        data = json.loads(body_str) if body_str else {}

        return Response.json({
            "item_id": item_id,
            "received": data.get("value", None)
        })

    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        reader, writer = await asyncio.open_connection(host, port)

        req_body = b'{"value": 42}'
        req_lines = [
            b"POST /items/abc-123 HTTP/1.1\r\n",
            b"Host: localhost\r\n",
            f"Content-Length: {len(req_body)}\r\n".encode("latin-1"),
            b"Connection: close\r\n",
            b"\r\n",
            req_body,
        ]
        writer.writelines(req_lines)
        await writer.drain()

        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()

        resp_text = response_data.decode("latin-1")
        assert "HTTP/1.1 200 OK" in resp_text
        assert "X-E2E-Status: passed" in resp_text
        assert '{"item_id":"abc-123","received":42}' in resp_text.replace(" ", "")

        assert events == ["middleware_in", "handler", "middleware_out"]

        await srv.close()

    asyncio.run(run())

def test_client_disconnect_safety(app: LingShu) -> None:
    """Test that a client disconnect does not hang the server or leak."""
    handler_started = asyncio.Event()

    @app.get("/long-polling")
    async def long_polling(request: Request) -> Response:
        handler_started.set()
        await asyncio.sleep(0.5)
        return Response.text("done")

    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        _reader, writer = await asyncio.open_connection(host, port)

        writer.write(b"GET /long-polling HTTP/1.1\r\nHost: localhost\r\n\r\n")
        await writer.drain()

        # Wait until handler actually starts
        await asyncio.wait_for(handler_started.wait(), timeout=1.0)

        # Simulate abrupt client disconnect
        writer.close()
        await writer.wait_closed()

        # Ensure server can still close safely without hanging
        await srv.close()

    asyncio.run(run())

def test_graceful_shutdown_drain(app: LingShu) -> None:
    """Test that server drains gracefully, finishing active requests."""
    @app.get("/process")
    async def process(request: Request) -> Response:
        await asyncio.sleep(0.2)
        return Response.text("finished")

    async def run() -> None:
        app.freeze()
        # Ensure drain_timeout is large enough to allow handler to finish
        srv_config = ServerConfig(
            host="127.0.0.1",
            port=0,
            drain_timeout=1.0,
            request_timeout=2.0,
        )
        srv = Server(app, srv_config)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        reader, writer = await asyncio.open_connection(host, port)
        writer.write(b"GET /process HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer.drain()

        # Wait slightly to ensure request is being handled
        await asyncio.sleep(0.05)

        # Initiate drain
        drain_task = asyncio.create_task(srv.drain())

        # Reader should eventually get the full response despite drain
        response_data = await reader.read()
        resp_text = response_data.decode("latin-1")

        assert "HTTP/1.1 200 OK" in resp_text
        assert "finished" in resp_text

        writer.close()
        await writer.wait_closed()

        await drain_task
        await srv.close()

    asyncio.run(run())
