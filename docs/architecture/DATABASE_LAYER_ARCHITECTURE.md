# Database Layer Architecture

Status: P5-06 minimal MySQL driver boundary
Issue: #128

## 1. Why `lingshu.db` comes before backend drivers

P5-04 established a shared database-layer foundation before any concrete MySQL,
Redis, or MongoDB package is implemented. P5-05 wired that foundation into the
LingShu application lifecycle through a minimal `app.db` developer API while
keeping core free of mandatory database client dependencies.

Starting with `lingshu.db` keeps the foundation narrow:

- no database driver is imported by `lingshu.db`;
- no socket is opened;
- no database connection is attempted;
- registration is inert and tied into existing application extension lifecycle;
- no mandatory runtime dependency is introduced.

## 2. Relationship to backend packages

`lingshu.db` is the shared contract layer. Future packages such as
`lingshu.db.mysql`, Redis, or MongoDB integrations are consumers of this
foundation, not hidden requirements of it.

Backend packages provide their own `DatabaseDriver` implementation and optional
dependency activation strategy, then produce backend-bound `DatabaseResource`
instances.

## 3. Contract boundaries

`DatabaseConfig` stores resource metadata and sensitive connection inputs. Its
`repr` and `safe_details` expose only coarse diagnostics.

`DatabaseDriver` is a protocol for async startup and shutdown. It does not
define query execution, pooling, migration, ORM, ODM, or policy behavior.

`DatabaseResource` binds a config to a driver and owns the lifecycle boundary.
Registration is inert. Startup may acquire resources. Shutdown releases anything
startup acquired.

`DatabaseManager` is a small registry with `register(resource)`, `get(name)`, and
`names()`. `LingShu.db` exposes the application-owned manager for developer code.
It is not an ORM, connection pool, query builder, or permission boundary.

`LingShu.add_database_resource(resource, *, dependencies=())` is the
configuration-time registration entry point. It registers the resource as an
application extension using the resource name as the extension name. Registration
is inert and does not call `resource.startup()` or `driver.startup()`.

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

Importing `lingshu.db` or `lingshu.db.mysql` must not:

- open sockets;
- read remote state;
- connect to a database;
- import real database client libraries as required dependencies;
- mutate global application state.

`DatabaseConfig.safe_details` may expose only coarse fields such as resource
name, backend kind, and whether sensitive fields were configured. DSNs,
usernames, passwords, tokens, host credentials, database names, schema names,
and query text must not appear in `repr`, logs, or `safe_details`.

## 6. Application lifecycle boundary

P5-05 added the minimal `app.db` boundary:

- `app.db` is a `DatabaseManager`;
- `add_database_resource()` is allowed only during configuration;
- database resources start through existing application extension startup;
- database resources shut down through existing reverse extension shutdown;
- startup rollback and shutdown suppress-and-continue behavior remain owned by
  the existing application lifecycle.

## 7. Minimal MySQL driver integration (P5-06)

P5-06 adds `lingshu.db.mysql` with:

- `MySQLDriver` implementing the shared `DatabaseDriver` protocol;
- `make_mysql_resource(config, *, driver=...)` helper for registered resources;
- registration-inert behavior preserved through `LingShu.add_database_resource()`;
- startup/shutdown call points that use optional dependency `aiomysql`.

Dependency policy:

- `lingshu.db.mysql` is import-safe and may be imported even when `aiomysql`
  is absent.
- `aiomysql` is only loaded when startup attempts to establish a MySQL handle.
- a focused `DatabaseConfigurationError` is raised when dependency is missing.

`shutdown` attempts to close acquired handles and is wrapped by existing resource
lifecycle error handling.

## 8. Future backend integration

Redis, MongoDB, and other backends consume the same contract boundary with:

- their own `DatabaseDriver`;
- backend-specific `DatabaseConfig` construction conventions;
- `DatabaseResource` registration and application lifecycle integration;
- optional dependencies activated only at runtime path.

Backends must continue to keep secret redaction and failure semantics at the
`DatabaseConfig`, `DatabaseResource`, and `DatabaseError` contract boundary.

