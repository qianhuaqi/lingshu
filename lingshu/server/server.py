"""Single-worker HTTP/1.1 Server."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from lingshu.core.time import SystemMonotonicClock
from lingshu.runtime.scope import Scope, ScopeKind
from lingshu.server.config import ServerConfig
from lingshu.server.protocol import HttpConnection

if TYPE_CHECKING:
    from lingshu.core.application import LingShu


class Server:
    """Native single-worker HTTP/1.1 Server."""

    __slots__ = ("_app", "_app_scope", "_clock", "_config", "_connections", "_server")

    def __init__(self, app: LingShu, config: ServerConfig) -> None:
        self._app = app
        self._config = config
        self._clock = SystemMonotonicClock()
        self._app_scope: Scope | None = None
        self._server: asyncio.Server | None = None
        self._connections: set[HttpConnection] = set()

    async def startup(self) -> None:
        """Bind listener and transition application to running."""
        if self._server is not None:
            return

        self._app_scope = Scope.application(clock=self._clock)
        await self._app.startup()

        try:
            self._server = await asyncio.start_server(
                self._handle_connection,
                host=self._config.host,
                port=self._config.port,
                limit=self._config.max_headers_bytes + 2,
            )
        except Exception:
            await self._app.shutdown()
            if self._app_scope is not None:
                await self._app_scope.close()
                self._app_scope = None
            raise

    async def drain(self) -> None:
        """Stop accepting connections and allow active ones to finish."""
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        await self._app.drain()

        # Mark all connections as draining so they don't accept new requests on keep-alive
        for conn in self._connections:
            conn.drain()

        # Wait for connections to close within drain budget
        if self._connections:
            try:
                async with asyncio.timeout(self._config.drain_timeout):
                    while self._connections:
                        await asyncio.sleep(0.01)
            except TimeoutError:
                for conn in tuple(self._connections):
                    conn.close()

    async def close(self) -> None:
        """Idempotently close the server and application."""
        if self._server is not None:
            self._server.close()
            import contextlib

            with contextlib.suppress(Exception):
                await self._server.wait_closed()
            self._server = None

        for conn in tuple(self._connections):
            conn.close()

        import contextlib

        with contextlib.suppress(Exception):
            await self._app.shutdown()

        if self._app_scope is not None:
            with contextlib.suppress(Exception):
                await self._app_scope.close()
            self._app_scope = None

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle an incoming TCP connection."""
        if len(self._connections) >= self._config.max_connections:
            writer.close()
            return

        assert self._app_scope is not None
        conn_scope = self._app_scope.create_child(ScopeKind.CONNECTION)

        conn = HttpConnection(self._app, self._config, conn_scope, reader, writer)
        self._connections.add(conn)
        try:
            async with conn_scope:
                await conn.serve()
        finally:
            self._connections.discard(conn)


async def serve(app: LingShu, config: ServerConfig) -> None:
    """Run the server until interrupted."""
    server = Server(app, config)
    try:
        await server.startup()
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await server.drain()
        await server.close()


__all__ = ("Server", "serve")
