# LingShu V1 / V2 / V3 Delivery Plan

Project: LingShu Framework
Owner: 多多
Planner / PM: 小顾
Status: active delivery plan

## 0. Core delivery rule

LingShu 后续只按可交付能力判断进展，不再用“边界、审计、阶段叙事”代替框架能力。

| 口径 | 必须回答的问题 |
| --- | --- |
| 能不能用 | 业务开发者是否可以直接调用 API |
| 能不能跑 | 是否有可运行示例或命令 |
| 能不能测 | 是否有自动化测试证明能力有效 |
| 能不能省事 | 是否减少业务项目重复开发成本 |

一个任务如果没有产生可调用 API、可运行示例、测试、命令或项目模板，只能算辅助工作，不能算主进展。

## 1. Three-version target

```text
V1: 补齐框架业务能力模块
V2: 补齐 CLI 与项目生成体验
V3: 补齐测试、稳定性和验收硬化
```

三个版本完成后，LingShu 必须能支撑：

| 场景 | 结果 |
| --- | --- |
| 普通 API 项目 | 能启动、写接口、连数据库、看文档 |
| 后台管理项目 | 能登录、鉴权、管理用户/角色/权限、上传文件 |
| 数据驱动项目 | 能使用 SQL/NoSQL、事务、迁移、查询构造器、基础 ORM |
| 本地开发 | 能用 SQLite、Memory/Redis、docs、测试命令快速启动 |
| 内部业务落地 | 能支撑剧栈、柿子量化等项目起步 |

## 2. Responsibility split

### 小顾负责

| 工作 | 说明 |
| --- | --- |
| 版本规划 | 明确 V1/V2/V3 交付目标 |
| issue 编写 | 把任务拆成开发者能直接执行的短任务 |
| 验收标准 | 写清可运行命令、测试、API、示例 |
| PR 标题/正文 | 统一写 summary、validation、risk |
| 最终文档 | 功能实现后补充用户文档和开发文档 |
| 合并建议 | 判断合并、返工、下一步 |

### 开发者负责

| 工作 | 说明 |
| --- | --- |
| 代码 | 按 issue 实现模块能力 |
| 测试 | 单元测试、集成测试、示例测试 |
| 验证 | ruff、format、mypy、pytest |
| 简短汇报 | 分支、commit、API、验证结果 |

开发者不负责长文档、路线规划、PR 包装、验收口径设计。

## 3. V1: framework capability completion

V1 目标是一次性补齐当前框架缺失的业务能力模块，让 LingShu 可以开始承载真实后台/API 项目。

### 3.1 V1 module list

| 模块 | 目标 |
| --- | --- |
| `lingshu.db` | 统一数据库入口，管理 SQL 与 NoSQL 后端 |
| `lingshu.db.sqlite` | SQLite 本地开发与测试数据库 |
| `lingshu.db.mysql` | MySQL 数据库能力 |
| `lingshu.db.postgresql` | PostgreSQL 数据库能力 |
| `lingshu.db.redis` | Redis NoSQL / 缓存 / 计数 / 锁等能力 |
| `lingshu.db.mongodb` | MongoDB 文档数据库能力 |
| `lingshu.cache` | 面向业务缓存的统一入口，可基于 memory/redis |
| `lingshu.openapi` | `/openapi.json` 和 `/docs` |
| `lingshu.upload` | multipart 文件上传、本地保存、限制和安全处理 |
| `lingshu.auth` | 登录、密码、token、当前用户 |
| `lingshu.rbac` | 用户、角色、权限、接口鉴权 |
| `lingshu.config` practical layer | `.env`、环境变量、DATABASE_URL、REDIS_URL、MONGO_URL 等业务配置体验 |
| `lingshu.errors` practical layer | 统一错误码和安全错误响应 |
| examples | `basic_api` 和 `admin` 可运行示例 |

## 4. V1 database design: `lingshu.db`

### 4.1 Correct package naming

数据库模块采用扁平后端包命名。

```text
lingshu.db.sqlite
lingshu.db.mysql
lingshu.db.postgresql
lingshu.db.redis
lingshu.db.mongodb
```

