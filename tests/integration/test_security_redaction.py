"""Security and redaction integration tests for the LingShu framework."""

import asyncio

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

def test_unhandled_exception_does_not_leak_details(app: LingShu) -> None:
    """Test that a handler raising an exception does not leak details in the response."""
    @app.get("/error")
    async def cause_error(request: Request) -> Response:
        raise RuntimeError("SUPER_SECRET_INTERNAL_ERROR_DETAIL")

    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        
        reader, writer = await asyncio.open_connection(host, port)
        
        writer.write(b"GET /error HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer.drain()
        
        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()
        
        resp_text = response_data.decode("latin-1")
        assert "HTTP/1.1 500" in resp_text
        assert "SUPER_SECRET_INTERNAL_ERROR_DETAIL" not in resp_text
        assert "RuntimeError" not in resp_text
        
        await srv.close()
        
    asyncio.run(run())

def test_oversized_header_safe_rejection(app: LingShu) -> None:
    """Test that an oversized header is rejected safely without leaking parser state."""
    async def run() -> None:
        app.freeze()
        srv = Server(app, _TEST_CONFIG)
        await srv.startup()
        
        assert srv._server is not None
        sock = srv._server.sockets[0]
        host, port = sock.getsockname()
        
        reader, writer = await asyncio.open_connection(host, port)
        
        # Max headers bytes is bounded (8192 usually), we send a very large one
        big_header = b"X-Secret: " + (b"A" * 70000) + b"\r\n"
        writer.write(b"GET / HTTP/1.1\r\nHost: localhost\r\n" + big_header + b"\r\n")
        await writer.drain()
        
        response_data = await reader.read()
        writer.close()
        await writer.wait_closed()
        
        resp_text = response_data.decode("latin-1")
        assert "HTTP/1.1 431" in resp_text
        # Ensure nothing from the big header is echoed back
        assert "X-Secret" not in resp_text
        assert "AAAAA" not in resp_text
        
        await srv.close()
        
    asyncio.run(run())
