# LingShu V2 CLI and Project Generation Plan

Project: LingShu Framework
Owner: 多多
Planner / PM: 小顾
Status: active V2 plan

## 0. V2 goal

V2 must make LingShu easy to start real projects with.

V2 does not expand core business modules. V2 packages the V1 capabilities into clear CLI commands and project templates.

After V2, a developer should be able to generate a working API or admin project without manually copying files or guessing structure.

## 1. V2 delivery rule

A V2 task is progress only if it produces one of:

- a runnable CLI command;
- a generated project template;
- a generated test suite;
- a command that diagnoses project problems;
- a command that initializes or runs a generated project.

## 2. V2 module checklist

| Command / area | Purpose |
| --- | --- |
| `lingshu new` | Generate minimal project. |
| `lingshu new-api` | Generate API project. |
| `lingshu new-admin` | Generate admin project. |
| `lingshu run` | Run a LingShu app target. |
| `lingshu check` | Check import, app, config, routes, and backend URLs. |
| `lingshu routes` | Print registered routes. |
| `lingshu db init` | Initialize project database schema/migrations/seed. |
| `lingshu doctor` | Diagnose local environment and project readiness. |
| Project templates | Basic, API, admin. |
| Windows/Linux instructions | Reliable commands for both environments. |

## 3. CLI command rules

All commands must follow these rules:

| Rule | Requirement |
| --- | --- |
| readable output | command output should tell the developer what happened and what to do next. |
| safe failure | errors should be clear and not leak secrets. |
| deterministic files | generated files should be stable for tests. |
| no hidden service requirement | generated projects should run locally with SQLite and MemoryCache by default. |
| V1 module usage | generated projects must use V1 framework modules, not hand-written substitutes. |

## 4. `lingshu new`

### Goal

Create the smallest runnable LingShu project.

### Command

```powershell
lingshu new myapp
```

### Generated structure

```text
myapp/
  app.py
  config.py
  .env.example
  README.md
  tests/
    test_app.py
```

### Required content

| File | Requirement |
| --- | --- |
| `app.py` | create app, health route, run target. |
| `config.py` | basic config loading. |
| `.env.example` | APP_ENV, APP_SECRET, DATABASE_URL. |
| `README.md` | install, run, test commands. |
| `tests/test_app.py` | app import and health route test. |

### Acceptance

- command creates all expected files;
- project imports cleanly;
- generated health route works;
- generated tests pass.

## 5. `lingshu new-api`

### Goal

Create a database-backed API starter.

### Command

```powershell
lingshu new-api myapi
```

### Generated structure

```text
myapi/
  app.py
  config.py
  routes/
    users.py
  db/
    schema.sql
    migrations/
      0001_create_users.py
  .env.example
  README.md
  tests/
    test_users.py
    test_openapi.py
```

### Required features

| Feature | Requirement |
| --- | --- |
| database | uses `lingshu.db.sqlite` by default. |
| users CRUD | list/create/read/update/delete where routing supports it. |
| validation | uses `lingshu.validation` for request data. |
| response | uses `lingshu.response` helpers. |
| docs | OpenAPI and `/docs` enabled. |
| tests | users route and docs tests. |

### Acceptance

- generated API project can initialize DB;
- users API can create and list users;
- `/openapi.json` and `/docs` work;
- generated tests pass.

## 6. `lingshu new-admin`

### Goal

Create a usable internal admin starter.

### Command

```powershell
lingshu new-admin myadmin
```

### Generated structure

```text
myadmin/
  app.py
  config.py
  routes/
    auth.py
    users.py
    roles.py
    admin.py
    upload.py
  db/
    migrations/
      0001_create_auth_tables.py
      0002_create_audit_tables.py
    seed.py
  uploads/
    .gitkeep
  .env.example
  README.md
  tests/
    test_login.py
    test_permissions.py
    test_upload.py
    test_docs.py
```

### Required features