`SQL` 和 `NoSQL` 只作为文档分类，不作为真实包路径。不要设计成 `lingshu.db.sql.mysql` 或 `lingshu.db.nosql.redis`。

### 4.2 Target package layout

```text
lingshu/db/
  __init__.py
  config.py
  errors.py
  urls.py
  manager.py
  query.py
  orm.py
  migration.py
  transaction.py
  safety.py
  sqlite.py
  mysql.py
  postgresql.py
  redis.py
  mongodb.py
```

### 4.3 Unified entry API

目标入口：

```python
from lingshu.db import DB

db = DB.sqlite("dev.db")
rows = db.query("select id, name from users")
```

应用入口：

```python
app.db = DB.from_url("sqlite:///dev.db")

@app.get("/users")
async def users(request):
    rows = request.app.db.query("select id, name from users")
    return {"data": rows}
```

NoSQL 入口：

```python
from lingshu.db import DB

redis = DB.redis("redis://localhost:6379/0")
mongo = DB.mongodb("mongodb://localhost:27017/app")
```

## 5. V1 SQL database capabilities

SQL 后端包括：

```text
lingshu.db.sqlite
lingshu.db.mysql
lingshu.db.postgresql
```

### 5.1 SQL capability table

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| 数据库连接 | 连接 MySQL、PostgreSQL、SQLite 等数据库 | `DB.sqlite(...)`、`DB.mysql(...)`、`DB.postgresql(...)`、`DB.from_url(...)` | SQLite 真实连接；MySQL/PostgreSQL 有统一入口、配置对象和可测适配边界 |
| 执行 SQL | 直接执行查询、插入、更新、删除语句 | `execute(sql, params=None)`、`query(sql, params=None)`、`query_one(sql, params=None)` | create table、insert、select、update、delete 测试通过 |
| 查询构造器 | 用代码拼查询，减少手写 SQL | `db.table("users").select(...).where(...).order_by(...).limit(...)` | 生成 SQL 正确、参数绑定正确、能查询 SQLite |
| ORM 映射 | 把数据库表变成代码里的对象或模型 | 最小 Model / Table 映射，支持字段定义、insert、get、update、delete | 定义 User 模型并完成增删改查测试 |
| 数据迁移 | 用代码管理建表、改字段、加索引 | migration 文件、迁移记录表、`upgrade()`、`downgrade()`、执行顺序 | 新建表迁移、加字段迁移、重复执行不重复应用 |
| 事务处理 | 多个操作要么全部成功，要么全部回滚 | `with db.transaction(): ...`，成功 commit，异常 rollback | commit/rollback 测试通过 |
| 连接池 | 复用数据库连接，提高性能 | MySQL/PostgreSQL 使用连接池；SQLite 明确连接策略 | acquire/release、关闭池、异常释放测试 |
| 安全防护 | 参数绑定，防止 SQL 注入 | 所有 execute/query/query builder 必须支持参数绑定，不拼接用户输入 | 注入字符串测试不破坏 SQL |
| 错误封装 | 把底层异常变成稳定框架错误 | `DBConnectionError`、`DBExecutionError`、`DBTransactionError`、`DBMigrationError` | 错误 code、safe message 测试 |
| 生命周期 | 应用启动/关闭时管理数据库资源 | `app.db` 注册、startup 初始化、shutdown 关闭 | app startup/shutdown 测试 |

### 5.2 SQL backend requirements

| 后端模块 | V1 目标 | 实现要求 |
| --- | --- | --- |
| `lingshu.db.sqlite` | 完整可用 | 使用 Python stdlib `sqlite3`，支持连接、execute/query、事务、迁移、ORM、query builder 测试 |
| `lingshu.db.mysql` | 业务可用入口 | 基于已有 MySQL 边界产品化，提供统一 DB API、连接池、事务、参数绑定、错误封装 |
| `lingshu.db.postgresql` | 统一适配入口 | 建立配置、URL、适配器接口、测试替身；真实驱动作为 optional backend 接入 |

### 5.3 Query builder target

```python
rows = (
    db.table("users")
    .select("id", "name")
    .where("status", "=", "active")
    .order_by("id", desc=True)
    .limit(20)
    .all()
)
```

