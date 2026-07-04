# P2 Framework Audit Baseline

Status: draft for Issue #79 / P2-01
Base milestone: P2 after P2-00 roadmap merge
Scope: audit and risk register only

## 1. Purpose

This document records the first P2 framework-level audit for LingShu. It is meant to prevent product direction, risk analysis, and safety requirements from being lost in chat history.

The audit covers:

- security and protocol safety;
- concurrency, cancellation, deadlines, and resource ownership;
- database, cache, storage, and external-resource boundaries;
- server operation and single-worker runtime behavior;
- configuration and toolchain reproducibility;
- Runtime Record, logging, and redaction expectations;
- packaging and supply-chain boundaries;
- developer experience and misuse risks;
- follow-up Issue order.

This document does not authorize implementation of new runtime features. It creates the baseline from which later P2 tasks must be split.

## 2. Current project position

LingShu is a serious pre-alpha framework foundation, not a toy. P1 delivered a minimum single-worker vertical slice with package boundaries, application freeze, request/response primitives, routing, middleware, runtime scopes, a native HTTP/1.1 server, CLI, and packaging evidence.

LingShu is not production-ready. The repository must continue to avoid claims of production readiness, public package publication, or top-tier ecosystem completeness until later release gates are satisfied.

## 3. Severity scale

```text
S0 blocker: must be fixed before any implementation-heavy P2 work.
S1 high: must be scheduled before production-facing or integration-heavy work.
S2 medium: important hardening, can be sequenced after stronger gates exist.
S3 low: documentation, ergonomics, or future improvement.
D deferred: intentionally out of scope until a later Issue/ADR authorizes it.
```

## 4. Security and protocol safety

### Current facts

The P1 server already has explicit configuration limits for connection count, keep-alive count, keep-alive timeout, request timeout, drain timeout, maximum header bytes, and maximum body bytes.

The HTTP/1.1 parser rejects or safely handles a limited protocol subset, including:

- invalid request lines;
- unsupported HTTP versions;
- oversized request target or headers;
- malformed headers;
- `Transfer-Encoding`;
- duplicate `Content-Length`;
- non-numeric or oversized `Content-Length`;
- incomplete body reads;
- handler exceptions that should not expose traceback to the client.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| SEC-01 | S1 | No fuzz corpus for request parser | Parser behavior exists but needs malformed-input matrix and fuzz-style regression tests. | P2-04 server hardening |
| SEC-02 | S1 | Proxy and forwarded-header policy undefined | `X-Forwarded-*`, `Forwarded`, host trust, and client IP trust are not defined. | Later security ADR |
| SEC-03 | S1 | TLS boundary undefined | Native TLS termination and reverse-proxy expectations are not documented. | P2 operations docs or later ADR |
| SEC-04 | S1 | Logging/redaction path is not fully proven end-to-end | Safe client responses exist, but operator logs and runtime records need stronger evidence. | P2-01/P2-04 |
| SEC-05 | S2 | Header normalization and duplicate policy need expanded matrix | `Content-Length` is handled, but broader duplicate-header semantics should be documented. | P2-04 |
| SEC-06 | D | Multipart/form/upload/compression not supported | This is deferred by design and must not be added incidentally. | Future protocol ADR |

### Required rule

New diagnostics must never expose raw request bodies, credentials, local filesystem paths, environment secrets, DSNs, tokens, private stack traces, or protected configuration values.

## 5. Concurrency, cancellation, deadlines, and resource ownership

### Current facts

LingShu has a hierarchical `Scope` model with application, connection, request, and operation ownership levels. Scopes own child scopes, managed tasks, cancellation tokens, deadlines, cleanup callbacks, cleanup budgets, and close reports.

