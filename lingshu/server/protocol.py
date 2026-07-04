"""HTTP/1.1 protocol parsing and connection handling."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from lingshu.core.errors import ProtocolError, ResourceLimitError
from lingshu.core.identifiers import ConnectionId, RequestId
from lingshu.http.body import RequestBody
from lingshu.http.message import Headers, HTTPMethod, HTTPVersion, RequestTarget
from lingshu.http.request import ConnectionInfo, Request
from lingshu.http.response import Response
from lingshu.runtime.deadline import Deadline
from lingshu.runtime.scope import ScopeKind

if TYPE_CHECKING:
    from lingshu.core.application import LingShu
    from lingshu.runtime.scope import Scope
    from lingshu.server.config import ServerConfig


class HttpConnection:
    """Manages a single HTTP/1.1 connection."""

    __slots__ = (
        "_app",
        "_closed",
        "_config",
        "_conn_scope",
        "_connection_info",
        "_draining",
        "_reader",
        "_requests_handled",
        "_writer",
    )

    def __init__(
        self,
        app: LingShu,
        config: ServerConfig,
        conn_scope: Scope,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self._app = app
        self._config = config
        self._conn_scope = conn_scope
        self._reader = reader
        self._writer = writer
        self._requests_handled = 0
        self._draining = False
        self._closed = False

        peername = writer.get_extra_info("peername")
        sockname = writer.get_extra_info("sockname")
        self._connection_info = ConnectionInfo(
            peer=str(peername) if peername else None,
            local=str(sockname) if sockname else None,
            secure=writer.get_extra_info("sslcontext") is not None,
        )

    def drain(self) -> None:
        """Mark connection as draining, will close after current request."""
        self._draining = True

    def close(self) -> None:
        """Immediately close the connection."""
        if not self._closed:
            self._closed = True
            self._writer.close()

    async def serve(self) -> None:
        """Process requests on this connection sequentially."""
        try:
            while not self._closed and not self._draining:
                if self._requests_handled >= self._config.max_keepalive_requests:
                    break

                try:
                    request_line_coro = self._reader.readuntil(b"\r\n")
                    raw_request_line = await asyncio.wait_for(
                        request_line_coro, timeout=self._config.keepalive_timeout
                    )
                except TimeoutError:
                    break
                except asyncio.IncompleteReadError as e:
                    if not e.partial:
                        break  # Client closed connection cleanly
                    break  # Client disconnected midway
                except Exception:
                    break

                if len(raw_request_line) > self._config.max_headers_bytes:
                    await self._send_error(414, "URI Too Long")
                    break

                self._requests_handled += 1

                try:
                    # Parse request line
                    line = raw_request_line.decode("ascii").rstrip("\r\n")
                    parts = line.split(" ")
                    if len(parts) != 3:
                        await self._send_error(400, "Bad Request")
                        break

                    method_str, target_str, version_str = parts

                    if version_str == "HTTP/1.0":
                        version = HTTPVersion.HTTP_1_0
                    elif version_str == "HTTP/1.1":
                        version = HTTPVersion.HTTP_1_1
                    else:
                        await self._send_error(505, "HTTP Version Not Supported")
                        break

                    method = HTTPMethod(method_str)
                    target = RequestTarget.parse(
                        target_str, max_bytes=self._config.max_headers_bytes
                    )

                    # Parse headers
                    raw_headers = []
                    headers_size = 0
                    while True:
                        try:
                            header_line = await asyncio.wait_for(
                                self._reader.readuntil(b"\r\n"),
                                timeout=self._config.request_timeout,
                            )
                        except TimeoutError:
                            await self._send_error(408, "Request Timeout")
                            return

                        headers_size += len(header_line)
                        if headers_size > self._config.max_headers_bytes:
                            await self._send_error(431, "Request Header Fields Too Large")
                            return

                        if header_line == b"\r\n":
                            break

                        header_line = header_line.rstrip(b"\r\n")
                        if b":" not in header_line:
                            await self._send_error(400, "Bad Request")
                            return

                        name, value = header_line.split(b":", 1)
                        raw_headers.append((name, value))

                    headers = Headers(raw_headers, max_total_bytes=self._config.max_headers_bytes)

                    # Connection close handling
                    connection_header = (headers.get("connection") or "").lower()
                    is_http_1_0 = version == HTTPVersion.HTTP_1_0
                    if connection_header == "close" or (
                        is_http_1_0 and connection_header != "keep-alive"
                    ):
                        self.drain()

                    # Handle body
                    content_length_str = headers.get("content-length")
                    body_bytes = b""
                    if content_length_str:
                        try:
                            content_length = int(content_length_str)
                            if content_length < 0:
                                raise ValueError
                        except ValueError:
                            await self._send_error(400, "Bad Request")
                            break

                        if content_length > self._config.max_body_bytes:
                            await self._send_error(413, "Content Too Large")
                            break

                        if content_length > 0:
                            try:
                                body_bytes = await asyncio.wait_for(
                                    self._reader.readexactly(content_length),
                                    timeout=self._config.request_timeout,
                                )
                            except TimeoutError:
                                await self._send_error(408, "Request Timeout")
                                break
                            except asyncio.IncompleteReadError:
                                break

                    # Dispatch request
                    await self._dispatch_request(method, target, version, headers, body_bytes)

                except ProtocolError:
                    await self._send_error(400, "Bad Request")
                    break
                except ResourceLimitError as exc:
                    if exc.code == "request.target_too_large":
                        await self._send_error(414, "URI Too Long")
                    else:
                        await self._send_error(431, "Request Header Fields Too Large")
                    break
                except Exception:
                    await self._send_error(500, "Internal Server Error")
                    break

        finally:
            self.close()

    async def _dispatch_request(
        self,
        method: HTTPMethod,
        target: RequestTarget,
        version: HTTPVersion,
        headers: Headers,
        body_bytes: bytes,
    ) -> None:
        timeout_ns = int(self._config.request_timeout * 1_000_000_000)
        req_deadline = Deadline.after(timeout_ns, self._conn_scope.clock)
        req_scope = self._conn_scope.create_child(ScopeKind.REQUEST, deadline=req_deadline)

        async with req_scope:
            request_body = RequestBody.from_bytes(
                body_bytes,
                scope=req_scope,
                max_bytes=self._config.max_body_bytes,
            )

            request = Request(
                method=method,
                target=target,
                version=version,
                headers=headers,
                scope=req_scope,
                body=request_body,
                request_id=RequestId.generate(),
                connection_id=ConnectionId.generate(),  # use generated ID
                connection_info=self._connection_info,
            )

            try:
                response = await self._app.kernel.dispatch(method.value, target.path, request)
            except asyncio.CancelledError:
                raise
            except Exception:
                # Should not happen as dispatch handles exceptions, but just in case
                response = Response.text("Internal Server Error", status=500)

            await self._commit_response(response, version)

    async def _commit_response(self, response: Response, version: HTTPVersion) -> None:
        try:
            head = response.commit()

            # Write status line
            status_line = f"{version.value} {head.status} {self._reason_phrase(head.status)}\r\n"
            lines = [status_line.encode("ascii")]

            # Write headers
            for name, value in head.headers:
                lines.append(f"{name}: {value}\r\n".encode("latin-1"))

            if self._draining and not head.headers.contains("connection"):
                lines.append(b"connection: close\r\n")

            lines.append(b"\r\n")

            self._writer.writelines(lines)

            # Write body
            if response.body:
                self._writer.write(response.body)

            await self._writer.drain()
            response.complete()
        except asyncio.CancelledError:
            response.abort()
            raise
        except Exception:
            response.abort()

    async def _send_error(self, status: int, reason: str) -> None:
        """Send a basic error response and close connection."""
        if self._closed:
            return
        try:
            body = f"{status} {reason}".encode("ascii")
            lines = [
                f"HTTP/1.1 {status} {reason}\r\n".encode("ascii"),
                b"connection: close\r\n",
                b"content-type: text/plain\r\n",
                f"content-length: {len(body)}\r\n\r\n".encode("ascii"),
                body,
            ]
            self._writer.writelines(lines)
            await self._writer.drain()
        except Exception:
            pass
        finally:
            self.drain()

    def _reason_phrase(self, status: int) -> str:
        # A minimal mapping for common status codes
        reasons = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            408: "Request Timeout",
            413: "Content Too Large",
            414: "URI Too Long",
            431: "Request Header Fields Too Large",
            500: "Internal Server Error",
            505: "HTTP Version Not Supported",
        }
        return reasons.get(status, "Unknown")