| 能力 | 作用 | V1 实现要求 |
| --- | --- | --- |
| select | 选择字段 | 支持字段列表，默认 `*` |
| where | 条件过滤 | 支持 `=`, `!=`, `>`, `<`, `>=`, `<=`, `like`, `in` |
| order_by | 排序 | 支持 asc/desc |
| limit/offset | 分页 | 支持限制数量和偏移 |
| insert | 插入记录 | dict 输入转 SQL 参数 |
| update | 更新记录 | dict 输入 + where 条件 |
| delete | 删除记录 | where 条件必须显式 |
| 参数绑定 | 防注入 | 所有值走参数绑定 |

### 5.4 Minimal ORM target

```python
from lingshu.db import Model, field

class User(Model):
    __table__ = "users"
    id = field.integer(primary_key=True)
    name = field.text()
    status = field.text(default="active")

user = User(name="dodo")
db.save(user)
found = db.get(User, user.id)
```

| 能力 | 作用 | V1 实现要求 |
| --- | --- | --- |
| Model 定义 | 表映射到类 | 支持 `__table__` 和字段声明 |
| 字段类型 | 描述列类型 | integer、text、boolean、datetime 基础类型 |
| 主键 | 定位记录 | 支持单字段主键 |
| insert/save | 保存对象 | 对象转 insert/update |
| get | 按主键查询 | 返回模型对象或 None |
| update | 修改对象 | 保存变更 |
| delete | 删除对象 | 按主键删除 |
| dict 转换 | API 返回方便 | `to_dict()` |

### 5.5 Migration target

```python
db.migrations.apply("migrations")
db.migrations.status()
```

迁移文件示例：

```python
def upgrade(db):
    db.execute("create table users (id integer primary key, name text)")

def downgrade(db):
    db.execute("drop table users")
```

| 能力 | 作用 | V1 实现要求 |
| --- | --- | --- |
| 迁移目录 | 存放迁移文件 | 默认 `migrations/` |
| 迁移记录表 | 记录已执行迁移 | `_lingshu_migrations` |
| apply | 执行未应用迁移 | 按文件名顺序执行 |
| status | 查看迁移状态 | 列出已执行/未执行 |
| rollback | 回滚最近迁移 | 支持 downgrade |
| 幂等 | 避免重复执行 | 已执行迁移不重复应用 |

## 6. V1 Redis capabilities: `lingshu.db.redis`

Redis 模块路径：

```text
lingshu.db.redis
```

目标入口：

```python
redis = DB.redis("redis://localhost:6379/0")
await redis.set("user:1", {"name": "dodo"}, ttl=3600)
user = await redis.get("user:1")
```

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| 连接 Redis | 连接 Redis 服务 | `DB.redis(url)`、`RedisClient.from_url(url)` | 缺依赖/连接失败有清晰错误；fake 测试基础行为 |
| key/value | 字符串与 JSON 缓存 | `get`、`set`、`delete`、`exists` | set/get/delete 测试 |
| TTL | 过期时间 | `set(..., ttl=seconds)`、`ttl(key)` | TTL 过期测试 |
| Hash | 存储对象字段 | `hget`、`hset`、`hgetall`、`hdel` | hash round-trip 测试 |
| List | 队列/列表 | `lpush`、`rpush`、`lpop`、`rpop`、`llen` | list 行为测试 |
| Set | 去重集合 | `sadd`、`srem`、`smembers` | set 行为测试 |
| Counter | 计数器 | `incr`、`decr` | 计数测试 |
| Lock | 简单分布式锁 | `lock(name, ttl)` 上下文 | fake 实现测试获得/释放 |
| Pub/Sub | 简单发布订阅 | `publish`、`subscribe` 接口边界 | 接口和 fake 行为测试 |
| 序列化 | dict/list/scalar 自动序列化 | JSON serializer | round-trip 测试 |
| 命名空间 | 避免 key 冲突 | prefix/namespace | namespace 隔离测试 |
| app.cache | 业务缓存入口 | `app.cache` 可绑定 redis/memory | handler 内可使用 |

