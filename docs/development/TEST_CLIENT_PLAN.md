# Test Client Implementation Decision

Status: P3-04 decision for Issue #98
Previous baseline: P2-05 planning document for Issue #88

## 1. Purpose

This document turns the P2-05 test-client planning boundary into a concrete P3-04 decision.

P3 accepts a narrow future public test client direction, but P3-04 does not implement it.
The implementation should be handled by a later focused issue after this contract is on
`main`.

## 2. Current baseline

Current tests use:

- direct CLI calls;
- direct application dispatch;
- protocol-level tests;
- end-to-end TCP integration tests against the native single-worker server.

There is still no public `lingshu.testing` API in P3-04.

The current TCP tests remain important because they exercise the native parser, server,
connection handling, request body handling, and response commit path. A future in-process
client must not replace those tests.

## 3. Decision

Accept a future public test client under:

```python
from lingshu.testing import TestClient
```

The first implementation should be async-only:

```python
async with TestClient(app) as client:
    response = await client.request("GET", "/hello")
```

Convenience helpers may be added only as thin wrappers after `request(...)` is stable:

```python
await client.get("/hello")
await client.post("/items", body=b"payload")
```

No synchronous wrapper is accepted for the first implementation. A sync wrapper can be
considered later only if it does not hide event-loop ownership or cancellation behavior.

## 4. Dispatch strategy

The first test client should dispatch through the application kernel in-process rather than
opening a real TCP listener.

Rationale:

- it keeps developer tests fast and deterministic;
- it avoids allocating ports;
- it exercises routing, middleware, handler contracts, response normalization, request body
  consumption, path parameters, scopes, and safe diagnostics;
- it clearly complements, rather than replaces, TCP integration tests.

Risk:

- it does not exercise HTTP parsing, connection keep-alive, wire formatting, socket errors,
  or native server shutdown behavior.

Mitigation:

- document this limitation in the public test-client docs;
- keep real TCP integration tests for protocol and server behavior;
- add comparison tests for shared request/response behavior where practical.

## 5. Request construction contract

A future `TestClient.request(...)` should construct the same public `Request` type used by
the server path.

Required construction pieces:

- `HTTPMethod` from the provided method string;
- `RequestTarget.parse(...)` from the provided target path/query string;
- `HTTPVersion.HTTP_1_1` as the initial in-process version;
- immutable `Headers` built from explicit caller-provided header tuples;
- `RequestBody.from_bytes(...)` for byte bodies;
- generated `RequestId` and `ConnectionId` values;
- `ConnectionInfo` with deterministic test metadata;
- application, connection, and request scopes with bounded deadlines.

The first implementation should accept byte bodies only. Text, JSON, form, and multipart
request helpers are deferred until request-body ergonomics are implemented in a separate
issue.

## 6. Response capture contract

The test client response object should be a testing facade, not a replacement for runtime
`Response`.

Required captured fields:

- `status`: integer HTTP status;
- `headers`: immutable `Headers` view;
- `body`: response bytes.

Allowed convenience properties after the base facade is stable:

- `text`, decoded as UTF-8 by default;
- `json()`, only after request/response JSON helper policy is stable.

The first implementation should not expose mutable runtime response internals after commit.

## 7. Error behavior

The test client must preserve current safe diagnostic boundaries:

- handler return contract errors should surface as deterministic test failures or captured
  framework responses according to the same kernel behavior used today;
- client-visible errors must not include tracebacks or secrets;
- unexpected internal errors must not expose raw exception text through client-visible
  response bodies.

A later implementation issue must define the exact exception/captured-response split before
writing code.

## 8. Required tests for implementation

The implementation issue must include focused tests for:

- basic GET route dispatch;
- POST byte body dispatch;
- headers and duplicate-header behavior;
- path parameter propagation;
- middleware order;
- response status, headers, and body capture;
- request body single-consumer behavior;
- safe diagnostics for client-visible and hidden errors;
- deadline/cancellation behavior at the request-scope level;
- at least one behavior comparison with a real TCP integration test.

## 9. Explicit non-goals

P3-04 does not add:

- a public `lingshu.testing` module;
- a `TestClient` implementation;
- fixture helpers;
- synchronous wrappers;
- JSON request helpers;
- form or multipart helpers;
- browser automation;
- ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 adapters;
- OpenAPI helpers;
- validation helpers;
- dependency injection;
- database, cache, storage, auth, tenant, or RBAC test helpers;
- new mandatory runtime dependencies;
- production-readiness claims.

## 10. Exit condition

P3-04 exits when this decision is merged.

A later implementation issue may introduce the narrow async `lingshu.testing.TestClient`
only if it follows the contracts in this document and keeps CI green.
