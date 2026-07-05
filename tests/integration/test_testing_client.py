"""Integration tests for the async TestClient."""

import asyncio
from typing import cast

import pytest
from lingshu import LingShu, Request, Response
from lingshu.core.errors import FatalScope, RequestError
from lingshu.testing import TestClient


@pytest.fixture
def app() -> LingShu:
    return LingShu()


def test_get_dispatch(app: LingShu) -> None:
    @app.get("/hello")
    async def hello(request: Request) -> Response:
        return Response.text("Hello World")

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.get("/hello")

            assert response.status == 200
            assert response.text == "Hello World"
            assert response.headers.get("content-type") == "text/plain; charset=utf-8"

    asyncio.run(run())


def test_post_byte_body(app: LingShu) -> None:
    @app.post("/echo")
    async def echo(request: Request) -> Response:
        body = await request.body.read()
        return Response.bytes(body)

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.post("/echo", body=b"raw bytes")

            assert response.status == 200
            assert response.body == b"raw bytes"
            assert response.headers.get("content-type") == "application/octet-stream"

    asyncio.run(run())


def test_headers_and_duplicates(app: LingShu) -> None:
    @app.get("/headers")
    async def check_headers(request: Request) -> Response:
        return Response.text(
            ",".join(request.headers.get_all("x-test")),
            headers=[("X-Response", "first"), ("x-response", "second")],
        )

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.get("/headers", headers=[("x-test", "a"), ("X-Test", "b")])

            assert response.status == 200
            assert response.text == "a,b"
            assert response.headers.get_all("x-response") == ("first", "second")

    asyncio.run(run())


def test_path_parameters(app: LingShu) -> None:
    @app.get("/users/{user_id}")
    async def get_user(request: Request) -> Response:
        return Response.text(f"User {request.path_params['user_id']}")

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.get("/users/123")

            assert response.status == 200
            assert response.text == "User 123"

    asyncio.run(run())


def test_middleware_order(app: LingShu) -> None:
    calls: list[str] = []

    @app.add_middleware
    async def mw1(request: Request, call_next: object) -> Response:
        calls.append("mw1_in")
        from lingshu.http.middleware import Next

        response = await cast(Next, call_next)()
        calls.append("mw1_out")
        return response

    @app.add_middleware
    async def mw2(request: Request, call_next: object) -> Response:
        calls.append("mw2_in")
        from lingshu.http.middleware import Next

        response = await cast(Next, call_next)()
        calls.append("mw2_out")
        return response

    @app.get("/test")
    async def test(request: Request) -> Response:
        calls.append("handler")
        return Response.text("ok")

    async def run() -> None:
        async with TestClient(app) as client:
            await client.get("/test")

            assert calls == ["mw1_in", "mw2_in", "handler", "mw2_out", "mw1_out"]

    asyncio.run(run())


def test_request_body_single_consumer(app: LingShu) -> None:
    @app.post("/consume")
    async def consume(request: Request) -> Response:
        await request.body.read()
        try:
            await request.body.read()
            return Response.text("failed", status=500)
        except RequestError as exc:
            assert exc.code == "request.body_already_consumed"
            assert exc.fatal_scope == FatalScope.REQUEST
            return Response.text("consumed")

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.post("/consume", body=b"data")
            assert response.status == 200
            assert response.text == "consumed"

    asyncio.run(run())


def test_safe_diagnostics(app: LingShu) -> None:
    @app.get("/fail")
    async def fail(request: Request) -> Response:
        raise ValueError("internal secret")

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.get("/fail")
            assert response.status == 500
            assert response.text == "Internal Server Error"
            assert "internal secret" not in response.text

    asyncio.run(run())


def test_request_cancellation(app: LingShu) -> None:
    """Test BaseException cancellation propagates out of the test client."""

    @app.get("/cancel")
    async def cancel(request: Request) -> Response:
        raise asyncio.CancelledError()

    async def run() -> None:
        async with TestClient(app) as client:
            with pytest.raises(asyncio.CancelledError):
                await client.get("/cancel")

    asyncio.run(run())


def test_query_string_routing(app: LingShu) -> None:
    """Test that requests with query strings route correctly by parsed path."""

    @app.get("/search")
    async def search(request: Request) -> Response:
        assert request.target.path == "/search"
        assert request.target.query == "q=abc"
        return Response.text("found")

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.get("/search?q=abc")
            assert response.status == 200
            assert response.text == "found"

    asyncio.run(run())


def test_not_found(app: LingShu) -> None:
    """Test 404 behavior."""

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.get("/missing")
            assert response.status == 404
            assert response.text == "Not Found"

    asyncio.run(run())


def test_method_not_allowed(app: LingShu) -> None:
    """Test 405 behavior."""

    @app.get("/only-get")
    async def only_get(request: Request) -> Response:
        return Response.text("ok")

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.post("/only-get")
            assert response.status == 405
            assert response.text == "Method Not Allowed"
            assert response.headers.get("allow") == "GET"

    asyncio.run(run())
