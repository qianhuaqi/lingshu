# LingShu Framework 总体架构设计总纲（P0-RC4）

- 设计负责人：小顾
- 产品决策人：多多
- 状态：P0 候选总纲，尚未最终冻结
- GitHub Issue：#25
- 规范仓库：`qianhuaqi/lingshu`
- 治理基线：latest accepted `main`
- 已接受决策：ADR-001、ADR-002、ADR-003、ADR-004
- 决策状态表：`docs/architecture/P0_DECISION_STATUS.md`
- 历史候选稿：`docs/architecture/candidates/LINGSHU_FRAMEWORK_BLUEPRINT_V0.6_CANDIDATE.md`

> 本文件是当前唯一总体架构入口。只有已由多多确认，并在
> `P0_DECISION_STATUS.md` 标记为 Confirmed 的内容，才能成为实施依据。
> P0 结束前不得创建生产源码、包骨架、运行时依赖或发布配置。

---

## 1. 根本定位

LingShu 是从零开发、完全独立、自主可控的 Python Web/API Framework。

LingShu 不是 Sanic、FastAPI、Flask、Django、Starlette 或其他上层 Web
Framework 的封装、适配层或迁移版本，也不承担历史实现兼容义务。

LingShu 自己定义并控制：

- Application Kernel；
- HTTP Runtime；
- Native Server；
- Request、Response、Router、Middleware 与 Streaming；
- 生命周期、并发、取消、清理、容量和背压；
- Extension Protocol；
- Request ID 与请求级 Runtime Record；
- CLI、测试支持和后续生态。

## 2. 历史实现边界

旧实现封存于：

```text
archive/legacy-sanic-20260628
```

封存提交：

```text
b869270e0ec7cbc324d17ef246e39d0873aab14f
```

旧源码、测试、依赖、脚手架、Issue、PR 和 API：

- 只可作为历史参考；
- 不作为新框架代码基线；
- 不产生兼容义务；
- 不允许直接复制到新框架；
- 有价值的思想必须重新进入 Issue、架构评审和新实现。

## 3. 已确认的最高原则

### 3.1 自主框架内核

核心运行能力由 LingShu 自行设计和实现，不通过安装其他上层 Web 框架获得。
Python 标准库可以作为语言基础；核心第三方依赖必须逐项评审并另立 ADR。

### 3.2 机制与政策分离

核心只提供通用机制，不把 JWT、Tenant、RBAC、数据库、ORM、Redis、用户、订单
等具体政策或业务模型写入核心。

### 3.3 单向、无环依赖

依赖必须显式、无环并可由机器检查验证。下层不得反向依赖业务能力、具体集成、
项目代码、测试工具或根级公共 facade。

### 3.4 显式生命周期

禁止通过 import 副作用注册、建连、启动任务、打开文件或修改进程级全局状态。
启动、运行、排空和关闭必须有明确状态、有界预算、失败回滚、逆序清理、幂等关闭
和可观测结果。

### 3.5 默认隔离与有界

App、Worker、Connection、Request、Operation 和 Extension 状态按 Scope 隔离。
连接、队列、请求体、Header、任务、重试、缓存、日志、执行器、Runtime Record 和
磁盘使用必须有上限、背压或拒绝策略。

### 3.6 Deadline、取消与清理

Deadline 是整条调用链共享的绝对 monotonic 预算，子调用只能继承或缩短。
取消必须传播，不得静默吞掉；任何退出路径都必须执行确定性、有限时清理。

### 3.7 安全优先

- 协议歧义直接拒绝；
- 敏感信息默认不记录；
- 不自造密码学、TLS 或证书验证；
- 安全、正确性和可恢复性优先于未经验证的极限性能。

## 4. 单仓库与开发并发（ADR-001）

规范仓库：

```text
qianhuaqi/lingshu
```

- 一个任务对应一个 Issue、一个分支、一个主写入者和一个 PR；
- 并行开发者使用独立 worktree/clone、虚拟环境、运行目录、缓存和端口；
- Issue 声明写入范围、依赖和集成顺序；
- 重叠路径或同一公共契约禁止并行；
- 公共契约和基础能力先合并；
- 开发可并行，进入 `main` 必须串行；
- 最终合并权属于项目负责人。

## 5. 运行时并发模型（ADR-002）

### 5.1 Worker 与所有权

- 标准库 `asyncio` 语义是正确性基线；
- 每个 Worker 进程拥有一个事件循环和一个 Application Runtime；
- Supervisor 管理 Worker、就绪、信号、有限重启和最终退出；
- Worker 不共享可变 Python 应用状态；
- 单 Worker 是语义基线，多 Worker 只扩展吞吐。

