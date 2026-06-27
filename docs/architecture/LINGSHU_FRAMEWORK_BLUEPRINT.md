# LingShu Framework 总体架构设计总纲（Blueprint v0.4）

- 设计负责人：小顾
- 产品决策人：多多
- 状态：总体设计草案，待多多确认并冻结
- GitHub Issue：#25
- 设计分支：`research/lingshu-framework-blueprint`
- 唯一权威文件：`docs/architecture/LINGSHU_FRAMEWORK_BLUEPRINT.md`
- 变更规则：任何方向变化必须通过 Issue、ADR、Git 提交和多多确认；聊天记录不得覆盖本文件

---

## 1. 根本定位

LingShu 是一个完全独立、自主可控的 Python Web/API Framework，不是 Sanic、FastAPI、Flask、Django 或 Starlette 的二次封装，也不承担当前旧实现的兼容义务。

LingShu 自己定义并控制：

- Application Kernel；
- HTTP Runtime；
- Request、Response、Router、Middleware；
- Native HTTP Server；
- Extension Protocol；
- 生命周期、依赖作用域、取消和清理；
- 错误、安全、调试和可观测合同；
- CLI、Scaffold 和官方扩展生态。

当前仓库中的旧代码只作为需求、测试和实现素材。凡是与本 Blueprint 冲突的代码，在 1.0 前可以重写或删除，不建立永久兼容层。

### 1.1 目标

LingShu 的核心目标是：

1. 稳定：生命周期明确、资源可回滚、取消不泄漏；
2. 安全：从 HTTP 解析层拒绝歧义和恶意输入；
3. 强大：具备完整应用内核、HTTP Runtime、原生服务器和扩展生态；
4. 可调试：每次请求可以凭 Request ID 还原完整执行过程；
5. 可扩展：Auth、Tenant、RBAC、Data、Cache、i18n 等独立安装；
6. 可验证：所有关键行为都有合同测试、协议测试和安全测试；
7. 可维护：Python 版本和平台差异集中处理，不污染业务代码。

### 1.2 明确不做

- 不依赖其他上层 Python Web Framework；
- 不为旧 API 保留双轨实现；
- 不把用户、订单、租户表、角色表等业务模型塞入 Core；
- 不自造密码学算法、TLS 算法和证书验证；
- 不为追求零依赖牺牲安全和正确性；
- 1.0 首阶段不承诺完整 HTTP/2、HTTP/3；
- 不以未经测试的极限性能代替稳定性和安全性。

---

## 2. 总体架构

```text
Project Application
        ↓
Official / Third-party Extensions
        ↓
LingShu HTTP Runtime
        ↓
LingShu Application Kernel
        ↕ Transport Contract
LingShu Native Server
```

包依赖方向：

```text
lingshu_core

lingshu_http       → lingshu_core
lingshu_server     → lingshu_core + lingshu_http
lingshu_cli        → lingshu_core
lingshu            → lingshu_core + lingshu_http + lingshu_server + lingshu_cli

lingshu_auth       → lingshu_core + lingshu_http
lingshu_tenant     → lingshu_core + lingshu_http
lingshu_rbac       → lingshu_core + lingshu_http
lingshu_data       → lingshu_core
lingshu_cache      → lingshu_core
lingshu_i18n       → lingshu_core
lingshu_openapi    → lingshu_core + lingshu_http
lingshu_observability → lingshu_core + lingshu_http
```

Core 不得反向依赖 HTTP、Server 或任何扩展。

---

## 3. 单仓多包结构

```text
packages/
├── lingshu-core/
├── lingshu-http/
├── lingshu-server/
├── lingshu-cli/
├── lingshu-framework/
├── lingshu-auth/
├── lingshu-tenant/
├── lingshu-rbac/
├── lingshu-data/
├── lingshu-cache/
├── lingshu-i18n/
├── lingshu-openapi/
└── lingshu-observability/
```

默认安装：

```bash
pip install lingshu-framework
```

