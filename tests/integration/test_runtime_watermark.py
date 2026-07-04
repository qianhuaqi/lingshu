"""Runtime Record and hard-watermark integration tests."""

import asyncio

import pytest
from lingshu import LingShu, Request, Response
from lingshu.server import Server, ServerConfig

_TEST_CONFIG = ServerConfig(
    host="127.0.0.1",
    port=0,
    max_connections=2,  # Hard-watermark at 2 concurrent connections
    keepalive_timeout=0.5,
    request_timeout=1.0,
    drain_timeout=0.5,
)

@pytest.fixture
def app() -> LingShu:
    return LingShu()

def test_hard_watermark_drops_excess_connections(app: LingShu) -> None:
    """Test that connections exceeding max_connections are immediately dropped."""
    active_handlers = []
    handlers_ready = asyncio.Event()
    handler_resume = asyncio.Event()

    @app.get("/slow")
    async def slow(request: Request) -> Response:
        active_handlers.append(1)
        if len(active_handlers) == 2:
            handlers_ready.set()
        await handler_resume.wait()
        return Response.text("slow_done")

    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()

        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()

        # Connect 1: consumes 1 slot
        reader1, writer1 = await asyncio.open_connection(host, port)
        writer1.write(b"GET /slow HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer1.drain()

        # Connect 2: consumes 1 slot
        reader2, writer2 = await asyncio.open_connection(host, port)
        writer2.write(b"GET /slow HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer2.drain()

        # Wait for both handlers to be scheduled
        await asyncio.wait_for(handlers_ready.wait(), timeout=2.0)

        # Connect 3: should be dropped immediately (exceeds max_connections=2)
        reader3, writer3 = await asyncio.open_connection(host, port)
        # It's possible we can write, but the read should fail (EOF or 503)
        writer3.write(b"GET /slow HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer3.drain()

        # Expecting EOF or safe 503/429 because server dropped connection
        response3 = await reader3.read()

        if response3 != b"":
            resp_text = response3.decode("latin-1")
            assert any(code in resp_text for code in ["503", "429"]), "Must be safe rejection"
            assert "Traceback" not in resp_text

        writer3.close()
        await writer3.wait_closed()

        # Resume the pending handlers to free slots
        handler_resume.set()

        response1 = await reader1.read()
        response2 = await reader2.read()
        assert b"HTTP/1.1 200 OK" in response1
        assert b"HTTP/1.1 200 OK" in response2

        writer1.close()
        await writer1.wait_closed()
        writer2.close()
        await writer2.wait_closed()

        # Connect 4: saturation recovered, slot available
        reader4, writer4 = await asyncio.open_connection(host, port)
        writer4.write(b"GET /slow HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer4.drain()
        response4 = await reader4.read()
        assert b"HTTP/1.1 200 OK" in response4
        writer4.close()
        await writer4.wait_closed()

        await srv.close()

    asyncio.run(run())
