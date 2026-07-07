# LingShu V1 / V2 / V3 Delivery Plan

Project: LingShu Framework
Owner: 多多
Planner / PM: 小顾
Status: active delivery plan

## 0. Delivery principle

LingShu 的后续推进只按可交付能力判断，不再按边界、审计、阶段叙事判断进展。

每个版本必须回答四个问题：

1. 业务开发者能不能直接用？
2. 有没有稳定 API？
3. 有没有测试证明它能跑？
4. 有没有减少后续业务项目开发成本？

如果一个工作项没有产生可调用 API、可运行示例、测试或项目模板，它只能算辅助工作，不能算主进展。

## 1. Three-version target

三个版本内，LingShu 必须从“有地基的框架”变成“可以支撑内部后台/API 项目的框架”。

最终必须具备：

- database：数据库访问、事务、SQLite、本地开发、MySQL 业务使用入口；
- cache：内存缓存、Redis 缓存、app.cache 使用入口；
- openapi：接口文档 JSON 和浏览器文档页；
- upload：multipart 文件上传、本地保存、大小限制；
- auth：登录、token、当前用户；
- rbac：角色、权限、接口权限校验；
- app integration：app.db、app.cache、request.user 等业务使用方式；
- examples：basic API 示例和 admin 示例；
- cli：项目生成、启动、检查、路由查看、数据库初始化；
- tests：模块测试、集成测试、模板生成测试、admin 全链路测试。

## 2. Version layout

```text
V1: Capability completion
V2: CLI and project generation
V3: Testing, stability, and acceptance hardening
```

V1 先把业务必需能力补齐。
V2 再把项目生成和开发体验补齐。
V3 最后把测试、稳定性和验收链路补扎实。

## 3. Role split

### 小顾 owns

- version planning;
- issue writing;
- acceptance criteria;
- PR title and PR body;
- final documentation;
- review and merge recommendation;
- follow-up task split.

### Developer owns

- implementation code;
- tests;
- validation commands;
- short factual handoff report.

Developer should not spend time writing long planning documents. Planning and final documentation are PM work.

## 4. V1: Capability completion

### 4.1 V1 goal

V1 must make LingShu usable for a real backend/API service without relying on external project glue.

A developer must be able to write:

```python
@app.get("/users")
async def list_users(request):
    rows = request.app.db.query("select id, name from users")
    return {"data": rows}
```

A developer must be able to write:

```python
@app.get("/me")
@require_login
async def me(request):
    return request.user
```

A developer must be able to write:

```python
@app.post("/assets")
@require_permission("asset:create")
async def create_asset(request):
    return {"ok": True}
```

### 4.2 V1 module list

V1 includes these modules:

1. `lingshu.database`
2. `lingshu.cache`
3. `lingshu.openapi`
4. `lingshu.upload`
5. `lingshu.auth`
6. `lingshu.rbac`
7. app integration: `app.db`, `app.cache`, `request.user`
8. examples: `examples/basic_api`, `examples/admin`

### 4.3 V1-01 database module

Current primary issue: #146

#### Goal

Create a real database API for LingShu.

#### Public API target

```python
from lingshu.database import Database

db = Database.sqlite("dev.db")
db.execute("create table users (id integer primary key, name text)")
db.execute("insert into users (name) values (?)", ("dodo",))
rows = db.query("select id, name from users")
one = db.query_one("select id, name from users where id = ?", (1,))
```

Transaction target:

```python
with db.transaction():
    db.execute("insert into users (name) values (?)", ("dodo",))
```

Async project compatibility may be added through an adapter or future async wrapper, but the V1 local SQLite path must be directly usable and testable.

#### Implementation plan

Implement package:

```text
lingshu/database/
  __init__.py
  config.py
  errors.py
  protocol.py
  database.py
  sqlite.py
  mysql.py
```

Minimum objects:

```text
DatabaseConfig
Database
DatabaseAdapter protocol
SQLiteAdapter
MySQLAdapter or MySQLDatabase wrapper over existing lingshu.db.mysql boundary
DatabaseError
DatabaseConnectionError
DatabaseExecutionError
DatabaseTransactionError
```

Required behavior:

