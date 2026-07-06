# Redis Extension Contract

Status: draft for P5-01 review
Context: Issue #116

## 1. Purpose

This document defines the Redis data-extension track for LingShu. It records the
contract boundary the eventual Redis extension must satisfy without implementing a
Redis client in `lingshu` core.

## 2. Scope

P5-01 is document-first. A minimal import-safe skeleton is optional and only
appropriate if later work needs a testable public surface.

This track does not:

- implement Redis runtime behavior;
- add a mandatory Redis dependency to `lingshu` core;
- require network I/O at import time;
- publish a public package;
- claim production readiness or performance characteristics.

## 3. Package Boundary

The eventual official Redis extension package is expected to follow the P4
extension boundary and packaging policy:

- core integration remains through `app.add_extension(...)`;
- any later helper must stay contract-oriented and import-safe;
- the extension package must not depend on `lingshu` internals that are not
  already part of the accepted public extension contracts;
- the core package must stay free of new mandatory runtime dependencies.

The future package name is expected to be `lingshu-redis`, but this issue does
not require publishing or installing that package.

## 4. Configuration Contract

The Redis extension should accept a small configuration schema that can be
projected into redacted diagnostics before any output leaves extension internals.

Suggested configuration fields:

- `url` or equivalent connection locator;
- `host`;
- `port`;
- `username`;
- `password`;
- `database`;
- `tls_enabled`;
- `connect_timeout_ms`;
- `pool_size`;
- `name`.

Redaction rules:

- connection strings are never shown in `repr`, logs, or `safe_details`;
- passwords, tokens, host credentials, and database indexes are never shown in
  `repr`, logs, or `safe_details`;
- any field that can reveal private connection topology must be treated as
  non-public for diagnostics;
- safe diagnostics may include only coarse labels such as extension name,
  backend kind, and other non-sensitive operational markers.

## 5. Lifecycle Contract

The Redis extension must follow the accepted P4 lifecycle rules:

- registration happens before application freeze through `app.add_extension(...)`;
- import-time and registration-time code must not open sockets or fetch remote
  state;
- startup owns connection establishment;
- shutdown owns cleanup and release of any acquired handles;
- startup and shutdown ordering follows the dependency order from the core
  extension plan;
- lifecycle failures must use the accepted safe-details and redaction rules.

## 6. Diagnostics Contract

Redis extension diagnostics must remain safe by default:

- `ConfigSnapshot.redacted(...)` is the required projection for lifecycle
  reports, handoff summaries, and other externally visible diagnostics;
- `safe_details` payloads must remain frozen and redaction-safe;
- `repr` output must not expose connection strings, passwords, tokens, host
  credentials, or database indexes;
- retries, reconnects, and pool state may be described only at a coarse level
  that does not reveal private connection material.

## 7. Non-Goals

- no full Redis client;
- no production connection pooling;
- no Redis Cluster support;
- no Redis Sentinel support;
- no MySQL or MongoDB implementation;
- no identity/access implementation;
- no OpenAPI implementation;
- no multi-worker support;
- no reload or watch support;
- no ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 adapter work;
- no public package publication;
- no new core mandatory runtime dependencies;
- no import-time network calls;
- no production-ready or performance claims.

## 8. P5-01 Acceptance Shape

P5-01 is complete when the Redis track is documented clearly enough that later
implementation work can stay inside the accepted P4 contracts.

If a later issue needs a public surface, the smallest possible skeleton should:

- stay import-safe;
- stay contract-oriented;
- avoid runtime behavior beyond what the contract needs for tests;
- keep all sensitive connection data redacted in diagnostics.