The single-worker server creates an application scope, connection scopes, and request scopes. Request dispatch is guarded by request timeouts. Server drain stops accepting connections, marks active connections as draining, and waits within a configured drain budget.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| CON-01 | S0 | Need a complete leak audit for request-scope cleanup | Future DB/storage work depends on proof that cancellation and close cannot leak scoped resources. | P2-01 audit tests if needed |
| CON-02 | S1 | Disconnect race matrix incomplete | Need tests for client disconnect before headers, during body, during handler, and during response drain. | P2-04 |
| CON-03 | S1 | Writer failure behavior needs explicit contract | `_commit_response` aborts on exceptions, but operator visibility and runtime record linkage need review. | P2-04 |
| CON-04 | S1 | Drain while handlers run needs more evidence | P1 has basic drain coverage, but saturation and timeout combinations need matrix coverage. | P2-04 |
| CON-05 | S1 | Cleanup timeout residue must be observable | Close reports exist, but production-facing operator story is not complete. | P2-04/P2 observability |
| CON-06 | S2 | Admission hard watermark returns EOF by design | EOF is accepted in tests, but operator diagnostics and stable policy need documentation. | P2-04 |

### Required rule

Every future framework-owned background task must be attached to an explicit Scope or explicitly justified by ADR. No hidden global task pools are allowed.

## 6. Database, cache, storage, and external-resource boundaries

### Current facts

LingShu currently has no official database integration, no mandatory database driver, and no runtime dependency for SQL, Redis, storage, or cache.

That is a strength at this stage. It prevents accidental import-time side effects and keeps P1/P2 focused on framework foundations.

### Future integration red lines

Any future database, cache, storage, queue, auth, or tenant integration must satisfy these requirements before implementation:

- no connection pool may be created at import time;
- no hidden global business resource may be created by the framework;
- connection pools must have explicit lifecycle ownership;
- request cancellation must release, close, or roll back scoped resources;
- transaction ownership must be explicit;
- DSNs, credentials, tokens, and tenant identifiers must be protected values;
- cleanup failures must be observable without leaking secrets;
- integrations must not become mandatory runtime dependencies unless explicitly approved;
- each official integration needs its own Issue and usually an ADR.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| DB-01 | S0 | No resource ownership contract for DB integration yet | This must exist before any DB driver or pool is introduced. | Future ADR before DB work |
| DB-02 | S0 | No cancellation-to-rollback rule encoded | Request cancellation must not leave open transactions. | Future DB contract |
| DB-03 | S1 | Protected DSN/credential handling needs stronger config model | Depends on config hardening. | P2-03 |
| DB-04 | D | No DB implementation in P2-01 | Audit only. Do not add drivers, pools, or APIs in this task. | Deferred |

### Required rule

Do not implement DB, cache, storage, auth, tenant, or RBAC during P2 audit or configuration hardening. Define contracts first.

## 7. Server operation and single-worker runtime behavior

### Current facts

The server is intentionally a native single-worker HTTP/1.1 implementation. It is suitable for P1 vertical-slice validation but not a production runtime claim.

The server has startup, drain, close, connection admission, request parsing, request dispatch, and response commit paths.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| SRV-01 | S1 | Readiness/not-ready policy incomplete | Need explicit behavior before startup, during drain, and after close. | P2-04 |
| SRV-02 | S1 | Runtime Record does not yet fully explain server path | Admission, rejection, timeout, disconnect, and close events need record linkage. | P2-04/P2 observability |
| SRV-03 | S1 | Signal behavior is minimal | Production-grade signal matrix is deferred, but P2 should document the boundary. | P2-04 |
| SRV-04 | S1 | No multi-worker supervisor | Deferred by design; must not be mixed into P2-04. | Later ADR |
| SRV-05 | S2 | No reload/watch | Deferred by design. | Later ADR |
| SRV-06 | S2 | No ASGI/WSGI adapter | Deferred by design. | Later ADR |

### Required rule

P2 server work must harden the current single-worker runtime first. Multi-worker, reload/watch, ASGI, WSGI, WebSocket, HTTP/2, and HTTP/3 remain out of scope until later ADRs.

## 8. Configuration and toolchain reproducibility

### Current facts

The package requires Python >=3.12. Runtime dependencies are currently empty. Development dependencies allow broad version ranges, including Ruff.

Local assessment found a risk that newer Ruff versions can require formatting changes that were not part of the accepted baseline.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| CFG-01 | S0 | Toolchain reproducibility is not strict enough | Broad formatter range can create noisy multi-agent diffs. | P2-02 |
| CFG-02 | S1 | Startup config surface needs stronger documentation | CLI/config precedence and protected values need clearer rules. | P2-03 |
| CFG-03 | S1 | Protected config redaction needs end-to-end evidence | Required before DB or external integrations. | P2-03 |
| CFG-04 | D | Config hot reload is not authorized | Must not be implemented in P2-03. | Later ADR |

