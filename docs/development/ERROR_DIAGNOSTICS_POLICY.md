# Error Diagnostics Policy

Status: P3-03 policy for Issue #96

## 1. Objective

P3-03 clarifies how LingShu separates developer-facing diagnostics from client-visible
error responses.

The goal is to make framework failures easier to reason about without weakening the current
safety boundary. Client-visible diagnostics must remain generic unless an error explicitly
marks allowlisted fields as safe.

## 2. Current baseline

The current error stack already has these boundaries:

- `LingShuError` stores a stable dotted `code`, `safe_message`, `safe_details`, severity,
  retryability, HTTP status, and `fatal_scope`.
- `safe_details` are recursively validated and frozen; arbitrary objects, bytes,
  non-string mapping keys, and non-finite floats are rejected.
- `internal_cause` and Python exception causes are retained only for internal diagnostics.
- `ProblemDetails` serializes only allowlisted fields.
- `problem_from_exception(...)` maps non-client-visible framework errors and unexpected
  ordinary exceptions to a generic `internal.error` response.
- `HTTPException` is the accepted explicit application-level client-visible error path.
- native protocol parsing failures use short generic text responses such as `Bad Request`
  or `Internal Server Error`.
- CLI commands catch broad application/server failures and print fixed safe messages rather
  than tracebacks or raw exception text.

## 3. Diagnostic audiences

LingShu treats diagnostics as audience-specific.

### Client-visible diagnostics

Client-visible diagnostics are the bytes returned to an HTTP client. They may include only:

- a generic status reason from the protocol path;
- a `ProblemDetails` document created from a client-visible error;
- allowlisted safe fields from `safe_message` and `safe_details`;
- request identifiers that are already designed for correlation.

Client-visible diagnostics must not include:

- tracebacks;
- file paths;
- environment variables;
- request bodies;
- raw exception reprs;
- internal causes;
- secrets, tokens, passwords, keys, cookies, or authorization values.

### Developer-facing diagnostics

Developer-facing diagnostics are CLI messages, logs, docs, and test failure messages intended
for application developers or maintainers.

They should be clearer than client-visible diagnostics, but they still must not print secrets,
tracebacks, raw request bodies, or arbitrary exception text by default.

## 4. Error classification principles

Use the narrowest stable error category available:

- `ProtocolError` for malformed or unsupported protocol input.
- `RequestError` for invalid request-scoped contracts.
- `HandlerContractError` for invalid handler signatures or return values.
- `ConfigurationError` for configuration loading or validation failures.
- `ResourceLimitError` for configured limit enforcement.
- `LifecycleError` for invalid lifecycle transitions.
- `InternalError` for framework invariant failures.
- `HTTPException` for intentional application-level client-visible responses.

Fatal scope must describe the smallest owner that must fail: operation, request,
connection, worker, or supervisor.

## 5. Safe details policy

`safe_details` are not a shortcut for dumping context. They are an allowlisted, structured,
client-eligible map.

Allowed values are:

- strings;
- integers;
- finite floats;
- booleans;
- `None`;
- lists or tuples of safe values;
- mappings from string keys to safe values.

Never place secrets, raw headers, raw bodies, stack frames, exception reprs, or arbitrary
objects in `safe_details`.

## 6. Client-visible problem policy

A framework error becomes client-visible only when it is explicitly marked `client_visible`
and has an HTTP status.

All other framework errors, even if they contain a `safe_message`, map to generic
`internal.error` when converted to `ProblemDetails`. This prevents accidental exposure of
internal contract, routing, configuration, or runtime details.

## 7. CLI wording policy

CLI output should remain deterministic and safe:

- target-resolution errors may describe the invalid target shape;
- application validation failures should not print tracebacks by default;
- invalid server configuration should use a fixed safe message;
- runtime server failures should use a fixed safe message;
- unsupported multi-worker mode should remain explicit and deterministic.

## 8. Explicit non-goals

P3-03 does not add:

- broad exception middleware;
- OpenAPI error schemas;
- validation framework integration;
- dependency injection;
- database, cache, storage, auth, tenant, or RBAC integration;
- new client error formats;
- production logging backends;
- mandatory runtime dependencies;
- production-readiness claims.

## 9. Future work

A later issue may improve developer ergonomics further by adding structured logging or richer
internal diagnostics. That work must define a separate redaction policy and prove that
client-visible outputs remain generic and safe.