默认只包含 Core、HTTP Runtime、Native Server 和 CLI。Auth、Tenant、数据库、Redis 等按需安装。

多个 distribution 不得共同写同一个普通 Python package。各扩展使用独立 import package，例如：

```text
lingshu_core
lingshu_http
lingshu_server
lingshu_auth
lingshu_tenant
```

只有薄总入口包使用 `lingshu`。

---

## 4. Application Kernel

`lingshu_core` 负责：

- Application Kernel；
- 配置系统；
- 生命周期状态机；
- Extension Manifest；
- Capability Registry；
- Scope-aware Dependency Container；
- ContextVar 管理；
- Execution Context；
- Deadline、Cancellation 和 Cleanup Stack；
- Health Model；
- Error 基础模型；
- Logging Contract；
- Task Registry。

Core 禁止包含：

- HTTP Method、URL Router、Request、Response；
- Sanic、ASGI、WSGI；
- JWT、Tenant、RBAC；
- 数据库、Redis、ORM；
- WebSocket；
- 项目业务字段和表结构。

Kernel 状态机：

```text
created → configured → registered → starting → ready
→ draining → stopping → closed
```

启动失败必须保留原始异常，逆序回滚已启动资源，并汇总清理异常。

内置作用域：

```text
application
worker
request
operation
transient
```

长生命周期对象不得捕获短生命周期对象。

---

## 5. HTTP Runtime

`lingshu_http` 完全由 LingShu 实现，不依赖其他 Web Framework。

### 5.1 核心对象

```python
class Request:
    id: str
    method: str
    target: str
    path: str
    query: QueryParams
    headers: Headers
    cookies: Cookies
    client: ClientInfo
    server: ServerInfo
    body: BodyStream
    state: RequestState
    execution: ExecutionContext

class Response:
    status: int
    headers: Headers
    body: bytes | AsyncIterator[bytes]
```

### 5.2 Router

必须支持：

- 静态和参数路由；
- 类型转换；
- Method 和 Host 匹配；
- Route Name 和反向 URL；
- Route Metadata；
- 启动时冲突检查；
- 编译后的确定性路由树；
- 禁止最后注册者静默覆盖。

### 5.3 Middleware Pipeline

显式阶段：

```text
connection
request_start
before_routing
after_routing
before_handler
after_handler
response_start
response_body
request_end
exception
cleanup
```

中间件必须声明阶段、优先级、依赖、短路能力、Streaming 能力和异常行为。

### 5.4 Streaming

Request Body 与 Response Body 必须支持流式读写、背压、客户端断开、最大 Body 限制、临时文件和清理。

---

## 6. Native Server

`lingshu_server` 是 LingShu 自己的网络运行层。

第一阶段正式范围：

- asyncio TCP；
- HTTP/1.1；
- Keep-Alive；
- Content-Length；
- Chunked Transfer；
- Request/Response Streaming；
- TLS 使用 Python `ssl` / OpenSSL；
- 单进程和多 Worker；
- Windows 与 Linux；
- Graceful Shutdown；
- 可信代理配置。

Parser 采用双实现合同：

1. `StrictPythonParser`：自主实现，作为规范、安全和测试基准；
2. `AcceleratedParser`：后续可选高性能实现，必须通过同一协议测试。

服务器必须默认拒绝：

- 重复或冲突 Content-Length；
- Content-Length 与 Transfer-Encoding 冲突；
- 非法 Chunk；
- CRLF 注入；
- 请求走私；
- 超大 Header、过多 Header、超长请求行；
- Slowloris；
- 无界 Body 和 Multipart；
- 未受信代理头；
- 路径编码歧义。

遇到协议歧义必须拒绝，不能宽松猜测。

---

## 7. Extension Protocol

Manifest 示例：

```python
ExtensionManifest(
    name="lingshu.auth",
    version="0.1.0",
    requires_core=">=0.1,<1.0",
    requires_http=">=0.1,<1.0",
    requires_python=">=3.10,<3.15",
    provides=("security.authentication",),
    requires=(),
    optional_requires=(),
    conflicts=(),
)
```