### Required rule

P2 must lock or narrow development tools before broad implementation work. Formatting churn must not be mixed with feature changes.

## 9. Runtime Record, logging, and redaction

### Current facts

P1 established Runtime Record seeds and redaction primitives. P1 also included tests proving safe client responses and absence of traceback exposure in selected paths.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| OBS-01 | S1 | Runtime Record is not yet complete across server lifecycle | Need records for admission, timeout, cancellation, drain, rejection, handler failure, and cleanup failure. | P2-04 |
| OBS-02 | S1 | Logging integration is not defined | Need safe operator logging without production claims. | P2 observability task |
| OBS-03 | S1 | Secret redaction needs end-to-end review | Especially before config and DB integration. | P2-03 |
| OBS-04 | S2 | Metrics/tracing exporters are not authorized | Define contracts before integrations. | Later ADR |

### Required rule

Observability must explain framework behavior without leaking protected data. External observability integrations are deferred.

## 10. Packaging and supply-chain boundaries

### Current facts

P1 added package build checks and clean-install validation. Production artifacts exclude forbidden development-only content such as tests and examples.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| PKG-01 | S1 | Public package publication remains unauthorized | Need release policy, signing/checksums maybe later. | Later release ADR |
| PKG-02 | S1 | Toolchain pinning affects packaging reproducibility | Build tools should be bounded more deliberately. | P2-02 |
| PKG-03 | S2 | Artifact inventory policy should stay explicit | Avoid accidental examples/tests leakage. | Packaging maintenance |

### Required rule

Do not publish LingShu publicly until project lead explicitly authorizes a release track.

## 11. Developer experience and misuse risks

### Current facts

P1 provides CLI `version`, `check`, and `run --workers 1`, plus a minimal example.

### Confirmed gaps and risks

| ID | Severity | Risk | Notes | Follow-up |
| --- | --- | --- | --- | --- |
| DX-01 | S1 | No test client | Hard to write user-level framework tests. | P2-05 or P3 |
| DX-02 | S1 | JSON and validation ergonomics are minimal | Response supports text/bytes primitives; full JSON/DTO/OpenAPI is future work. | P3 |
| DX-03 | S2 | Error pages/debug mode undefined | Must be safe by default. | P2-05/P3 |
| DX-04 | S2 | Extension guidance limited | Need docs before ecosystem grows. | P2-05 |
| DX-05 | D | FastAPI-style DI/OpenAPI not P2 default | Requires explicit future Issue/ADR. | P3/P4 |

### Required rule

Developer convenience must not bypass safety, scope ownership, or governance.

## 12. Immediate blocker list

Before implementation-heavy P2 work proceeds, these must be handled or explicitly accepted by project lead:

1. P2-02 toolchain reproducibility must prevent format churn across agents.
2. P2-03 config hardening must define protected values and startup config behavior.
3. P2-04 server hardening must expand disconnect, drain, timeout, and malformed-input coverage.
4. Future DB work must wait for a resource ownership ADR.

## 13. Follow-up Issue order

Recommended order after this audit:

```text
P2-02: Toolchain reproducibility and Ruff baseline
P2-03: Static configuration hardening and protected-value evidence
P2-04: Single-worker server operational hardening
P2-05: Developer ergonomics, examples, and test client planning
P3: JSON/content negotiation, typed request/response ergonomics, validation surface
P4: official integration contracts for DB/cache/storage/auth
P5: production runtime track and release readiness
```

## 14. Explicit deferrals

The audit does not authorize:

- database driver or connection pool implementation;
- SQL, Redis, cache, storage, auth, tenant, or RBAC integration;
- OpenAPI;
- dependency injection;
- multi-worker supervisor;
- reload/watch;
- ASGI or WSGI adapters;
- WebSocket, HTTP/2, or HTTP/3;
- public package publication;
- production-readiness claims;
- new mandatory runtime dependencies.

## 15. Exit condition for P2-01

P2-01 is complete when:

- this audit baseline is merged into `main`;
- the audit distinguishes current facts from future requirements;
- follow-up work is sequenced;
- no runtime feature expansion is included;
- CI passes with the existing governance checks.
