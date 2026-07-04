# Request Body Ergonomics Plan

Status: P3-02 planning contract for Issue #94

## 1. Objective

P3-02 defines the safe next step for request body ergonomics and content-type handling.

This document does not implement a new request parser. It records the current baseline,
accepted near-term shape, required tests, and explicit exclusions so a later implementation
cannot accidentally expand into validation, OpenAPI, dependency injection, or broad content
negotiation.

## 2. Current baseline

The current public request surface is intentionally small:

- `Request.body` exposes a `RequestBody` object.
- `RequestBody.read(max_bytes=None)` buffers the body exactly once within configured and
  caller-provided byte limits.
- `RequestBody.iter_chunks()` streams chunks exactly once without exposing an unbounded
  buffer.
- consuming a body twice raises `request.body_already_consumed`.
- body chunks must be bytes-like values.
- body reads preserve scope checks and configured resource-limit behavior.
- headers are immutable, duplicate-preserving, and case-insensitive.
- headers support `get`, `get_all`, `contains`, `items`, iteration, and length.

There is no accepted public helper yet for:

- JSON request parsing;
- text decoding;
- form parsing;
- multipart parsing;
- content negotiation;
- schema validation;
- automatic handler argument binding.

## 3. P3 meaning of request body ergonomics

For P3, request body ergonomics means reducing boilerplate for common request-body reads
without changing the framework's safety boundaries.

An acceptable helper must be:

- explicit at the call site;
- bounded by existing body limits;
- single-consumer, matching `RequestBody.read()` semantics;
- deterministic about decoding and error behavior;
- implemented with the Python standard library only;
- safe in diagnostics;
- covered by focused tests before it is accepted as public API.

P3 ergonomics does not mean automatic parsing based on handler annotations, broad content
negotiation, OpenAPI generation, validation, or dependency injection.

## 4. Content-type handling contract

P3 may add narrow content-type inspection helpers before adding parsers.

Allowed near-term shape:

- read normalized headers through the existing immutable `Headers` object;
- inspect `content-type` using `request.headers.get("content-type")`;
- document that a parser helper may require an exact media type match or an explicitly
  accepted media-type family;
- treat missing `content-type` as a deterministic caller-visible parsing error for helpers
  that require one;
- keep duplicate `content-type` behavior explicit before adding parser helpers.

Deferred behavior:

- no `Accept` negotiation system;
- no automatic response format selection;
- no weighted media-range parser;
- no charset negotiation framework;
- no multipart parser;
- no form parser unless a later issue defines exact limits and behavior.

## 5. Candidate future API shapes

The recommended next implementation issue should choose one narrow path.

### Option A: `RequestBody.json(...)`

Possible shape:

```python
value = await request.body.json(max_bytes=None)
```

Advantages:

- naturally attaches parsing to the single-consumer body object;
- mirrors the existing `RequestBody.read()` ownership boundary;
- avoids implying that `Request` performs automatic parsing.

Required decisions before implementation:

- whether `content-type` is checked by this method or by a `Request`-level wrapper;
- whether the result type is `object` or a documented JSON value alias;
- which exception code is used for invalid JSON;
- whether empty bodies are invalid JSON or return `None`;
- whether non-UTF-8 input is rejected with a deterministic request error.

### Option B: `Request.json(...)`

Possible shape:

```python
value = await request.json(max_bytes=None)
```

Advantages:

- shorter for application developers;
- gives direct access to headers for content-type checks.

Risks:

- may imply broader automatic request parsing;
- may hide the single-consumer body contract unless the docs and tests are explicit.

### Recommendation

Defer implementation in P3-02. Use a later issue for a narrow `Request.json(...)` or
`RequestBody.json(...)` helper after the exact API and error taxonomy are approved.

P3-02 should remain a planning and contract task because JSON request parsing touches:

- body consumption semantics;
- content-type interpretation;
- text decoding;
- safe error classification;
- type expectations for parsed JSON values.

## 6. Required tests for a later JSON helper

A later helper implementation must cover at least:

- valid JSON object body returns a parsed value;
- UTF-8 non-ASCII content is accepted;
- invalid JSON raises a deterministic request-scoped error;
- body can only be consumed once;
- helper respects configured body limits and caller `max_bytes`;
- missing or wrong `content-type` behavior matches the accepted contract;
- existing `RequestBody.read()` and `iter_chunks()` behavior remains unchanged;
- no traceback, secret, or internal diagnostic leaks to client-visible surfaces.

## 7. Explicit non-goals

P3-02 does not add:

- request-body helper implementation;
- broad content negotiation;
- schema validation;
- OpenAPI generation;
- dependency injection;
- handler parameter binding;
- form or multipart parsing;
- database, cache, storage, auth, tenant, or RBAC integration;
- multi-worker, reload/watch, ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 support;
- mandatory runtime dependencies;
- production-readiness claims.

## 8. Exit decision

P3-02 exits with this planning contract only.

The next implementation issue may introduce a narrow request JSON helper if it defines:

- the exact public method name and location;
- content-type requirements;
- byte and decoding limits;
- error codes and safe details;
- focused tests;
- documentation updates;
- no new mandatory runtime dependency.
