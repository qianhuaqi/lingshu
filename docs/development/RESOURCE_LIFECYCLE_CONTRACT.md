# Application Resource Lifecycle Contract

Status: draft for P4-03 review
Context: Issue #108

## 1. Goal

Define the lifecycle contract for application-owned resources (e.g., database connection pools, message brokers, remote clients). This contract covers registration, startup, failure handling, cleanup, shutdown, and safe diagnostics, without providing concrete protocol implementations.

## 2. Application-Owned Resources

An application-owned resource is a stateful component whose lifecycle (initialization, steady state, and termination) is strictly bound to the `Application` lifecycle. It must:

- be registered during `ApplicationState.CONFIGURING`;
- initialize network connections or heavy allocations during `Application.startup()`;
- release handles, sockets, and memory during `Application.shutdown()`.

## 3. Registration and Freeze Limits

- Resources are registered through the `ExtensionContribution` mechanism via `app.add_extension(...)`.
- Resource registration must occur before the application is frozen.
- Once `app.freeze()` is called, no new resources can be registered. The application compiles a deterministic `ExtensionLifecyclePlan`.

## 4. Startup and Shutdown Order

- **Startup**: resource startup hooks execute serially in topological dependency order.
- **Shutdown**: resource shutdown hooks execute serially in reverse topological order.

## 5. Partial Startup Failure and Cleanup

If any startup hook fails:

- previously started extensions are rolled back in reverse startup order by invoking shutdown hooks with individual exceptions suppressed;
- the started list is cleared;
- the application returns to `ApplicationState.FROZEN`;
- the original startup exception is re-raised.

## 6. Shutdown Failures

If a shutdown hook fails during `Application.shutdown()`:

- individual shutdown exceptions are suppressed for continuation;
- remaining extensions still receive shutdown;
- the started list is cleared;
- the application transitions to `ApplicationState.STOPPED`.

## 7. Fatal Scopes, Diagnostics, and Redaction

If a resource encounters unrecoverable failure, it may signal through `LingShuError` using `FatalScope` values.

Diagnostics must observe redaction safety:

- `freeze_safe_details` is required for safe client-exposed detail payloads.
- Sensitive resource metadata must come from redacted config output and not from runtime plaintext.

## 8. Cancellation and Deadlines

- Resource operations should respect runtime scope deadlines and cancellation tokens.
- Blocking I/O should be bounded by remaining deadlines.
- On cancellation, operations should abort safely and release resources.

## 9. Resource-safe metadata and redaction requirements

Extension resources that carry configuration-derived metadata in lifecycle events must:

- avoid storing plaintext secrets in started-resource state;
- emit only redacted metadata in lifecycle logs and summaries;
- route config field reporting through `ConfigSnapshot.redacted(...)` and `CONFIGURATION_REDACTION_CONTRACT.md`.

## 10. Relationship to Existing Hooks

- `app.add_extension(...)`: primary entry for resource registration.
- `startup_hook` / `shutdown_hook`: lifecycle execution points.

## 11. Testing Requirements for P5 Data Extensions

Concrete P5 resources must test:

- startup failures and rollback cleanup;
- graceful shutdown under simulated contention;
- deadline and cancellation behavior;
- redaction-safe diagnostics for lifecycle event metadata.

## 12. Non-Goals and Blocked Tracks

- concrete implementations (Redis, MySQL, MongoDB, Identity);
- multi-worker orchestration and process supervision;
- reload/watch and adapter integrations (ASGI/WSGI);
- public package publication before P4-05.
