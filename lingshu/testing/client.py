"""Async test client for in-process application testing."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from lingshu.core.application import ApplicationState, LingShu
from lingshu.core.identifiers import ConnectionId, RequestId
from lingshu.http.body import RequestBody
from lingshu.http.message import Headers, HTTPMethod, HTTPVersion, RequestTarget
from lingshu.http.request import ConnectionInfo, Request
from lingshu.runtime import Scope, ScopeKind


@dataclass(frozen=True, slots=True)
class TestResponse:
    """Safe test facade capturing a dispatched Response.

    This facade prevents tests from modifying the runtime Response object
    after dispatch and provides test-friendly convenience properties.
    """

    status: int
    headers: Headers
    body: bytes

    @property
    def text(self) -> str:
        """Decode the captured body bytes as UTF-8 text."""

        return self.body.decode("utf-8")


class TestClient:
    """In-process async test client for dispatching requests to a LingShu application.

    The TestClient bypasses protocol parsing and socket handling. It executes the native
    application kernel pipeline, providing high-fidelity routing, middleware, parameter,
    and diagnostic coverage without allocating ports or dropping fast test determinism.

    This client is exclusively asynchronous. It starts application lifecycle during
    ``__aenter__`` and cleanly drains and shuts down the application during ``__aexit__``.
    """

    __test__ = False
    __slots__ = ("_app", "_app_scope")

    def __init__(self, app: LingShu) -> None:
        self._app = app
        self._app_scope: Scope | None = None

    async def __aenter__(self) -> TestClient:
        if self._app.state in (ApplicationState.CREATED, ApplicationState.CONFIGURING):
            self._app.freeze()
        if self._app.state == ApplicationState.FROZEN:
            await self._app.startup()

        self._app_scope = Scope.application()
        await self._app_scope.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self._app_scope is not None:
            await self._app_scope.__aexit__(exc_type, exc_val, exc_tb)
            self._app_scope = None

        if self._app.state in (ApplicationState.RUNNING, ApplicationState.DRAINING):
            await self._app.shutdown()

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Iterable[tuple[str | bytes, str | bytes]] | None = None,
        body: bytes = b"",
    ) -> TestResponse:
        """Construct and dispatch an in-process Request to the application."""

        if self._app_scope is None:
            raise RuntimeError("TestClient must be used as an async context manager.")

        # Prepare HTTP metadata types.
        http_method = HTTPMethod(method)
        target = RequestTarget.parse(path)
        http_version = HTTPVersion.HTTP_1_1
        request_headers = Headers(headers or ())

        # Scopes.
        conn_scope = self._app_scope.create_child(ScopeKind.CONNECTION)

        # We manually close the Connection scope at the end of this request because the TestClient
        # doesn't maintain persistent connections.
        async with conn_scope:
            req_scope = conn_scope.create_child(ScopeKind.REQUEST, duration_ns=60_000_000_000)

            async with req_scope:
                request_body = RequestBody.from_bytes(
                    body,
                    scope=req_scope,
                    max_bytes=max(len(body), 1048576) if body else 1048576,
                )

                request = Request(
                    method=http_method,
                    target=target,
                    version=http_version,
                    headers=request_headers,
                    scope=req_scope,
                    body=request_body,
                    request_id=RequestId.generate(),
                    connection_id=ConnectionId.generate(),
                    connection_info=ConnectionInfo(local="testclient", peer="testclient"),
                )

                response = await self._app.dispatch(http_method.value, target.path, request)

                return TestResponse(
                    status=response.status,
                    headers=response.headers,
                    body=response.body,
                )

    async def get(
        self,
        path: str,
        *,
        headers: Iterable[tuple[str | bytes, str | bytes]] | None = None,
    ) -> TestResponse:
        """Dispatch a GET request."""

        return await self.request("GET", path, headers=headers)

    async def post(
        self,
        path: str,
        *,
        headers: Iterable[tuple[str | bytes, str | bytes]] | None = None,
        body: bytes = b"",
    ) -> TestResponse:
        """Dispatch a POST request."""

        return await self.request("POST", path, headers=headers, body=body)


__all__ = ("TestClient", "TestResponse")
