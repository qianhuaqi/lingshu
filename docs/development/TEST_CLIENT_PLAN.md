# Test Client Planning Boundary

Status: P2-05 planning baseline
Issue: #88

## Purpose

This document defines the future test-client direction without implementing a broad testing framework in P2-05.

The future test client should make framework applications easier to test while preserving LingShu's runtime boundaries, cancellation rules, and safe diagnostics.

## Current state

Current tests use direct CLI calls, direct application dispatch, protocol-level tests, and end-to-end TCP integration tests. There is no public `lingshu.testing` test client API yet.

P2-05 may document the plan and validate current examples, but it must not introduce a new broad public testing surface.

## Future test client goals

A future test client should eventually support:

- constructing requests against a frozen `LingShu` app without opening a real TCP listener;
- preserving the same request, response, middleware, routing, exception, scope, and cancellation contracts as the runtime path;
- safe inspection of response status, headers, and body;
- deterministic timeout and cancellation behavior for tests;
- no traceback or secret leakage in client-facing diagnostics;
- clear separation between in-process tests and real TCP integration tests.

## Required design questions before implementation

Before implementation, a later Issue or ADR must decide:

1. whether the test client lives under `lingshu.testing`;
2. whether it dispatches through the application kernel directly or through a protocol-like adapter;
3. how request bodies are represented;
4. how connection metadata and request scope are created;
5. how deadlines and cancellation are exposed to tests;
6. how to avoid diverging from the real server path;
7. which APIs are stable enough to publish.

## Explicit non-goals for P2-05

P2-05 does not implement:

- a public test client class;
- fixture helpers;
- JSON request or response helpers;
- validation helpers;
- dependency injection;
- OpenAPI helpers;
- database, cache, storage, auth, tenant, or RBAC test helpers;
- ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 adapters;
- new runtime dependencies.

## Acceptance for a later implementation Issue

A later implementation Issue should include:

- narrow public API proposal;
- examples that prove the intended developer experience;
- tests comparing test-client behavior with real server behavior;
- cancellation and timeout tests;
- redaction and safe diagnostics tests;
- explicit statement that it does not replace end-to-end TCP integration tests.