| Feature | Requirement |
| --- | --- |
| auth | login and `/me`. |
| RBAC | users, roles, permissions, protected route. |
| database | schema/migrations/seed. |
| cache | app.cache example. |
| upload/storage | upload route saves local file. |
| audit | example operation audit. |
| health | `/health` and `/ready`. |
| docs | `/docs` and `/openapi.json`. |
| tests | login, permission, upload, docs tests. |

### Acceptance

- generated admin project initializes DB;
- admin seed creates a login user;
- login returns token;
- `/me` works with token;
- permission-protected route rejects missing permission;
- upload route works;
- docs work;
- generated tests pass.

## 7. `lingshu run`

### Goal

Run a LingShu application target.

### Command

```powershell
lingshu run app:app
```

### Capabilities

| Capability | Requirement |
| --- | --- |
| import target | load `module:app`. |
| factory target | support `module:create_app --factory` if framework supports factories. |
| host/port | support host and port options. |
| readable output | print local URL and docs URL when enabled. |
| failure message | show import/config errors safely. |

## 8. `lingshu check`

### Goal

Check whether a project is ready to run.

### Command

```powershell
lingshu check app:app
```

### Checks

| Check | Requirement |
| --- | --- |
| import | app target imports. |
| app type | target is a LingShu app. |
| routes | route table can be read. |
| config | config can load. |
| DATABASE_URL | parse and validate when present. |
| REDIS_URL | parse and validate when present. |
| MONGO_URL | parse and validate when present. |
| APP_SECRET | present when auth/session enabled. |
| migrations | schema/migration directory exists when DB enabled. |

## 9. `lingshu routes`

### Goal

Print registered routes for quick inspection.

### Command

```powershell
lingshu routes app:app
```

### Output fields

| Field | Requirement |
| --- | --- |
| method | HTTP method. |
| path | route path. |
| handler | handler function. |
| auth | whether login required. |
| permission | required permission if any. |
| summary | route summary if available. |

## 10. `lingshu db init`

### Goal

Initialize the generated project database.

### Command

```powershell
lingshu db init
```

### Behavior

| Behavior | Requirement |
| --- | --- |
| config | read project config and DATABASE_URL. |
| create DB | create SQLite database by default. |
| migrations | apply migrations in order. |
| seed | optional seed execution. |
| idempotent | repeated run is safe. |
| output | print DB path and applied migrations. |

## 11. `lingshu doctor`

### Goal

Diagnose local environment and common project issues.

### Checks

| Check | Requirement |
| --- | --- |
| Python version | show version and compatibility. |
| package import | LingShu importable. |
| optional deps | show missing optional DB/cache drivers. |
| project files | detect app.py/config/.env/migrations. |
| permissions | check writable upload/db paths. |
| config secrets | warn missing APP_SECRET. |

## 12. Template rules

Generated templates must:

- use V1 framework modules;
- avoid hand-written substitutes for framework functions;
- default to SQLite and MemoryCache;
- include `.env.example`;
- include tests;
- include README with Windows PowerShell and Linux shell commands;
- be deterministic for automated tests.

## 13. V2 issue breakdown

| Issue | Main delivery |
| --- | --- |
| V2-01 | `lingshu new` minimal project generator. |
| V2-02 | `lingshu new-api` generator. |
| V2-03 | `lingshu new-admin` generator. |
| V2-04 | `lingshu run`. |
| V2-05 | `lingshu check`. |
| V2-06 | `lingshu routes`. |
| V2-07 | `lingshu db init`. |
| V2-08 | `lingshu doctor`. |
| V2-09 | generated project tests. |
| V2-10 | V2 acceptance. |

## 14. V2 final acceptance

V2 is accepted only when all are true:

```powershell
lingshu new myapp
cd myapp
python -m pytest
```

```powershell
lingshu new-api myapi
cd myapi
lingshu db init
python -m pytest
```

```powershell
lingshu new-admin myadmin
cd myadmin
lingshu db init
lingshu check app:app
lingshu routes app:app
python -m pytest
```

And the repository validation chain passes:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy lingshu tests
.\.venv\Scripts\python.exe -m pytest
```