## 7. V1 MongoDB capabilities: `lingshu.db.mongodb`

MongoDB 模块路径：

```text
lingshu.db.mongodb
```

目标入口：

```python
mongo = DB.mongodb("mongodb://localhost:27017/app")
users = mongo.collection("users")
await users.insert_one({"name": "dodo"})
```

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| 连接 MongoDB | 连接 MongoDB 数据库 | `DB.mongodb(url)`、`MongoClient.from_url(url)` | 缺依赖/连接失败有清晰错误；fake 测试基础行为 |
| Collection | 获取集合 | `mongo.collection("users")` | collection 对象可用 |
| Insert | 插入文档 | `insert_one`、`insert_many` | 插入测试 |
| Find | 查询文档 | `find_one`、`find` | 查询测试 |
| Update | 更新文档 | `update_one`、`update_many` | 更新测试 |
| Delete | 删除文档 | `delete_one`、`delete_many` | 删除测试 |
| Index | 索引管理 | `create_index`、`drop_index` | fake 行为测试 |
| Aggregation | 聚合查询 | `aggregate(pipeline)` | pipeline 传递测试 |
| Transaction | 多文档事务边界 | 如果后端支持，提供 `transaction()` 边界 | 接口行为测试 |
| ObjectId 处理 | 文档 ID 规范 | 统一 ID 转换和安全返回 | ID round-trip 测试 |
| 错误封装 | 稳定错误码 | `MongoConnectionError`、`MongoExecutionError` | 错误测试 |

## 8. V1 cache module: `lingshu.cache`

缓存模块是业务友好入口，底层可以使用 memory 或 `lingshu.db.redis`。

```python
await request.app.cache.set("user:1", {"name": "dodo"}, ttl=3600)
user = await request.app.cache.get("user:1")
```

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| MemoryCache | 本地开发无需 Redis | `MemoryCache()` | set/get/delete/ttl 测试 |
| RedisCache | 生产缓存入口 | 基于 `lingshu.db.redis` | fake 或 optional dependency 测试 |
| get/set/delete | 基础缓存 | 统一 async API | 行为测试 |
| exists | 判断 key 是否存在 | `exists(key)` | 存在/不存在测试 |
| ttl | 获取剩余时间 | `ttl(key)` | TTL 测试 |
| namespace | key 隔离 | prefix/namespace | 隔离测试 |
| serializer | JSON 序列化 | dict/list/scalar round-trip | 序列化测试 |
| app.cache | app 注入 | handler 通过 `request.app.cache` 使用 | handler 测试 |

## 9. V1 OpenAPI / docs module: `lingshu.openapi`

```python
app.enable_openapi(title="My API", version="0.1.0")

@app.get("/users", summary="List users")
async def users(request):
    return {"data": []}
```

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| OpenAPI JSON | 输出接口 schema | `GET /openapi.json` | JSON 结构测试 |
| Docs 页面 | 浏览器查看接口 | `GET /docs` | HTML 返回测试 |
| 路由收集 | 自动读取 app routes | method/path/handler | route schema 测试 |
| route metadata | 接口说明 | summary、tags、description | metadata 测试 |
| request schema | 请求参数说明 | query/body metadata | schema 测试 |
| response schema | 响应说明 | response metadata | schema 测试 |
| auth 标记 | 文档显示登录要求 | require_login metadata | protected route schema 测试 |
| permission 标记 | 文档显示权限要求 | require_permission metadata | permission schema 测试 |

## 10. V1 upload module: `lingshu.upload`

```python
@app.post("/upload")
async def upload(request):
    file = await request.file("avatar")
    saved = await file.save("uploads")
    return {"path": saved.path}
```

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| multipart parser | 解析上传请求 | 支持 `multipart/form-data` | 上传请求测试 |
| single file | 单文件上传 | `request.file(name)` | 文件字段测试 |
| file metadata | 获取文件信息 | filename、content_type、size | metadata 测试 |
| size limit | 限制大小 | max size 配置 | 超限测试 |
| local save | 保存本地 | `file.save(dir)` | 文件存在测试 |
| safe filename | 防路径穿越 | 清理文件名或生成安全名 | path traversal 测试 |
| error response | 上传错误可读 | missing/too large/invalid multipart | 错误码测试 |