- `Database.sqlite(path)` returns a usable local database object.
- `Database.mysql(config or url)` exposes the existing MySQL boundary through a cleaner public entry.
- `execute(sql, params=None)` executes DDL/DML.
- `query(sql, params=None)` returns list-like rows.
- `query_one(sql, params=None)` returns one row or `None`.
- `transaction()` commits on success and rolls back on exception.
- `close()` closes owned connection resources.
- errors are converted to stable LingShu database errors.

Row format:

- V1 should return dict-like rows for business convenience where practical.
- SQLite should use `sqlite3.Row` and convert to plain dicts or expose a stable row object.

#### Tests

Add tests proving:

- create table;
- insert;
- query;
- query_one;
- update;
- delete;
- transaction commit;
- transaction rollback;
- close behavior;
- error wrapping for invalid SQL.

Suggested test files:

```text
tests/database/test_sqlite_database.py
tests/database/test_transaction.py
tests/database/test_database_errors.py
```

#### Acceptance

- `Database.sqlite(...)` works without external dependencies.
- existing MySQL boundary remains compatible.
- no mandatory external database service is required for default tests.
- ruff, format check, mypy, pytest pass.

### 4.4 V1-02 app.db and DATABASE_URL

#### Goal

Make database access natural inside a LingShu app.

#### Public API target

```python
from lingshu import LingShu
from lingshu.database import Database

app = LingShu()
app.db = Database.sqlite("dev.db")

@app.get("/users")
async def users(request):
    return {"data": request.app.db.query("select id, name from users")}
```

Configuration target:

```text
DATABASE_URL=sqlite:///dev.db
```

#### Implementation plan

Add or standardize:

```text
app.db registration / injection
Database.from_url(...)
DatabaseConfig.from_env(...)
```

Supported URL forms in V1:

```text
sqlite:///relative/path.db
sqlite:////absolute/path.db
mysql://user:password@host:port/database
```

The app should be able to initialize database from config without business code managing connection lifecycle manually.

#### Tests

- app.db can be assigned and accessed from request handler;
- `Database.from_url("sqlite:///...")` works;
- invalid database URL returns a readable config error;
- database resource closes during app shutdown if lifecycle hook exists.

### 4.5 V1-03 cache module

#### Goal

Provide cache API for business code with memory cache and Redis cache.

#### Public API target

```python
await request.app.cache.set("user:1", {"name": "dodo"}, ttl=3600)
user = await request.app.cache.get("user:1")
await request.app.cache.delete("user:1")
```

#### Implementation plan

Implement package:

```text
lingshu/cache/
  __init__.py
  config.py
  errors.py
  protocol.py
  memory.py
  redis.py
  serializer.py
```

Minimum objects:

```text
Cache
CacheConfig
CacheAdapter protocol
MemoryCache
RedisCache
CacheError
CacheConnectionError
CacheSerializationError
```

Required behavior:

- `MemoryCache` works without external service.
- `RedisCache` is implemented as optional backend.
- `get(key)` returns cached value or `None`.
- `set(key, value, ttl=None)` stores value.
- `delete(key)` removes value.
- `exists(key)` checks existence.
- `ttl(key)` returns remaining TTL when supported.
- namespace/prefix is supported.
- JSON serialization is available for dict/list/scalar values.
- `app.cache` exposes cache to handlers.

#### Tests

- memory cache set/get/delete;
- memory cache TTL expiry;
- namespace isolation;
- serialization round trip;
- app.cache handler access;
- Redis adapter missing dependency path is readable.

### 4.6 V1-04 OpenAPI and docs

#### Goal

Expose API documentation for routes.

#### Public behavior target

```text
GET /openapi.json
GET /docs
```

#### Implementation plan

Implement package:

```text
lingshu/openapi/
  __init__.py
  builder.py
  schema.py
  docs.py
```

Required behavior:

- collect registered routes;
- expose path, method, handler name, summary when provided;
- allow optional route metadata;
- generate minimal OpenAPI-compatible JSON;
- serve a simple docs page that loads `/openapi.json`;
- integrate with LingShu app through explicit method such as `app.enable_openapi()`.

Target developer API:

```python
app.enable_openapi(title="My API", version="0.1.0")

@app.get("/users", summary="List users")
async def list_users(request):
    return {"data": []}
```

#### Tests

