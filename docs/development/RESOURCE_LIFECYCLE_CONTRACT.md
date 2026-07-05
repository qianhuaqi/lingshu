# Application Resource Lifecycle Contract

Status: draft for P4-03 review
Context: Issue #108

## 1. Goal

Define the lifecycle contract for application-owned resources (e.g., database connection pools, message brokers, remote clients). This contract defines resource registration, startup, failure handling, cleanup, shutdown, and safe diagnostics, without providing concrete protocol implementations.

## 2. Application-Owned Resources

An application-owned resource is a stateful component whose lifecycle (initialization, steady state, and termination) is strictly bound to the `Application` lifecycle. 
It must:
- Be registered during `ApplicationState.CONFIGURING`.
- Initialize network connections or heavy allocations during `Application.startup()`.
- Cleanly release handles, sockets, and memory during `Application.shutdown()`.

## 3. Registration and Freeze Limits

- Resources are registered through the `ExtensionContribution` mechanism via `app.add_extension(...)`.
- Resource registration must occur before the application is frozen.
- Once `app.freeze()` is called, no new resources can be registered. The application compiles a deterministic `ExtensionLifecyclePlan`.

## 4. Startup and Shutdown Order

- **Startup**: Resource startup hooks execute serially in the topological order of their extension dependencies. A resource can safely assume its declared dependencies are fully started and available.
- **Shutdown**: Resource shutdown hooks execute serially in the exact reverse topological order of startup.

## 5. Partial Startup Failure and Cleanup

If any resource startup hook fails:
- The current baseline rolls back successfully started extensions in reverse startup order by calling their shutdown hooks with individual shutdown exceptions suppressed.
- The started-extension list is cleared, the application state returns to `ApplicationState.FROZEN`, and the original startup exception is re-raised.
- Later Issues may define a distinct failed/stopping state if needed.

## 6. Shutdown Failures

If a shutdown hook fails during `Application.shutdown()`:
- The current baseline suppresses individual shutdown-hook exceptions while continuing best-effort cleanup.
- The shutdown sequence continues to execute remaining extension shutdown hooks and application shutdown hooks.
- The application clears the started-extension list and transitions to `ApplicationState.STOPPED` after the best-effort shutdown pass.
- P4-03 does not implement grouped shutdown failure reporting, shutdown-failure logging, or a configurable cleanup deadline budget.
- A later authorized issue may add grouped reporting, diagnostics, or cleanup deadline enforcement.

## 7. Fatal Scopes, Diagnostics, and Redaction

- If a resource encounters an unrecoverable state (e.g., a connection pool is permanently broken), it can signal a failure using `FatalScope.WORKER` or `FatalScope.SUPERVISOR` via `LingShuError`.
- Diagnostics exposed by resources must comply with `lingshu.core.errors.freeze_safe_details`.
- Resources must strictly redact sensitive configurations (e.g., passwords, connection string tokens) before including them in error messages, logs, or diagnostics.

## 8. Cancellation and Deadlines

- Resource operations must respect runtime `Scope` deadlines and `CancellationToken`.
- Blocking I/O within a resource must be bounded by the current `Scope`'s remaining deadline.
- When a `Scope` is cancelled (e.g., due to a client disconnect or timeout), the resource must abort pending operations gracefully and return the connection to the pool without leaking.

## 9. Relationship to Existing Hooks

- `app.add_extension(...)`: The primary entry point for resource registration.
- `startup_hook` / `shutdown_hook`: Resources utilize the existing application startup and shutdown hook abstractions provided by `ExtensionContribution`. Resources must not invent their own ad-hoc lifecycle mechanisms.

## 10. Testing Requirements for Future P5 Data Extensions

Future concrete extensions (P5) that implement this contract must include tests verifying that:
- Startup delays or failures are handled gracefully.
- Shutdown cleanly releases all external handles and connections.
- Deadlines and cancellations are respected under simulated latency.
- Credentials are never leaked in exception traces or diagnostics.

## 11. Non-Goals and Blocked Tracks

- Concrete implementations (e.g., Redis, MySQL, MongoDB, Identity) are explicitly out of scope.
- Multi-worker orchestration, process supervision, and reload/watch mechanisms are deferred.
- Adapter integrations (ASGI/WSGI) and public package publication are blocked until P4-05.