## 11. V1 auth module: `lingshu.auth`

```python
@app.post("/login")
async def login(request):
    return await auth.login(request)

@app.get("/me")
@require_login
async def me(request):
    return request.user
```

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| password hash | 安全保存密码 | hash/verify helper | hash verify 测试 |
| login | 用户登录 | username/password -> token | 成功/失败测试 |
| token create | 生成 token | 带用户 ID、过期时间 | token 测试 |
| token verify | 校验 token | 解析并验证 | invalid/expired 测试 |
| request.user | 当前用户 | middleware 写入 request.user | handler 测试 |
| require_login | 登录保护 | decorator/middleware | 未登录失败、已登录成功 |
| auth error | 稳定错误 | `auth.required`、`auth.invalid_token` | 错误响应测试 |
| DB user repo | 用户数据来源 | 基于 `lingshu.db` 的最小用户仓库 | 登录查用户测试 |

## 12. V1 RBAC module: `lingshu.rbac`

```python
@app.post("/assets")
@require_permission("asset:create")
async def create_asset(request):
    return {"ok": True}
```

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| user | 用户主体 | 用户 ID、状态、角色 | 用户表/模型测试 |
| role | 角色 | 角色名称、描述 | role 测试 |
| permission | 权限点 | 字符串权限，如 `asset:create` | permission 测试 |
| user-role | 用户绑定角色 | 多角色支持 | 多角色测试 |
| role-permission | 角色绑定权限 | 多权限支持 | 权限合并测试 |
| require_permission | 接口权限校验 | decorator/middleware | 有/无权限测试 |
| permission error | 稳定错误 | `permission.denied` | 错误响应测试 |
| admin seed | 初始化管理员 | admin 示例提供 seed | seed login 测试 |

## 13. V1 config and errors

### 13.1 `lingshu.config` practical layer

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| `.env` | 本地配置 | 加载 `.env` 或 `.env.example` 约定 | env 测试 |
| environment variables | 线上配置 | 环境变量覆盖默认值 | 覆盖测试 |
| DATABASE_URL | 数据库配置 | sqlite/mysql/postgresql URL | URL 解析测试 |
| REDIS_URL | Redis 配置 | Redis optional backend | URL 解析测试 |
| MONGO_URL | MongoDB 配置 | Mongo optional backend | URL 解析测试 |
| APP_SECRET | token 密钥 | auth 使用 | 缺失/存在测试 |
| redaction | 隐藏敏感值 | 日志/错误不暴露密码密钥 | redaction 测试 |
| typed config | 类型化配置 | int/bool/path/list 基础转换 | 类型转换测试 |

### 13.2 `lingshu.errors` practical layer

| 能力 | 作用 | V1 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| error code | 稳定错误码 | `db.execution_failed` 等 | code 测试 |
| safe message | 安全提示 | 不暴露内部异常细节 | response 测试 |
| HTTP mapping | 映射状态码 | auth 401、permission 403、db 500 | status 测试 |
| details | 安全详情 | 只放白名单字段 | 敏感字段测试 |
| internal cause | 内部保留异常 | 不返回客户端 | traceback 不泄露测试 |
| problem JSON | 标准错误格式 | JSON error body | body 测试 |

## 14. V1 examples

### 14.1 `examples/basic_api`

| 能力 | 作用 | 内容 |
| --- | --- | --- |
| app.py | 启动示例 API | 创建 app，启用 db/openapi |
| users API | 演示数据库 CRUD | list/create/read/update/delete |
| schema/migration | 建表 | users 表 |
| docs | 接口文档 | `/docs`、`/openapi.json` |
| tests | 示例可测 | users route 测试 |

### 14.2 `examples/admin`

| 能力 | 作用 | 内容 |
| --- | --- | --- |
| login | 管理员登录 | `/login` |
| me | 当前用户 | `/me` |
| users | 用户管理示例 | list/create |
| roles | 角色权限示例 | role/permission 表 |
| protected route | 登录保护 | require_login |
| permission route | 权限保护 | require_permission |
| upload | 文件上传 | `/upload` |
| cache | 缓存示例 | app.cache 使用 |
| docs | 接口文档 | `/docs` |
| tests | 示例验收 | login/permission/upload 测试 |