- `/openapi.json` returns valid JSON;
- registered routes appear in schema;
- summary appears when provided;
- `/docs` returns HTML;
- docs endpoints do not break existing routes.

### 4.7 V1-05 upload module

#### Goal

Support common backend file upload.

#### Public API target

```python
@app.post("/upload")
async def upload(request):
    file = await request.file("avatar")
    saved = await file.save("uploads")
    return {"path": saved.path}
```

#### Implementation plan

Implement package:

```text
lingshu/upload/
  __init__.py
  file.py
  parser.py
  storage.py
  errors.py
```

Required behavior:

- parse `multipart/form-data`;
- support single file field;
- expose filename, content_type, size;
- enforce max file size;
- save to local directory;
- return safe saved path;
- reject path traversal;
- provide readable error response.

#### Tests

- upload small file;
- reject oversized file;
- reject missing file field;
- preserve safe filename or generate safe name;
- prevent path traversal;
- save file to temp directory in tests.

### 4.8 V1-06 auth module

#### Goal

Provide basic login/token/current-user capability.

#### Public API target

```python
from lingshu.auth import Auth, require_login

@app.post("/login")
async def login(request):
    return await auth.login(request)

@app.get("/me")
@require_login
async def me(request):
    return request.user
```

#### Implementation plan

Implement package:

```text
lingshu/auth/
  __init__.py
  config.py
  password.py
  token.py
  middleware.py
  decorators.py
  errors.py
```

Required behavior:

- password hashing helper;
- password verification helper;
- token creation;
- token verification;
- auth middleware that populates `request.user`;
- `require_login` decorator;
- login failure returns stable error;
- missing/invalid token returns stable error.

V1 can store users through the database API and a minimal user repository used by examples.

#### Tests

- password hash/verify;
- login success;
- login failure;
- token verification;
- `/me` with token succeeds;
- `/me` without token fails;
- request.user is available after authentication.

### 4.9 V1-07 RBAC module

#### Goal

Provide role/permission checks for internal admin services.

#### Public API target

```python
from lingshu.rbac import require_permission

@app.post("/assets")
@require_permission("asset:create")
async def create_asset(request):
    return {"ok": True}
```

#### Implementation plan

Implement package:

```text
lingshu/rbac/
  __init__.py
  models.py
  repository.py
  decorators.py
  errors.py
```

Required behavior:

- user has roles;
- role has permissions;
- `require_permission(name)` checks current user;
- missing login returns auth error;
- missing permission returns permission error;
- admin example includes tables and seed data.

#### Tests

- user with permission can access;
- user without permission is rejected;
- unauthenticated user is rejected;
- multiple roles merge permissions;
- permission checks use database-backed repository in example tests.

### 4.10 V1-08 examples

#### Goal

Provide runnable business examples for developers and for acceptance.

#### Required examples

```text
examples/basic_api/
  app.py
  schema.sql
  README.md

examples/admin/
  app.py
  schema.sql
  seed.py
  README.md
```

#### basic_api must include

- database initialization;
- `/users` list;
- `/users` create;
- `/users/{id}` read/update/delete if routing supports it;
- `/openapi.json`;
- `/docs`.

#### admin must include

- user table;
- role table;
- permission table;
- login;
- `/me`;
- protected route;
- permission-protected route;
- cache usage where appropriate;
- upload route.

#### Tests

- example imports safely;
- example app can be created;
- key routes return expected status/body through test client.

### 4.11 V1 final acceptance

V1 is accepted only when these are true:

- database module works;
- SQLite works;
- MySQL public entry exists over accepted boundary;
- app.db works;
- cache works with memory backend;
- Redis backend exists as optional path;
- OpenAPI JSON works;
- `/docs` works;
- upload works;
- auth works;
- RBAC works;
- examples/basic_api works;
- examples/admin works;
- validation chain passes.

