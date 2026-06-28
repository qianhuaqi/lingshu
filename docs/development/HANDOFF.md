# Development Handoff

Updated at: 2026-06-28
Project: LingShu Framework
Phase: P1 - Single-Worker Minimum Vertical Slice
Completed: P1-00 / PR #53
Active Issue: #54
Branch: `human/dodo/p1-01-core-foundations`
Primary writer: qianhuaqi / 小顾
Base commit: `689fb411f5d3ed03ad0059ede86bf532541e7249`
Current implementation commit: `5b6b06600fe603083e4e1c0bad9666bc8b0d3c65`
Status: Core provider implementation written; CI and independent review pending

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
- Unit tests for time, identifiers, safe errors, redaction, and package-boundary transition.

## Review focus

- confirm distinct identifier classes remain unequal even with identical text;
- confirm entropy failure catches Exception, never BaseException control flow;
- confirm timestamp parsing is intentionally strict `Z` only;
- confirm safe details cannot retain mutable source mappings/sequences;
- confirm hidden causes/messages never enter Problem Details;
- confirm P1-01 does not prematurely define HTTPException or HTTP response policy;
- confirm Core exports do not create import-time side effects.

## Checks not yet claimed

No CI result is claimed yet for this branch. Required evidence must come from the P1-01 workflow run and any reviewer-requested focused test.

## Next action

1. open the P1-01 Pull Request;
2. inspect every CI job;
3. correct failures only inside Issue #54 scope;
4. obtain independent review;
5. project lead merges;
6. only then open P1-02 and P1-03 according to the declared parallel wave.

## Protected facts

- no mandatory runtime dependency was added;
- root `lingshu` facade remains unchanged;
- configuration and runtime behavior remain deferred;
- archive branch remains untouched;
- no auto-merge; final merge belongs to the project lead.