生命周期：

```text
configure → register → start → ready → drain → stop → close
```

硬性规则：

- 禁止 import-time 注册和建连；
- 注册必须可撤销；
- Start 失败必须逆序回滚；
- Close 必须幂等；
- 后台任务必须进入 Task Registry；
- 多 App 完全隔离；
- 扩展不得修改 Core 文件；
- 扩展必须通过统一 Contract Test。

---

## 8. 官方扩展边界

### Auth

包含 Principal、Authenticator、JWT Bearer、API Key、Session 和认证中间件。不包含用户表、注册登录业务、Tenant 和 RBAC。

### Tenant

包含 TenantContext、Host/Header/Path Resolver 和 Tenant Middleware。不强制依赖 Auth。

需要从认证 Claims 解析 Tenant 时使用独立桥接扩展，禁止 Auth 与 Tenant 相互硬绑定。

### RBAC

包含 Permission、Policy、Gate 和 Authorization Middleware。不包含项目角色表和权限表。

### Data

包含 Resource、Transaction、Repository 和 Driver Extension Contract。MySQL、PostgreSQL、MongoDB、Redis 为独立包。

### Cache

包含 Cache Protocol、Memory Cache、TTL、Key 规范和 Stampede Protection。Redis 实现独立。

### i18n

包含 Locale Resolver、Catalog、Message Formatter 和资源注册。未安装时使用 ErrorSpec 默认消息。

---

## 9. Request ID 与每请求独立 Runtime Record

这是 LingShu 的框架级硬性能力。

### 9.1 不变量

每一个进入 HTTP Runtime 的请求，在完成最基础的报文安全校验后、进入路由和业务代码前，必须：

1. 生成内部 `request_id`；
2. 在 Runtime 中创建以该 `request_id` 命名的独立文件夹；
3. 记录从接入、解析、路由、中间件、业务调用、数据库/缓存/外部调用、响应、异常到清理的完整框架可观测事实；
4. 在正常、异常、超时、取消、客户端断开和崩溃恢复时留下明确终态。

若目录无法创建，默认不得让请求继续进入业务处理。框架返回安全的 `503 Runtime Storage Unavailable`，应用 readiness 失败，并写入进程级应急日志。

### 9.2 Request ID

内部 Request ID：

- 每次请求必有且不可变；
- 安全随机 128 bit；
- 不包含用户、IP、路径和时间戳明文；
- 不采用客户端值；
- 创建目录前检查碰撞；
- 响应头始终返回 `X-Request-ID`。

客户端传入的 `X-Request-ID` 只能作为经过严格校验的 `external_request_id`。

### 9.3 目录结构

默认：

```text
runtime/
└── requests/
    └── 2026/
        └── 06/
            └── 28/
                └── <request_id>/
                    ├── manifest.json
                    ├── request.json
                    ├── events.jsonl
                    ├── routing.json
                    ├── middleware.jsonl
                    ├── logs.jsonl
                    ├── calls/
                    │   ├── database.jsonl
                    │   ├── cache.jsonl
                    │   ├── external_http.jsonl
                    │   ├── message.jsonl
                    │   └── extension.jsonl
                    ├── response.json
                    ├── error.json
                    ├── cleanup.json
                    ├── final.json
                    ├── payload/
                    │   ├── request.meta.json
                    │   ├── request.body
                    │   ├── response.meta.json
                    │   └── response.body
                    └── attachments/
```

按日期分层是为了避免单目录包含海量子目录；最末级目录必须严格以内部 `request_id` 命名。

目录路径只能由内部 Request ID 构造，禁止把客户端值、URL、用户名或任意输入拼接进路径。

### 9.4 权威事件流

`events.jsonl` 是追加式权威时间线，每行一个 JSON 事件，包含：

```text
seq
request_id
event
monotonic_ns
elapsed_ms
component
status
safe_data
```

标准事件至少包括：