## 15. V1 issue breakdown

| Issue | 模块 | 主要交付 |
| --- | --- | --- |
| V1-01 | `lingshu.db` foundation | 统一 DB 入口、配置、错误、URL、manager |
| V1-02 | `lingshu.db.sqlite` | SQLite 连接、execute/query、事务、连接策略 |
| V1-03 | `lingshu.db.mysql` | MySQL 统一入口、连接池、execute/query、事务、错误封装 |
| V1-04 | `lingshu.db.postgresql` | PostgreSQL 统一入口、配置、适配接口、测试替身 |
| V1-05 | Query builder | select/where/insert/update/delete/参数绑定 |
| V1-06 | ORM minimal | Model、field、save/get/update/delete |
| V1-07 | Migration | migrations apply/status/rollback |
| V1-08 | `lingshu.db.redis` | Redis key/hash/list/set/ttl/counter/lock/pubsub |
| V1-09 | `lingshu.db.mongodb` | MongoDB collection CRUD/index/aggregate/transaction boundary |
| V1-10 | `lingshu.cache` | MemoryCache、RedisCache、app.cache |
| V1-11 | `lingshu.openapi` | `/openapi.json`、`/docs` |
| V1-12 | `lingshu.upload` | multipart、本地保存、大小限制、安全文件名 |
| V1-13 | `lingshu.auth` | password、token、request.user、require_login |
| V1-14 | `lingshu.rbac` | user/role/permission、require_permission |
| V1-15 | config/errors/examples | env、URL、redaction、统一错误、basic_api、admin |
| V1-16 | V1 acceptance | V1 全模块集成验收 |

## 16. V1 final acceptance

| 验收项 | 要求 |
| --- | --- |
| SQL | SQLite 可完整 CRUD；MySQL/PostgreSQL 有统一入口和适配边界 |
| SQL 安全 | 所有查询支持参数绑定 |
| Query builder | 能完成 select/insert/update/delete |
| ORM | 能定义 User 模型并增删改查 |
| Migration | 能建表、记录迁移、查看状态、回滚 |
| Redis | key/hash/list/set/ttl/counter/lock/pubsub 接口可用或 fake 可测 |
| MongoDB | collection CRUD/index/aggregate 接口可用或 fake 可测 |
| Cache | MemoryCache 可用，RedisCache 接口可用 |
| OpenAPI | `/openapi.json` 和 `/docs` 可访问 |
| Upload | 文件上传和保存可用 |
| Auth | 登录、token、request.user、require_login 可用 |
| RBAC | 角色权限和 require_permission 可用 |
| Examples | basic_api 和 admin 可运行 |
| Validation | ruff、format、mypy、pytest 全过 |

## 17. V2: CLI and project generation

V2 专门解决项目生成和开发体验。

### 17.1 V2 CLI capability table

| 能力 | 作用 | V2 实现要求 | 验收方式 |
| --- | --- | --- | --- |
| `lingshu new` | 创建最小项目 | app.py、config.py、tests、README、.env.example | 生成后能启动和测试 |
| `lingshu new-api` | 创建 API 项目 | users API、db schema、openapi、tests | 生成后 users API 测试通过 |
| `lingshu new-admin` | 创建后台项目 | login、me、rbac、upload、docs、db seed | 生成后 admin 验收通过 |
| `lingshu run` | 启动项目 | 加载 `module:app`，启动服务 | 本地启动测试 |
| `lingshu check` | 检查项目 | 检查 import、routes、config、db URL | 成功/失败诊断测试 |
| `lingshu routes` | 查看路由 | 输出 method/path/handler/auth/permission | 路由列表测试 |
| `lingshu db init` | 初始化数据库 | 执行 schema/migrations/seed | 生成 db 文件/表测试 |
| Windows 命令 | Windows 开发可用 | PowerShell 示例 | Windows 路径测试 |
| Linux 命令 | Linux 部署可用 | shell 示例 | Linux 路径测试 |

