# LingShu Framework 实施计划

状态：P5 总控计划
更新时间：2026-07-06

## 1. 总目标

LingShu 的目标是成为完整 Python Web/API Framework，而不是只完成最小 HTTP Server。

总体能力分为四层：

```text
1. Kernel layer：Application、Router、Middleware、Request、Response、Runtime
2. Resource layer：Extension、Resource lifecycle、Config、Diagnostics、Record
3. Application layer：DB、Cache、Queue、Session、OpenAPI、Validation、Auth
4. Production layer：Multi-worker、Reload、Adapters、Observability、Release
```

当前已经完成 Kernel layer 的最小闭环，并已有 Resource layer 基础。下一步要从 Resource layer 推进到 Application layer。

## 2. Plan 01：状态同步与完整性审计

目标：把仓库状态文档同步，建立完整性审计和总控计划。

交付：

```text
docs/development/FRAMEWORK_COMPLETENESS_AUDIT.md
docs/development/FRAMEWORK_COMPETITIVE_ANALYSIS.md
docs/development/FRAMEWORK_IMPLEMENTATION_PLAN.md
docs/development/FRAMEWORK_CLEANUP_AND_SYNC_PLAN.md
README.md
docs/development/CURRENT_PHASE.md
docs/development/HANDOFF.md
docs/development/P5_ROADMAP.md
```

## 3. Plan 02：`lingshu.db` 数据库层总架构

目标：先定义数据库层总架构，再推进具体数据库驱动。

交付：

```text
docs/architecture/DATABASE_LAYER_ARCHITECTURE.md
```

必须定义：

```text
lingshu.db 统一入口
lingshu.db.mysql
lingshu.db.redis
lingshu.db.mongodb
app.db 未来访问方向
DatabaseManager
DatabaseDriver
DatabaseResource
DatabaseConfig
ResourceRegistry
resource name：db.mysql.main / db.redis.cache / db.mongodb.main
SQL / NoSQL / ORM / Migration 分层
```

## 4. Plan 03：`lingshu.db` 最小代码骨架

目标：让 `lingshu.db` 成为真实 public namespace，而不是只停留在文档。

交付：

```text
lingshu/db/__init__.py
lingshu/db/driver.py
lingshu/db/resource.py
lingshu/db/manager.py
lingshu/db/config.py
lingshu/db/errors.py
tests/db/
```

验收：

```text
import lingshu.db 无副作用
不引入数据库 client
不连接网络
ruff / mypy / pytest 通过
```

## 5. Plan 04：`lingshu.db.mysql` 驱动契约与骨架

目标：建立第一个 SQL 驱动样板。

目标 API：

```python
from lingshu.db.mysql import mysql

app.add_extension(mysql(name="main", dsn="..."))
```

## 6. Plan 05：`lingshu.db.redis` 回归对齐

目标：把已完成的 Redis track 对齐到 `lingshu.db` 总架构。

目标 API：

```python
from lingshu.db.redis import redis

app.add_extension(redis(name="cache", dsn="..."))
```

## 7. Plan 06：`lingshu.db.mongodb` 驱动契约与骨架

目标：建立 NoSQL / Document DB 样板。

目标 API：

```python
from lingshu.db.mongodb import mongodb

app.add_extension(mongodb(name="main", dsn="..."))
```

## 8. 后续计划

```text
Plan 07：真实数据库 runtime adapter 策略
Plan 08：SQL Query / Transaction 层
Plan 09：NoSQL Command 层
Plan 10：ORM / ODM / Migration ADR
Plan 11：OpenAPI / Schema / Validation
Plan 12：Auth / Tenant / RBAC
Plan 13：Production Runtime
```