```text
Supervisor
└─ Worker
   └─ Application Runtime
      ├─ Infrastructure tasks
      ├─ Application-owned background tasks
      └─ Connection
         └─ Request
            └─ Operation / child tasks
```

未登记 fire-and-forget 任务被禁止。请求中创建的任务默认归 Request 所有。
长期任务必须显式登记并声明启动、停止、失败、重启和关闭策略。

### 5.2 HTTP/1.1 与资源控制

- 一个 HTTP/1.1 连接同一时刻执行一个请求；
- 多连接可以并发；
- Keep-Alive 请求顺序处理；
- 初始版本不并发执行 pipelined 请求或乱序响应；
- Worker、连接、请求、路由、后台任务、执行器、依赖、Telemetry 和 Record 队列均有界；
- 网络、解析、请求体、业务、依赖、响应流和写入形成完整背压链。

### 5.3 Blocking、崩溃与关闭

- Blocking I/O 使用有界线程执行器；
- CPU 密集工作使用有界进程执行器或外部任务系统；
- Worker 启动失败逆序清理；
- Worker 重启具有预算、速率限制和退避；
- 崩溃循环耗尽预算后停止自动重启。

运行状态：

```text
STARTING → RUNNING → DRAINING → STOPPING → STOPPED
```

关闭依次停止准入、排空、取消、停止后台任务、逆序关闭扩展、刷新记录、关闭
Transport/执行器、退出 Worker，并在 hard-stop Deadline 后强制终止残留进程。

详细规范：

- `docs/decisions/ADR-002-runtime-concurrency-model.md`；
- `docs/architecture/RUNTIME_CONCURRENCY_MODEL.md`。

## 6. 打包、源码与组件布局（ADR-003）

```text
Repository:          qianhuaqi/lingshu
Distribution:        lingshu
Import package:      lingshu
Packaging file:      pyproject.toml
Production source:   lingshu/
src layout:          prohibited
```

初始框架采用一个 distribution、一个 import package、一个根级 `pyproject.toml`、
一个版本和一个发布节奏。不使用 `src/lingshu/`、初始 `packages/` monorepo 或独立
`lingshu-core`、`lingshu-server` 等组件包。

目标组件：

```text
lingshu.core
lingshu.runtime
lingshu.http
lingshu.server
lingshu.record
lingshu.extensions
lingshu.cli
lingshu.testing
```

依赖方向：

```text
runtime     → core
http        → runtime + core
server      → http + runtime + core
record      → core + stable runtime contracts
extensions  → core + runtime (+ documented HTTP contracts when required)
cli         → public composition surface
testing     → public/test-support surfaces
```

禁止依赖环、下层导入根 facade、生产代码导入 `testing`、以及未经决策的跨组件私有
模块导入。

`lingshu/__init__.py` 是受控 public facade，采用显式 `__all__`。深层 import 默认
私有。可选集成只在激活时加载，不得成为隐藏 Core 依赖。

因为不使用 `src/`，打包验收必须构建 wheel/sdist、在全新环境中非 editable 安装、
切换到仓库外测试、禁止仓库 `PYTHONPATH` 注入，并核验安装文件与 metadata。

详细规范：

- `docs/decisions/ADR-003-package-source-layout-and-component-boundaries.md`；
- `docs/architecture/PACKAGE_AND_COMPONENT_LAYOUT.md`。

## 7. Application Kernel 与请求执行管线（ADR-004）

P0-D4 已通过 PR #41 接受。

### 7.1 Public facade 与内部 Kernel

公开应用类型是 `LingShu`，它是组件组合和注册 facade。

内部 Application Kernel 位于 `lingshu.core` 的私有机制中，负责生命周期状态、
注册目录、Application Revision、freeze 校验、不可变 Application Plan 和资源
生命周期契约。Kernel 不拥有 Listener、HTTP Parser 或业务政策，也不得依赖
`lingshu.server`。

### 7.2 Application 生命周期与 freeze

```text
CREATED
→ CONFIGURING
→ FROZEN
→ STARTING
→ RUNNING
→ DRAINING
→ STOPPING
→ STOPPED
```

- Route、Middleware、Exception Mapper、Extension、配置和 Hook 只在 freeze 前注册；
- freeze 校验完整 Revision 并原子发布不可变 Plan；
- 未变化 Revision 的 freeze 幂等；
- freeze 失败不发布部分 Plan；
- RUNNING 状态的注册目录不可变；
- 未来热更新必须创建新 Revision 并原子切换，禁止原地修改运行计划。