### 17.2 V2 generated project templates

| 模板 | 作用 | 必须包含 |
| --- | --- | --- |
| basic | 最小项目 | health route、config、tests |
| api | 数据 API 项目 | database、users CRUD、openapi、tests |
| admin | 后台项目 | auth、rbac、upload、cache、docs、db init、tests |

## 18. V3: testing, stability, and acceptance hardening

V3 专门做测试和稳定性。

### 18.1 V3 test capability table

| 测试模块 | 作用 | 必须覆盖 |
| --- | --- | --- |
| SQL database tests | 保证数据库可靠 | connection、execute、query、transaction、pool、safety |
| Query builder tests | 保证构造 SQL 正确 | select、where、insert、update、delete、params |
| ORM tests | 保证模型映射可用 | field、save、get、update、delete、to_dict |
| Migration tests | 保证迁移可用 | apply、status、rollback、幂等 |
| Redis tests | 保证 Redis 接口可靠 | get/set/hash/list/set/ttl/counter/lock/pubsub |
| MongoDB tests | 保证 Mongo 接口可靠 | insert/find/update/delete/index/aggregate |
| Cache tests | 保证缓存业务入口可靠 | memory、redis、namespace、serializer、ttl |
| OpenAPI tests | 保证接口文档可靠 | schema、metadata、auth/permission tags |
| Upload tests | 保证上传安全 | multipart、size limit、safe filename、save |
| Auth tests | 保证登录可靠 | password、token、request.user、require_login |
| RBAC tests | 保证权限可靠 | role、permission、require_permission |
| Config tests | 保证配置可靠 | env、url parse、redaction、missing config |
| Error tests | 保证错误安全 | code、safe message、status、no secret leak |
| CLI tests | 保证命令可靠 | new、new-api、new-admin、run、check、routes、db init |
| Template tests | 保证生成项目可靠 | generated project import、pytest、acceptance flow |
| End-to-end tests | 保证业务链路可靠 | admin 登录、权限、上传、docs、db/cache 一起跑 |

### 18.2 V3 final acceptance flow

```powershell
lingshu new-admin demo_admin
cd demo_admin
lingshu db init
lingshu check app:app
lingshu routes app:app
lingshu run app:app
```

Then verify:

| 请求 | 预期 |
| --- | --- |
| `GET /docs` | 返回文档页 |
| `GET /openapi.json` | 返回 schema |
| `POST /login` | 返回 token |
| `GET /me` without token | auth error |
| `GET /me` with token | 当前用户 |
| protected route without token | auth error |
| permission route without permission | permission error |
| permission route with permission | success |
| upload route | 保存文件并返回路径 |

### 18.3 V3 final validation

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy lingshu tests
.\.venv\Scripts\python.exe -m pytest
```

## 19. Execution order

Current execution starts from existing issue:

```text
#146: P6-DB-01 / V1-01 database core foundation
```

Immediate order:

```text
V1-01 lingshu.db foundation
V1-02 lingshu.db.sqlite
V1-03 lingshu.db.mysql
V1-04 lingshu.db.postgresql
V1-05 Query builder
V1-06 ORM minimal
V1-07 Migration
V1-08 lingshu.db.redis
V1-09 lingshu.db.mongodb
V1-10 lingshu.cache
V1-11 lingshu.openapi
V1-12 lingshu.upload
V1-13 lingshu.auth
V1-14 lingshu.rbac
V1-15 config/errors/examples
V1-16 V1 acceptance
V2-01 CLI new
V2-02 CLI new-api
V2-03 CLI new-admin
V2-04 run/check/routes/db init
V2-05 V2 acceptance
V3-01 module tests
V3-02 CLI/template tests
V3-03 admin end-to-end tests
V3-04 final hardening
```

## 20. Developer task format

Every issue given to developers must use this format:

```text
Goal:
Deliver:
API:
Tests:
Validation:
Branch:
Report:
```

## 21. Progress rule

A task is not progress unless it delivers one of:

- callable framework API;
- database/cache/auth/rbac/openapi/upload behavior;
- runnable command;
- runnable example;
- generated project template;
- automated test coverage;
- fixed integration failure.