```text
request.accepted
record.directory_created
request.headers_parsed
request.body_started
request.body.completed
route.match_started
route.matched
middleware.<name>.started
middleware.<name>.completed
handler.started
handler.completed
response.started
response.completed
cleanup.started
cleanup.completed
request.closed
```

异常事件包括协议拒绝、超时、取消、客户端断开、Handler 失败、Response 失败、Cleanup 失败和崩溃恢复。

序号在单请求内严格递增；耗时使用单调时钟；事件只追加，不修改历史。

### 9.5 “所有内容”的安全定义

所有内容指完整框架执行事实、阶段、调用摘要、时间线、错误和被策略允许的 Payload 快照。

默认禁止无条件落盘：

```text
Authorization
Proxy-Authorization
Cookie
Set-Cookie
Password
Secret
Token
API Key
私钥
数据库密码与完整连接串
未脱敏请求体和响应体
完整上传文件
完整 Python 本地变量
```

否则 Request Record 会成为大规模凭证和隐私泄漏源，违反安全框架目标。

### 9.6 Payload 捕获

每个请求必须记录 Body 元数据：Content-Type、大小、SHA-256、是否截断、是否脱敏和是否被策略禁止保存。

默认模式：

```text
metadata_only
```

可选：

```text
safe_fields
bounded_raw
disabled_for_route
```

必须有全局大小上限；Route 只能收紧，不能擅自放宽；JSON/Form 通过字段白名单和脱敏保存；二进制上传默认只保存元数据和摘要。

### 9.7 文件语义

- `manifest.json`：Schema、Request ID、App、Worker、进程、接收时间和初始状态；
- `request.json`：Method、Path Template、安全 Headers、Query 摘要、Client 和 Body 元数据；
- `routing.json`：Route、参数转换、匹配耗时和拒绝原因；
- `middleware.jsonl`：中间件阶段、顺序、耗时、短路和异常；
- `logs.jsonl`：本请求的结构化日志副本，自动注入 Request ID；
- `calls/*.jsonl`：数据库、缓存、外部 HTTP、消息和扩展调用摘要；
- `response.json`：状态码、Headers 摘要、Body 大小/摘要和写出结果；
- `error.json`：异常类型、安全摘要、发生阶段；
- `cleanup.json`：每个清理 Hook 和 ContextVar Reset 结果；
- `final.json`：最终状态、总耗时、事件数量、完整性和关闭时间。

数据库默认保存 SQL 指纹或模板，不保存未脱敏绑定参数。

### 9.8 状态与原子写

```text
open → closing → closed
```

异常终态：

```text
rejected
cancelled
timed_out
client_disconnected
failed
crashed
incomplete
```

JSON 快照先写临时文件再原子 rename；JSONL 只追加；重要里程碑刷新缓冲；`final.json` 最后写入；正常关闭后禁止继续写入目录。

### 9.9 写入架构和背压

```text
Request Execution
      ↓ structured events
Per-worker Bounded Record Queue
      ↓
Runtime Record Writer
      ↓
Request Directory
```

队列必须有界，不允许无限内存增长或静默丢事件。队列接近上限时对请求施加背压；持续不可用时 readiness=false；请求正常结束前必须确认 Final Record 已提交。

### 9.10 崩溃恢复

启动时扫描没有 `final.json` 的旧目录，追加恢复事件，并生成状态为 `crashed` 或 `incomplete` 的 `final.json`。恢复过程不得自动重放业务请求。

### 9.11 权限和路径安全

默认目标：

```text
POSIX directory 0700
POSIX file      0600
Windows         仅服务账户与明确管理员
```

必须防御符号链接替换、路径穿越、临时文件竞态、外部 Request ID 注入和任意文件读取。Runtime 目录绝不能被静态文件服务暴露。

### 9.12 保留和容量

必须配置：

```text
retention_days
max_total_bytes
max_request_count
min_free_disk_bytes
cleanup_interval
```

永不清理 Open 目录；优先清理超过 TTL 的 Closed/Rejected 目录；达到磁盘安全线时 readiness=false；清理操作必须审计；`runtime/` 必须加入 `.gitignore`。