Required validation:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy lingshu tests
.\.venv\Scripts\python.exe -m pytest
```

## 5. V2: CLI and project generation

### 5.1 V2 goal

V2 must make LingShu fast to start new projects with.

A developer must be able to run:

```powershell
lingshu new myapp
cd myapp
lingshu run app:app
```

And for admin projects:

```powershell
lingshu new-admin myadmin
cd myadmin
lingshu db init
lingshu run app:app
```

### 5.2 V2 module list

V2 includes:

1. `lingshu new`
2. `lingshu new-api`
3. `lingshu new-admin`
4. `lingshu run`
5. `lingshu routes`
6. `lingshu check`
7. `lingshu db init`
8. generated project templates
9. generated tests
10. generated `.env.example`
11. generated config file
12. Windows and Linux run instructions

### 5.3 V2-01 project generator

#### Goal

Generate a minimal runnable project.

#### Command target

```powershell
lingshu new myapp
```

Generated structure:

```text
myapp/
  app.py
  config.py
  .env.example
  README.md
  tests/
    test_app.py
```

Generated app must include:

- app creation;
- one health route;
- database config placeholder;
- basic test.

### 5.4 V2-02 API project generator

#### Goal

Generate an API starter project.

#### Command target

```powershell
lingshu new-api myapi
```

Generated structure:

```text
myapi/
  app.py
  config.py
  routes/
    users.py
  db/
    schema.sql
  .env.example
  README.md
  tests/
    test_users.py
```

Generated app must include:

- database initialization instruction;
- `/users` list/create routes;
- OpenAPI enabled;
- tests for core API route.

### 5.5 V2-03 admin project generator

#### Goal

Generate a usable internal admin starter.

#### Command target

```powershell
lingshu new-admin myadmin
```

Generated structure:

```text
myadmin/
  app.py
  config.py
  auth.py
  routes/
    auth.py
    users.py
    admin.py
  db/
    schema.sql
    seed.sql
  uploads/
    .gitkeep
  .env.example
  README.md
  tests/
    test_login.py
    test_permissions.py
```

Generated admin must include:

- database schema;
- seed admin user instructions;
- login route;
- `/me` route;
- permission-protected route;
- docs enabled;
- upload route.

### 5.6 V2-04 run/check/routes commands

#### `lingshu run`

Target:

```powershell
lingshu run app:app
```

Behavior:

- loads target app;
- validates import target;
- starts local dev server;
- prints host/port/routes/docs URL.

#### `lingshu check`

Target:

```powershell
lingshu check app:app
```

Behavior:

- validates app import;
- validates route registration;
- validates config shape;
- validates database URL format when present;
- returns readable diagnostics.

#### `lingshu routes`

Target:

```powershell
lingshu routes app:app
```

Behavior:

- prints method/path/handler name;
- marks auth-required routes when metadata exists;
- marks permission-required routes when metadata exists.

### 5.7 V2-05 db init command

#### Goal

Initialize generated project database.

#### Command target

```powershell
lingshu db init
```

Behavior:

- reads project config;
- finds schema file;
- initializes SQLite by default;
- prints created database path;
- for admin template, optionally applies seed file.

### 5.8 V2 final acceptance

V2 is accepted only when:

- `lingshu new myapp` generates runnable project;
- `lingshu new-api myapi` generates runnable API project;
- `lingshu new-admin myadmin` generates runnable admin project;
- generated projects include tests;
- generated projects include `.env.example`;
- generated projects can run on Windows PowerShell;
- generated projects can run on Linux shell;
- `lingshu run`, `lingshu check`, `lingshu routes`, `lingshu db init` work;
- validation chain passes.

## 6. V3: Testing, stability, and acceptance hardening

### 6.1 V3 goal

V3 must make V1 and V2 reliable enough for internal project use.

The target is not to add more feature surface. The target is to make database/cache/auth/rbac/upload/openapi/cli/templates pass real usage tests together.

### 6.2 V3 test areas

V3 must cover:

1. database unit tests;
2. database integration tests;
3. cache unit tests;
4. Redis optional path tests or missing dependency tests;
5. OpenAPI route generation tests;
6. docs page tests;
7. upload parser/storage tests;
8. auth token tests;
9. request.user tests;
10. RBAC permission tests;
11. CLI command tests;
12. project generation tests;
13. generated project pytest tests;
14. admin starter end-to-end tests;
15. Windows path tests;
16. Linux path tests;
17. error response tests;
18. config missing/invalid tests;
19. shutdown/cleanup tests;
20. regression tests for previously fixed issues.

### 6.3 V3-01 database stability tests

Required tests:

- SQLite file database;
- SQLite memory database;
- connection close;
- transaction commit;
- transaction rollback;
- nested transaction behavior decision test;
- invalid SQL error wrapping;
- params forwarding;
- row conversion.

### 6.4 V3-02 cache stability tests

Required tests:

- memory cache set/get/delete;
- TTL expiry;
- namespace isolation;
- JSON serializer;
- invalid value serialization error;
- Redis missing dependency diagnostic;
- app.cache lifecycle.

### 6.5 V3-03 auth/rbac stability tests

Required tests:

- password hash and verify;
- token create/verify;
- invalid token;
- expired token if TTL is supported;
- request.user population;
- require_login success/failure;
- require_permission success/failure;
- multi-role permission merge;
- admin seed login.

### 6.6 V3-04 upload/openapi stability tests

Required tests:

- valid upload;
- oversized upload rejection;
- missing field rejection;
- unsafe filename handling;
- docs endpoint;
- OpenAPI JSON route list;
- OpenAPI metadata preservation;
- protected route metadata where available.

### 6.7 V3-05 CLI/template tests

Required tests:

- `lingshu new` creates expected files;
- `lingshu new-api` creates expected files;
- `lingshu new-admin` creates expected files;
- generated basic project imports;
- generated API project tests pass;
- generated admin project tests pass;
- `lingshu db init` creates database;
- `lingshu routes` lists routes;
- `lingshu check` reports success;
- invalid target reports readable error.

### 6.8 V3 acceptance demo

V3 final acceptance requires a fresh generated admin project to pass this flow:

```powershell
lingshu new-admin demo_admin
cd demo_admin
lingshu db init
lingshu check app:app
lingshu routes app:app
lingshu run app:app
```

Then verify:

```text
GET /docs
GET /openapi.json
POST /login
GET /me
POST /upload
GET protected route without token -> auth error
GET protected route with token -> success
POST permission route without permission -> permission error
POST permission route with permission -> success
```

### 6.9 V3 final acceptance

V3 is accepted only when:

- all V1 modules are tested;
- all V2 commands are tested;
- generated projects can run their own tests;
- examples/basic_api passes;
- examples/admin passes;
- fresh generated admin demo passes acceptance flow;
- validation chain passes.

Required validation:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy lingshu tests
.\.venv\Scripts\python.exe -m pytest
```

