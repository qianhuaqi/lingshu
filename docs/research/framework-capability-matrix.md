# LingShu 全球框架能力矩阵

> 状态：第一批研究，持续补充中。
>
> 目标：不按语言排名，只提取可验证的工程机制，并裁决其是否适合 LingShu API。

## 裁决说明

- `adopt`：机制可以直接成为 LingShu 原则。
- `adapt`：保留思想，按 Sanic、异步上下文和 LingShu 边界改造。
- `extension`：不进入最小核心，作为可选后端或扩展。
- `reject`：明确不采用。
- `later`：有价值，但当前阶段暂不实施。

## 第一批能力矩阵

| 样本 | 语言/生态 | 关键机制 | 主要优点 | 主要风险或代价 | LingShu 初步裁决 |
|---|---|---|---|---|---|
| SQLAlchemy 2.x | Python | Session、identity map、Unit of Work、显式 begin/commit/rollback | 事务和对象生命周期边界成熟；Core 与 ORM 两层并存；高级 SQL 有逃生口 | Session/对象状态较复杂；隐式 autoflush、lazy load 容易产生意外 SQL；异步 Session 不能跨并发任务共享 | `adapt`：吸收事务作用域、UoW、identity 语义；默认减少隐式行为 |
| Ecto | Elixir | Changeset、显式外部/内部数据边界、数据库 constraint 转结构化错误 | 输入白名单、类型转换、校验、数据库约束清晰分层；对越权字段特别友好 | 与 Python ORM 传统写法差异大；完整照搬会增加概念 | `adapt`：为 LingShu 增加轻量 Mutation/Changeset 层，不复制整个 Ecto |
| EF Core | .NET | 短生命周期 DbContext、change tracking、property-level update、Unit of Work | 更新只提交已变字段；状态诊断能力强；事务和并发控制成熟 | 长生命周期 Context 容易积累状态和内存；跟踪状态复杂 | `adapt`：事务/资源必须请求级或显式作用域；可选变更追踪，不作为唯一写法 |
| Prisma ORM | TypeScript | Schema 驱动、代码生成、类型安全 Client、transaction/bulk API | 开发体验简单；模型、客户端和迁移联动；事务有 maxWait、timeout、isolation | 生成层可能限制数据库特性；跨后端的统一 API 容易掩盖方言差异 | `adopt` schema/生成体验；`reject` 假装所有数据库能力相同 |
| Ent | Go | Schema/codegen、类型安全 Query、事务 Client、commit/rollback hooks | 编译期类型安全；事务内复用 Client；生成代码稳定 | 代码生成链和升级成本；动态业务扩展不如运行时 ORM 灵活 | `adapt`：能力声明、事务 Client、生成契约；不强制所有模型代码生成 |
| SQLite | 数据库 | 独立事务与锁模型、单写多读、轻量嵌入式 | 单文件、部署简单、测试和边缘场景优秀 | 并发写、DDL、类型和连接语义与 MySQL 明显不同 | `extension`：独立 backend；禁止用 MySQL 方言分支勉强兼容 |
| MongoDB | 文档数据库 | Flexible schema + collection validator、document atomicity、aggregation | 文档聚合自然；Schema 可渐进约束；适合动态素材和嵌套结构 | 无约束使用会产生结构漂移；多文档事务成本高；operator/pipeline 输入存在安全风险 | `adapt`：独立 ODM、双层 Schema、operator 白名单；事务仅显式使用 |
| Redis | KV/协调 | 原子命令、TTL、pipeline、Lua/Function、Stream、锁 | 高性能缓存与协调；pipeline 可减少 RTT；适合幂等、限流、任务状态 | 不是事实数据库；锁受过期、时钟、故障切换影响；无界 key 会拖垮实例 | `adapt`：能力门面，不做 ORM；锁必须 owner+TTL，关键写考虑 fencing |

## 第一批对 LingShu 的组合结论

### 1. 统一入口，独立后端

```text
lingshu.db facade
    -> backend registry
        -> mysql
        -> sqlite
        -> mongodb
        -> redis
```

统一入口负责资源查找、上下文、生命周期、超时、取消、日志、指标和错误分类；具体查询语义由独立后端负责。

### 2. SQL ORM 采用“简单操作 + 显式事务”的混合路线

- 单表常用 CRUD 保持接近 Active Record 的便利性。
- 多步骤业务写入必须进入显式事务。
- 事务内部模型自动使用当前事务连接。
- 高级查询允许进入 Query Builder 或参数化 Raw SQL。
- 不默认依赖隐式 lazy load 和无限级联。

### 3. 输入校验与持久化模型不能完全混为一体

吸收 Ecto Changeset 的关键经验：

- 外部输入必须显式列出允许字段。
- 类型转换、业务校验和数据库约束错误分层。
- `is_admin`、`tenant_id` 等字段不能因为 ORM 模型存在就自动允许客户端写入。

### 4. 各后端必须声明能力

```text
transactions
savepoints
concurrent_writes
returning
upsert
json
schema_migration
document_validation
ttl
pipeline
streams
```

不支持的能力明确报错，不静默模拟。

### 5. 安全优先于统一语法

- SQL 值参数化；标识符和操作符白名单。
- MongoDB operator、projection 和 aggregation 入口受控。
- Redis key 命名空间、TTL、序列化和锁释放校验默认启用。
- Raw/native 入口仍受超时、审计、租户和脱敏约束。

## 下一批研究

- Doctrine ORM：Unit of Work、DBAL、identity map、事务事件。
- Hibernate/JPA：Session、flush、fetch strategy、optimistic locking。
- jOOQ、SQLx、sqlc：SQL 优先与类型安全。
- Django ORM、Rails Active Record、Eloquent：开发效率、Manager/Scope、批处理和风险。
- Drizzle、Piccolo、Tortoise：异步与轻量 ORM 体验。
- MongoEngine、Beanie、ODMantic：Python ODM 边界。
- Redis 客户端与框架封装：pipeline、cluster、cache stampede、锁与限流。

## 第一批官方资料

- SQLAlchemy Session Basics: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- Ecto Changeset: https://hexdocs.pm/ecto/Ecto.Changeset.html
- EF Core Change Tracking: https://learn.microsoft.com/en-us/ef/core/change-tracking/
- Prisma Transactions: https://www.prisma.io/docs/orm/prisma-client/queries/transactions
- Ent Transactions: https://entgo.io/docs/transactions/
- SQLite Transactions: https://www.sqlite.org/lang_transaction.html
- MongoDB Schema Validation: https://www.mongodb.com/docs/manual/core/schema-validation/
- MongoDB Transactions: https://www.mongodb.com/docs/manual/core/transactions/
- Redis Pipelining: https://redis.io/docs/latest/develop/using-commands/pipelining/
- Redis Distributed Locks: https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/