### 9.13 调试查询

```bash
lingshu debug request <request_id>
lingshu debug request <request_id> --timeline
lingshu debug request <request_id> --calls
lingshu debug request <request_id> --errors
```

开发环境可以提供受保护的 Inspector：

```text
GET /__lingshu/debug/requests/{request_id}
```

Inspector 只能按 Request ID 读取结构化记录，不接受任意文件路径。Production 默认关闭；启用必须认证、授权、来源限制和审计。

### 9.14 后台任务

后台任务生成新的 `operation_id` 和独立目录：

```text
runtime/operations/<date>/<operation_id>/
```

Operation Manifest 保存 `parent_request_id`。后台任务不得继续持有 Request 对象或 Request Scope Resource。

---

## 10. 错误码与语言资源

归属：

```text
Core      → Core 错误
HTTP      → HTTP/Server 错误
Extension → 扩展错误
Project   → 业务错误
```

每个包携带自己的 Registry 和 Catalog。启动时检查 Namespace、号段、Code、Key 和覆盖冲突。扩展不得修改 Core Registry，项目不得修改安装包资源。

---

## 11. 安全体系

默认：

- Debug 关闭；
- 错误脱敏；
- Header、Body、连接和时间均有上限；
- Proxy Header 默认不信任；
- Server Banner 最小化；
- CORS 默认关闭；
- Host 校验可配置；
- Cookie 安全属性明确；
- 日志和 Request Record 自动脱敏；
- Runtime 目录不公开；
- TLS 使用安全默认值。

安全测试必须覆盖 Fuzzing、Malformed HTTP、Request Smuggling、Slow Client、Disconnect、Header Injection、Path Traversal、Multipart Bomb、并发泄漏和取消泄漏。

---

## 12. 稳定性与性能

### 稳定性

- `asyncio.CancelledError` 必须传播；
- 所有资源有 Owner、Scope、Close、Timeout、Health 和 Rollback；
- 禁止裸 `asyncio.create_task`；
- App 状态不共享；
- Worker 资源独立；
- Request Context 不泄漏；
- Extension Registry 不使用进程级可变全局状态。

### 性能

- 流式读写和背压；
- 减少复制，优先 bytes/memoryview；
- 编译路由树和 Middleware Pipeline；
- 启动时编译依赖图；
- 运行时避免无界反射；
- 可选高性能 Parser；
- 可选 uvloop，但不成为必须依赖；
- 任何优化必须通过基准、协议和安全测试。

每请求目录会增加文件系统负担，因此必须用日期分层、有界写入队列、批量写、容量监控和背压保证可控，不允许为了性能静默丢失请求记录。

---

## 13. Python 支持

正式支持：

```text
Python 3.10
Python 3.11
Python 3.12
Python 3.13
Python 3.14
```

能力检测优先，版本判断集中在 Compat 层；不全局屏蔽弃用警告；新 Python 版本先进入预览 CI，通过后才扩大 `requires-python`。

---

## 14. 测试与发布门

测试层级：

```text
Unit
Contract
Integration
Protocol
Fuzz
Stress
Soak
Security
Packaging
Multi-platform
```

Request Record 必测：

1. 每个业务请求在路由前创建 Request ID 目录；
2. 目录名只能来自内部 Request ID；
3. 并发、多 App、多 Worker 不串目录；
4. Router、Middleware、Handler、Response 和 Cleanup 时间线完整；
5. DB/Cache/外部调用进入正确文件；
6. 正常、异常、超时、取消、断开和崩溃终态正确；
7. 目录创建失败时业务不执行；
8. 队列满时背压而不是丢事件；
9. Token、Cookie、密码等敏感数据不落盘；
10. Payload 捕获遵守大小和 Route 策略；
11. 权限、原子写和符号链接防御有效；
12. TTL、容量和磁盘安全线有效；
13. Inspector 不支持任意文件读取；
14. 请求结束后 ContextVar、文件句柄和 Scope 无泄漏。