## 7. Issue breakdown

### V1 issues

```text
V1-01 database core API
V1-02 app.db and DATABASE_URL integration
V1-03 cache module and app.cache
V1-04 OpenAPI JSON and /docs
V1-05 upload module
V1-06 auth login/token/request.user
V1-07 RBAC role/permission decorators
V1-08 basic_api and admin examples
V1-09 V1 integration acceptance
```

### V2 issues

```text
V2-01 lingshu new project generator
V2-02 lingshu new-api generator
V2-03 lingshu new-admin generator
V2-04 lingshu run/check/routes
V2-05 lingshu db init
V2-06 V2 generated project acceptance
```

### V3 issues

```text
V3-01 database hardening tests
V3-02 cache hardening tests
V3-03 auth/rbac hardening tests
V3-04 upload/openapi hardening tests
V3-05 CLI/template hardening tests
V3-06 generated admin end-to-end acceptance
```

## 8. Execution order

Start immediately with:

```text
V1-01 database core API
```

Mapping:

```text
Current GitHub issue: #146
Suggested branch: human/dodo/p6-db-01-database-core-foundation
```

After V1-01 is merged, continue in this order:

```text
V1-02 app.db and DATABASE_URL integration
V1-03 cache module and app.cache
V1-04 OpenAPI JSON and /docs
V1-05 upload module
V1-06 auth login/token/request.user
V1-07 RBAC role/permission decorators
V1-08 examples
V1-09 V1 integration acceptance
```

## 9. Developer task format

Each developer task must use this short format:

```text
Goal:
Deliver:
Tests:
Validation:
Branch:
Report:
```

No long planning text should be assigned to developers.

## 10. Progress rule

A task is not considered progress unless it delivers at least one of:

- callable framework API;
- runnable command;
- runnable example;
- test coverage;
- generated project template;
- fixed integration failure.

Documentation-only tasks are allowed only when they are PM-owned and support already-delivered capabilities.
