# Static Configuration and Diagnostics

Status: P2-03 baseline
Issue: #84

## Purpose

LingShu configuration remains static at startup. P2-03 does not authorize hot reload, env-file loaders, external configuration services, database settings, or production-readiness claims.

This document records the safe diagnostics rules for configuration work.

## Current server configuration rule

The native single-worker server is configured with `ServerConfig`.

`ServerConfig` validates:

- host is a non-empty, bounded, control-free string;
- port is an integer in the TCP port range;
- connection and byte limits are positive integers;
- timeouts are finite numbers with the documented positive or non-negative bounds.

Invalid server configuration must produce safe CLI diagnostics and must not echo raw user input.

## Diagnostic disclosure classes

Server bind host and port are public diagnostics.

Server limits and timeout values are internal diagnostics. They are redacted by default and can be included only through an explicit internal diagnostic path.

## CLI behavior

`lingshu run` validates server configuration before starting the server. If configuration is invalid, the CLI returns a usage error and prints only:

```text
Error: invalid server configuration
```

The CLI must not print a traceback, raw host value, filesystem path, token, DSN, credential, or other unreviewed value from the invalid input.

## Non-goals

P2-03 does not authorize:

- config hot reload;
- env-file parsing;
- external config services;
- database, cache, storage, auth, tenant, RBAC, or OpenAPI configuration;
- new runtime dependencies;
- multi-worker, reload/watch, ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 work;
- public package publication;
- production-readiness claims.