发布必须验证 Wheel/Sdist、Clean Install、Metadata、`requires-python`、依赖范围、Import Smoke、Public API Snapshot、Changelog 和 Migration Guide。

---

## 15. 当前仓库处理原则

分为三类：

1. 吸收思想：Context、生命周期、错误码、测试方法；
2. 重写素材：Router、Middleware、Auth、Tenant、Database、CLI；
3. 淘汰：Sanic 绑定实现、Legacy Facade、永久 Compat、Auth 双轨、Tenant/Auth 耦合、Core 内 Model/BusinessModel。

不以旧项目兼容为前提。

---

## 16. 实施路线

### P0 总纲冻结

完成本 Blueprint、对应 ADR 和多多确认，不修改生产代码。

### P1 单仓多包骨架

建立 Packages、独立 Pyproject、CI、Build 和 Install 测试。

### P2 Application Kernel

实现 Config、Context、Lifecycle、Extension、Capability、Scope、Error 和 Task Registry。

### P3 HTTP Runtime

实现 Request、Response、Headers、BodyStream、Router、Middleware、Exception Pipeline 和 Streaming。

### P4 Runtime Request Record

先实现 Request ID、每请求目录、事件流、脱敏、原子写、Writer Queue、容量、恢复和 Inspector，再进入正式 Server 业务处理。

### P5 Native Server MVP

实现 asyncio TCP、Strict HTTP/1.1 Parser、连接状态机、Keep-Alive、Chunked、Timeout、Limits 和 Graceful Shutdown。

### P6 Security Hardening

完成 Fuzz、Smuggling、Slowloris、Header Validation、Proxy Trust 和 TLS Defaults。

### P7 Extension Runtime

实现 Manifest、DAG、Lifecycle、Rollback 和 Contract Test Kit。

### P8 基础扩展

Auth、Tenant、RBAC、i18n 和 Cache。

### P9 Data Extensions

Data Protocol、MySQL、PostgreSQL、Mongo 和 Redis。

### P10 CLI 与 Scaffold

新项目、扩展、Controller/Service/Repository 模板。

### P11 性能、多 Worker、WebSocket、OpenAPI、Observability

按独立阶段实施并测试。

### P12 1.0 冻结

冻结 Stable API、安全文档、扩展指南、发布流程和长期支持策略。

---

## 17. 后续治理

每个实现 Issue 必须引用：

1. Blueprint 章节；
2. 对应 ADR；
3. 当前实施阶段；
4. 前置条件；
5. 允许和禁止范围；
6. 不变量；
7. 测试合同；
8. 回滚点；
9. 退出条件。

发现 Blueprint 有问题时：

```text
停止实现
→ 新建架构修订 Issue
→ 修改 Blueprint/ADR
→ 多多确认
→ 恢复实施
```

禁止在局部实现 PR 中悄悄改变总体设计。

---

## 18. 当前冻结候选决策

1. LingShu 是完全独立的 Python Framework；
2. 不依赖 Sanic 或其他上层 Web Framework；
3. 不承担旧项目兼容义务；
4. Core、HTTP Runtime 和 Native Server 均由 LingShu 定义；
5. TLS 使用 Python/OpenSSL，不自造密码学；
6. 第一阶段正式支持 HTTP/1.1；
7. Auth、Tenant、RBAC、Data、Cache、i18n 为独立扩展；
8. Model/BusinessModel 不进入 Core；
9. 不建立永久 Compat 层；
10. 采用单仓多包；
11. Python 3.10～3.14；
12. 安全、稳定和可测试优先于极限性能；
13. 每一个业务请求都必须拥有内部 Request ID；
14. 每一个请求必须在 `runtime/requests/<date>/<request_id>/` 创建独立 Request Record；
15. Request Record 无法创建时，默认不得进入业务处理；
16. 所有框架可观测事实必须记录，原始敏感数据必须按安全策略捕获；
17. 本 Blueprint 在多多确认并合并前不启动生产实现。
