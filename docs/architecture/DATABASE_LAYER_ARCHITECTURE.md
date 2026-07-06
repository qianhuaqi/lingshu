# Database Layer Architecture

Status: P5-05 application lifecycle boundary
Issue: #126

## 1. Why `lingshu.db` comes before MySQL

P5-04 established a shared database-layer foundation before any concrete MySQL,
Redis, or MongoDB package is implemented. P5-05 wires that foundation into the
LingShu application lifecycle through a minimal `app.db` developer API while
keeping core free of database client dependencies.

Starting with `lingshu.db` keeps the first implementation step narrow:

- no database driver is imported;
- no socket is opened;
- no database connection is attempted;
- application lifecycle integration is limited to inert registration plus
  startup/shutdown hooks;
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
and `names()`. `LingShu.db` exposes the application-owned manager for developer
code. It is not an ORM, connection pool, query builder, or permission boundary.

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

## 6. Application lifecycle boundary

P5-05 adds the minimal `app.db` boundary:

- `app.db` is a `DatabaseManager`;
- `add_database_resource()` is allowed only during configuration;
- database resources start through existing application extension startup;
- database resources shut down through existing reverse extension shutdown;
- startup rollback and shutdown suppress-and-continue behavior remain owned by
  the existing application lifecycle.

P5-05 still does not implement real database drivers, connection pools, ORM,
ODM, query builders, migrations, database permissions, or untrusted plugin
isolation.

## 7. Future backend integration

Future MySQL, Redis, and MongoDB work can integrate by:

- defining a backend-specific `DatabaseDriver`;
- constructing a `DatabaseConfig` with redacted diagnostics;
- wrapping both in a `DatabaseResource`;
- registering resources with `LingShu.add_database_resource()`;
- connecting only during startup and releasing resources during shutdown.

Those backend tracks must not make their client libraries mandatory
dependencies of core.
