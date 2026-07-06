# Database Layer Architecture

Status: P5-04 foundation
Issue: #124

## 1. Why `lingshu.db` comes before MySQL

P5-04 establishes a shared database-layer foundation before any concrete MySQL,
Redis, or MongoDB package is implemented. The foundation gives later data
extensions a common configuration, driver, resource, lifecycle, and manager
contract while keeping core free of database client dependencies.

Starting with `lingshu.db` keeps the first implementation step narrow:

- no database driver is imported;
- no socket is opened;
- no database connection is attempted;
- no application lifecycle integration is added;
- no mandatory runtime dependency is introduced.

## 2. Relationship to backend packages

`lingshu.db` is the shared contract layer. Future packages such as
`lingshu.db.mysql`, Redis, or MongoDB integrations are consumers of this
foundation, not hidden requirements of it.

Later backend packages may provide concrete `DatabaseDriver` implementations and
backend-specific resource factories. They must still follow the P4 extension
boundary, lifecycle contract, redaction contract, and packaging policy.

## 3. Contract boundaries

`DatabaseConfig` stores resource metadata and sensitive connection inputs. Its
`repr` and `safe_details` expose only coarse diagnostics.

`DatabaseDriver` is a protocol for async startup and shutdown. It does not
define query, pooling, migration, ORM, ODM, or connection-string behavior.

`DatabaseResource` binds a config to a driver and owns the lifecycle boundary.
Registration is inert. Startup may acquire resources. Shutdown releases anything
startup acquired.

`DatabaseManager` is a small registry with `register(resource)`, `get(name)`,
and `names()`. It does not couple to `Application` and does not inject `app.db`.

## 4. Resource naming

Database resources use lowercase dotted names:

```text
db.<backend>.<name>
```

Examples:

```text
db.mysql.main
db.redis.cache
db.mongodb.main
```

Names identify resources for registration and diagnostics. They are not network
locations, credentials, or database names.

## 5. Import safety and redaction

Importing `lingshu.db` must not:

- open sockets;
- read remote state;
- connect to a database;
- import MySQL, Redis, or MongoDB client libraries;
- mutate global application state.

`DatabaseConfig.safe_details` may expose only coarse fields such as resource
name, backend kind, and whether sensitive fields were configured. DSNs,
usernames, passwords, tokens, host credentials, database names, schema names,
and query text must not appear in `repr`, logs, or `safe_details`.

## 6. Why `app.db` is out of scope

P5-04 intentionally does not add `app.db`, Application lifecycle wiring, or
extension registration helpers. Those changes affect the public application
surface and lifecycle ordering, so they require a later issue that can review
integration behavior directly.

## 7. Future backend integration

Future MySQL, Redis, and MongoDB work can integrate by:

- defining a backend-specific `DatabaseDriver`;
- constructing a `DatabaseConfig` with redacted diagnostics;
- wrapping both in a `DatabaseResource`;
- registering resources in a `DatabaseManager`;
- connecting only during startup and releasing resources during shutdown.

Those backend tracks must not make their client libraries mandatory
dependencies of core.