Freeze 至少验证配置、扩展依赖、Route 冲突、Middleware 顺序、Exception Mapper、
Handler 签名、生命周期顺序和资源预算。

### 7.3 Route 与 Handler

Route 声明包含规范化 path、显式 method 集、Handler、可选 name、Route Middleware、
metadata、能力要求和以后批准的 Body/Response Policy。

- 注册顺序不是冲突解决规则；
- 重复或歧义 Route 在 freeze 失败；
- 静态和动态段使用显式 specificity 规则；
- 404 与 405 区分；
- 编译 Router 不可变并支持并发读。

初始 Handler：

```python
async def handler(request: Request) -> Response | SupportedReturnValue:
    ...
```

初期只接受异步 Handler 和一个显式 Request。Path 参数通过 Request 读取；Core 不做
自动依赖注入，也不把同步 Handler 直接放在事件循环执行。

### 7.4 Middleware

采用 Application Middleware 和 Route Middleware 两层确定性洋葱模型：

```python
async def middleware(request: Request, call_next: Next) -> Response:
    ...
```

- priority 数值越小，入口越早、出口越晚；
- 同 priority 使用当前 Revision 内显式注册序号；
- Application Middleware 包裹路由匹配和 Route pipeline；
- Route Middleware 只在匹配后执行；
- egress 严格逆序；
- Middleware 可以直接返回 Response 短路；
- `call_next` 只能调用一次且不能脱离当前 Scope；
- import 顺序不是 Middleware 顺序。

### 7.5 固定请求管线

```text
1. Server 接受协议请求
2. 创建 Request Scope 与绝对 Deadline
3. 分配身份并打开 Runtime Record
4. 构造不可变 Request 与有界 Body Stream
5. Worker/Application 准入
6. Application Middleware 入口
7. Route 匹配
8. Route 准入和 Capability 检查
9. Route Middleware 入口
10. 异步 Handler
11. Handler 返回值规范化为 Response
12. Route Middleware 出口
13. Application Middleware 出口
14. 未处理异常兜底
15. 最终准备 Response metadata/body policy
16. 提交 Response head
17. 在背压下发送 Body/Stream
18. 完成 Runtime Record
19. 取消/等待残留请求任务
20. 释放 Body、准入、Context 和 Scope 资源
```

每个阶段都必须可观测，并遵守 Deadline、取消、准入、记录和清理规则。

### 7.6 Request

- Request 归一个 Request Scope 所有；
- method、target、scheme、authority、path、query、protocol、headers、连接信息和身份只读；
- Route match 后增加只读 Route 身份和 path params；
- 可变应用数据放显式 request-scoped state；
- Extension state 使用 namespace 或 typed capability；
- Body 是有界、背压、单消费者 stream；
- 缓存和 decode 必须显式且受限；
- Scope 完成后访问 Request/Body 明确失败；
- 敏感数据默认脱敏。

### 7.7 Return Normalization

Handler 返回值只规范化一次。

初始支持：

- `Response`；
- `str`；
- bytes-like；
- structured value 需等待序列化决策。

默认拒绝 `None`、tuple response magic、任意 iterator/generator 和未知对象。
Middleware 必须返回 Response。

### 7.8 Response 与 commit

```text
NEW → PREPARED → COMMITTED → COMPLETED
                  ↘          ↘
                   ABORTED ← ABORTED
```

- commit 前可修改或替换 status、headers、cookies 和 body policy；
- `PREPARED` 已完成 framework finalization 但尚可替换；
- Transport 接受最终 Response head 时进入 `COMMITTED`；
- commit 后 status/headers 不可变；
- 每个请求最多 commit 一次；
- pre-commit exception 可生成替代 Response；
- post-commit failure 不得生成第二个 Response，只能按协议终止流/连接并记录；
- double commit、commit 后修改、完成后写入均为 framework error。

### 7.9 Exception

映射顺序：

1. 最具体 Route Mapper；
2. 最具体 Application Mapper；
3. 内置 `HTTPException`；
4. commit 前安全默认内部错误 Response。

同级歧义在 freeze 失败。Mapper 返回 Response；Mapper 自身失败时记录原异常和
Mapper 异常，并在 commit 前安全兜底。取消不得被普通异常路径转换为正常业务响应。
commit 后不能替换 Response。

### 7.10 Extension

Extension 可在配置阶段贡献 schema、capability、route、middleware、exception mapper、
lifecycle hook 和已批准的 Record/Telemetry sink。

