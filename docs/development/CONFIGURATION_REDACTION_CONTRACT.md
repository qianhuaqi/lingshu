# Configuration Redaction Contract for Extensions

Status: draft for P4-04 review  
Context: Issue #110

This contract is the behavioral boundary for configuration handling in P4-04 and later extension work. It defines the baseline redaction rules that already exist in the current framework and records the minimum extension obligations before any data or identity extension code lands.

## 1. Core primitives this contract assumes

P4-04 does not define new redaction runtime types; it requires extension code to use existing baseline types:

- `RedactionClass`: disclosure categories (`PUBLIC`, `INTERNAL`, `SENSITIVE`, `SECRET`).
- `SecretRef`: runtime reference helper for deferred secret material.
- `SecretValue`: immutable wrapper for sensitive strings whose `__str__` and `__repr__` are redacted.
- `ConfigField.redaction`: schema-level redaction declaration for configuration fields.
- `ConfigSnapshot.redacted(...)`: redacted config projection API.
- `LingShuError.safe_details`: client-visible safe diagnostics.
- `freeze_safe_details`: detail freezing helper used by diagnostics.

## 2. Confidential configuration definition

Within this contract, configuration is confidential when disclosure changes the security posture of credentials, external identity, transport trust, or private service access.

Confidential configuration includes, at minimum:

- credentials (`password`, `secret`, `api_key`, `private_token`, etc.);
- connection strings with embedded credentials;
- signing material and symmetric keys;
- any value whose disclosure is not explicitly intended for user-facing output.

Confidential data must be treated as non-public regardless of its position in memory, logs, config merge, or exception context.

## 3. Default-deny and allowlist diagnostics model

P4-04 uses an explicit allowlist model:

- Any value without an explicit redaction assignment is treated as sensitive from a diagnostics perspective unless contract text proves otherwise.
- `ConfigField.redaction` is the source of truth for extension schema fields.
- Diagnostics and summaries should only expose values that are known `PUBLIC`.
- For `INTERNAL` and `SENSITIVE`, extension implementations should avoid printing raw values and prefer redacted metadata.
- For `SECRET`, exposure is only permitted through `SecretValue` redacted rendering or scoped `.reveal()` call at use time.

## 4. Safe representation rules for `PUBLIC`, `INTERNAL`, `SENSITIVE`, `SECRET`

### PUBLIC

- Can be printed in user-facing output.
- Can appear in `repr`, structured logs, handoff summaries, and PR summaries.

### INTERNAL

- Intended for internal operator workflows.
- Should not be used in public diagnostics, and extension summaries should prefer metadata over raw output.

### SENSITIVE

- Must be masked in user-facing logs, `repr`, exception messages, diagnostics, and docs examples.
- May appear only in non-sensitive metadata forms (field names, key ids, redaction marker).

### SECRET

- Must be represented by `SecretValue` or equivalent deferred-value semantics.
- Must never be shown in cleartext in user-facing outputs.
- `.reveal()` usage is for runtime action only and must not persist plaintext values in diagnostics state.

## 5. Relationship to `ConfigSnapshot.redacted(...)`

Extension configuration flows must use `ConfigSnapshot.redacted(...)` before any output that leaves extension internals, including:

- startup logs and lifecycle reports;
- config snapshots shown in diagnostics;
- handoff summaries that include extension fields.

`ConfigSnapshot.redacted(...)` is the canonical baseline path for reducing leakage risk.

## 6. Relationship to `LingShuError.safe_details` and `freeze_safe_details`

- Extension errors exposed through `LingShuError.safe_details` MUST pass through redaction-safe structures.
- `freeze_safe_details` must be used for any extension-provided detail payloads that can reach clients.
- `SECRET` values must not be inserted into `safe_details` as cleartext.
- If an extension does not have a safe redacted representation for a field, that field must be omitted or replaced with a redacted placeholder.

## 7. Rules for nested structures and arbitrary mappings

Nested configuration objects are common (`dict`, `list`, and mixed trees). P4-04 requires:

- redaction policy follows declared config schema paths;
- unknown keys in nested structures are treated as non-public by default;
- when redacting mappings manually, extension code must avoid recursive leakage through implicit `str()`/`repr()` of containers;
- only redacted projections should be logged or emitted from error metadata.

This prevents accidental disclosure from free-form fields that bypass field-level schema declarations.

## 8. Rules for logs, exception messages, `repr`, PR summaries, handoff summaries, and documentation examples

For all of the above surfaces:

- field names are allowed, value content is not unless explicitly `PUBLIC`;
- exception messages must not call `.reveal()` for message content;
- `__repr__` for extension objects must not include raw confidential values;
- PR and handoff summaries must use placeholder values for confidential fields.

Docs examples involving sensitive fields should show synthetic placeholders only (for example `<redacted>`).

## 9. Resource lifecycle safe metadata rules

For extension resources participating in startup/shutdown:

- lifecycle metadata MUST avoid raw secret-bearing values;
- startup/shutdown summaries should expose only extension identifiers and redacted configuration metadata;
- `ConfigSnapshot.redacted(...)` is the default input for any lifecycle record surfaced in diagnostics.

These rules are consistent with [Resource Lifecycle Contract](./RESOURCE_LIFECYCLE_CONTRACT.md).

## 10. P5 extension testing expectations

Before later extension tracks can be accepted, implementations that depend on this contract should include tests for:

- schema-level redaction declarations for sensitive fields;
- redacted snapshot emission;
- safe-details emission without secret leakage;
- representation output checks for logs/repr/diagnostics;
- lifecycle diagnostics that include redacted metadata only.

## 11. Explicit non-goals

- no new concrete extension implementations (Redis/MySQL/MongoDB/identity);
- no secret manager or vault integration;
- no new runtime dependency class introduced in this P4 scope;
- no public package publication or extension binary distribution changes under P4-04.
