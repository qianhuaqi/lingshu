# P0 Hardening Checklist

This checklist preserves the hardening requirements that existed on the archived branch. It is not a second Blueprint. Every accepted item must be merged into `LINGSHU_FRAMEWORK_BLUEPRINT.md` before P0 freeze.

## Required topics

1. Unified time model
   - system time for display only;
   - monotonic time for deadlines, timeout, scheduling, and duration.
2. Standard identifiers
   - request ID;
   - connection ID;
   - trace ID;
   - operation ID.
3. Exception semantics
   - retryable;
   - client visible;
   - system fatal;
   - sensitive-record handling.
4. Configuration versioning
   - schema version;
   - fail-fast mismatch;
   - explicit migration;
   - validate, prepare, swap, rollback reload flow.
5. Serialization rules
   - RFC3339 datetime;
   - base64 bytes;
   - null semantics;
   - reject NaN and infinity;
   - explicit streaming format.
6. Async context isolation
   - explicit request-context propagation;
   - detached background tasks;
   - cleanup at scope end;
   - no request context retained by singletons.
7. Telemetry standard fields
   - request ID;
   - trace and span IDs;
   - duration;
   - status and error code;
   - component.
8. Worker resource budgets
   - memory;
   - active requests;
   - connections;
   - request-record disk usage;
   - event queue size;
   - explicit backpressure or rejection when limits are reached.

## Freeze rule

P0 cannot be accepted until these requirements are integrated into the single authoritative Blueprint and reviewed for consistency with the greenfield architecture.