freeze 解析依赖并编译贡献；启动按依赖顺序，关闭按逆序；请求期间只能通过编译后的
Hook、Capability 和 Scoped State 工作，不得修改注册目录。

### 7.11 最小公开 API

```python
from lingshu import LingShu, Request, Response, HTTPException
```

```python
from lingshu import LingShu, Request, Response

app = LingShu()

@app.get("/")
async def index(request: Request) -> Response:
    return Response.text("hello")
```

公开概念包括 LingShu、Request、Response、HTTPException、Route decorators、
Middleware registration、Exception Mapper registration 和 Extension registration。

Kernel、Plan、Matcher、Middleware compiler、Normalizer、Commit controller、Parser、
Transport 和 Record storage internals 保持私有。

详细规范：

- `docs/decisions/ADR-004-application-kernel-request-pipeline-and-public-api.md`；
- `docs/architecture/APPLICATION_KERNEL_AND_REQUEST_PIPELINE.md`。

## 8. Request ID 与 Runtime Record 已确认原则

每个进入业务处理的请求拥有内部 Request ID 和独立、可审计的 Runtime Record。

记录覆盖连接、解析、准入、路由、中间件、Handler、子任务、外部调用、Response、
异常、取消、提交、流式发送和最终清理。

必须具备默认脱敏、大小/容量限制、TTL、原子写入、权限安全、背压、磁盘安全线、
崩溃恢复、写入失败和 flush timeout 处理。

具体标识格式、事件 Envelope、存储格式、磁盘预算和恢复细节进入 P0-D5。

## 9. 当前禁止事项

P0 冻结前禁止：

- 创建生产 `lingshu/` 目录、`tests/` 骨架或 `pyproject.toml`；
- 创建 `src/lingshu/` 或初始 `packages/` 结构；
- 引入运行时依赖；
- 实现 Kernel、Runtime、HTTP、Server、Record、CLI 或 Extension；
- 发布安装包；
- 建立 Sanic 适配、迁移层或旧 API 兼容层；
- 多个开发者共享同一可写目录或分支；
- 并行任务修改重叠路径或同一公共契约；
- 启动 P1。

## 10. 下一项：P0-D5 Hardening Foundations

P0-D5 应统一收拢：

1. Request、Connection、Trace、Operation、Worker、Revision 与 Runtime Record 标识规范；
2. Exception 分类、稳定 Error Code、安全 Client Message、Cause Chain 和 Redaction；
3. Configuration 来源、优先级、Schema、Validation、Immutability、Version、Reload 和 Rollback；
4. JSON/通用 Serialization 与 Content Negotiation 基线；
5. Runtime Record Event Envelope、存储格式、大小预算、Retention、Disk Safety、Failure Mode 和 Crash Recovery；
6. Telemetry 公共字段、Correlation 和时间字段规范。

## 11. 其他尚未确认项

- cookie、form、multipart、upload 与高级 body API；
- automatic HEAD/OPTIONS；
- host routing、reverse routing、mount 和 sub-application；
- public run/serve 与 CLI 行为；
- sync Handler adaptation；
- dependency injection；
- Auth、Tenant、RBAC、Data、SQL、Redis、Cache、i18n、OpenAPI、Resilience、Scheduler、Storage、WebSocket；
- HTTP/2、HTTP/3 与可选加速器；
- Python/平台支持范围；
- build backend、权威 version source、optional extras；
- P1/v0.x 路线、首个 PyPI 发布和 v1.0 API freeze；
- License、贡献、安全披露、支持版本、Changelog 和 Code of Conduct。

## 12. 决策确认流程

候选或提案只有同时满足以下条件才成为 Confirmed：

1. GitHub Issue 写明问题和选择；
2. Blueprint 修改或 ADR；
3. 多多明确确认；
4. PR 审查并合并；
5. `P0_DECISION_STATUS.md` 同步。

## 13. P0 退出条件

P0 只有满足以下条件才能结束：

1. 本总纲由多多确认；
2. 所有已接受 Hardening 内容并入本文件；
3. 不存在第二份同级总体设计；
4. distribution、源码、组件和扩展结构已确认；
5. Kernel、HTTP、Server、Runtime Record 职责和执行合同已确认；
6. 启动、请求、响应、并发、关闭和崩溃恢复语义已确认；
7. P1 范围和验收标准可直接写入 Issue；
8. 旧实施 Issue 已关闭或历史化；
9. 多多明确授权启动 P1。

在此之前，所有开发模型只允许执行 P0 文档与治理工作。
