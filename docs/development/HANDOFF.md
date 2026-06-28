# Development Handoff

Updated at: 2026-06-28
Project: LingShu Framework
Phase: P1 - Single-Worker Minimum Vertical Slice
Completed: P1-00 / PR #53
Active Issue: #54
Active Pull Request: #55
Branch: `human/dodo/p1-01-core-foundations`
Primary writer: qianhuaqi / 小顾
Base commit: `689fb411f5d3ed03ad0059ede86bf532541e7249`
Verified implementation commit: `20a089683a6a35d3b8313489af6a0b32f7cc9691`
Status: implementation complete; required CI green; awaiting independent review and project-lead merge

## Implemented

- `WallClock` and `MonotonicClock` protocols with system implementations.
- Strict RFC3339 UTC `format_rfc3339_utc` and `parse_rfc3339_utc`.
- RequestId, ConnectionId, TraceId, OperationId, WorkerId, and RecordId as immutable typed 128-bit lowercase hexadecimal values.
- RevisionId as immutable lowercase SHA-256 canonical Revision identity.
- Secure identifier generation with InternalError cause preservation on entropy failure.
- Bounded external request-correlation validation that remains separate from internal RequestId.
- LingShuError and the frozen category subclasses.
- Lowercase dotted error-code validation.
- Severity and FatalScope bounded enums.
- Recursive safe-details validation and immutable mappings/tuples.
- ProblemDetails allowlist and generic `internal.error` fallback.
- Explicit `lingshu.core` exports while leaving root `lingshu.__all__` empty.
- Unit tests for time, identifiers, safe errors, redaction, control flow, and package-boundary transition.

## Verification

CI run #11 passed all required jobs:

```text
Quality and governance                   success
Build and clean install                  success
Linux Python 3.12                        success
Linux Python 3.13                        success
Linux Python 3.14                        success
Windows Python 3.12                      success
Windows Python 3.14                      success
macOS Python 3.12                        success
macOS Python 3.14                        success
Python 3.15 preview                      success
```

The quality job passed Ruff, format, mypy, pytest, and DCO. The build job passed wheel/sdist construction, artifact inventory, sdist rebuild, clean installation outside checkout, CLI/import smoke tests, and uninstall.

Temporary Ruff diagnostic workflow changes were fully reverted before this handoff. `.github/workflows/ci.yml` has no final P1-01 behavior change.

## Security review points satisfied

- inbound correlation text cannot replace internal RequestId;
- generated identifiers expose no host, PID, timestamp, user, tenant, route, or business meaning;
- secure-source failures catch ordinary `Exception`, not BaseException control flow;
- safe details reject arbitrary objects, bytes, non-string keys, and non-finite floats;
- client Problem Details contain only allowlisted safe values;
- internal causes, traceback, exception repr, paths, and secrets are not serialized;
- no mandatory runtime dependency was added.

## Remaining action

1. independently review PR #55;
2. resolve any blocking finding inside Issue #54 scope;
3. project lead performs final merge;
4. only after merge, create P1-02 and P1-03 from the resulting `main` commit according to the declared parallel wave.

## Protected facts

- root `lingshu` facade remains unchanged;
- configuration and runtime behavior remain deferred;
- archive branch remains untouched;
- public package publication remains unauthorized;
- no auto-merge; final merge belongs to the project lead.
