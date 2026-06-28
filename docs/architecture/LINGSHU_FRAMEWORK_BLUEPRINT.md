# LingShu Framework 总体架构设计总纲（P0-RC1）

- 设计负责人：小顾
- 产品决策人：多多
- 状态：P0 候选总纲，尚未冻结
- GitHub Issue：#25
- 规范仓库：`qianhuaqi/lingshu`
- 治理基线：latest accepted `main`
- 已接受决策：ADR-001、ADR-002
- 决策状态表：`docs/architecture/P0_DECISION_STATUS.md`
- 历史详细候选稿：`docs/architecture/candidates/LINGSHU_FRAMEWORK_BLUEPRINT_V0.6_CANDIDATE.md`

> 本文件是当前唯一总体架构入口。只有已经由多多确认，并在
> `P0_DECISION_STATUS.md` 中标记为 Confirmed 的内容，才可以成为后续
> 实施 Issue 的依据。候选目录、分包、扩展和版本规划不得直接执行。

---

## 1. 根本定位

LingShu 是从零开发、完全独立、自主可控的 Python Web/API Framework。

LingShu 不是 Sanic、FastAPI、Flask、Django、Starlette 或其他上层 Web
Framework 的封装、适配层或迁移版本，也不承担历史实现的兼容义务。

LingShu 自己定义并控制：

- Application Kernel；
- HTTP Runtime；
- Native Server；
- Request、Response、Router、Middleware 与 Streaming；
- 生命周期、并发、取消、清理、容量和背压；
- Extension Protocol；
- Request ID 与请求级 Runtime Record；
- CLI、测试支持和后续生态。

这些职责已经确认；它们的最终 distribution、物理模块和源码目录仍需后续决策。

## 2. 历史实现边界

旧实现完整封存于：

```text
archive/legacy-sanic-20260628
```

封存提交：

```text
b869270e0ec7cbc324d17ef246e39d0873aab14f
```

旧源码、测试、脚手架、依赖、Issue、PR 和 API：

- 只可作为历史参考；
- 不作为新框架代码基线；
- 不产生兼容义务；
- 不允许直接复制到新框架；
- 任何仍有价值的思想都必须重新进入 Issue、架构评审和新实现。

## 3. 已确认的最高原则

### 3.1 自主框架内核

灵枢核心运行能力由灵枢自行设计和实现，不通过安装其他上层 Web 框架获得。

Python 标准库可以作为语言运行基础。核心第三方依赖必须逐项评审并另立 ADR。

### 3.2 机制与政策分离

核心只提供通用机制，不把 JWT、Tenant、RBAC、数据库、ORM、Redis、用户、
订单等具体政策或业务模型写入核心。

哪些能力属于默认安装、官方可选能力或第三方生态，仍需 P0 决策。

### 3.3 单向依赖

当前确认的是概念依赖方向，而不是最终物理包结构：

```text
Project Application
        ↓
Optional Capabilities / Extensions
        ↓
LingShu HTTP Runtime
        ↓
LingShu Application Kernel
        ↕
LingShu Native Server / Transport
```

Core 不得反向依赖具体业务能力、数据库驱动、认证实现或项目代码。

### 3.4 显式生命周期

禁止通过 import 副作用完成注册、建连、启动任务或修改进程级全局状态。

启动、运行、排空和关闭必须具备：

- 明确状态；
- 有界时间预算；
- 失败回滚；
- 逆序清理；
- 幂等关闭；
- 可观测结果。

### 3.5 默认隔离

App、Worker、Connection、Request、Operation 和 Extension 状态必须按作用域隔离。

禁止把当前请求、事务、用户或其他请求级可变状态保存为进程级普通全局变量。

### 3.6 默认有界

连接、队列、请求体、Header、并发、任务、重试、缓存、日志、执行器、
Runtime Record 和磁盘使用都必须有明确上限、背压或拒绝策略。

### 3.7 取消与清理

Deadline 是完整调用链预算，不能在每层重新获得完整超时。

取消必须传播，不得静默吞掉；客户端断开、超时、应用排空、Worker 停止和人工
取消必须可区分。任何退出路径都必须执行确定性、有限时的清理。

### 3.8 安全优先

- 协议歧义直接拒绝，不猜测；
- 敏感信息默认不记录；
- 不自造密码学算法、TLS 算法和证书验证；
- 安全、正确性和可恢复性优先于未经验证的极限性能。

## 4. 单仓库与开发并发

LingShu 采用一个规范仓库：

```text
qianhuaqi/lingshu
```

框架核心、官方能力、测试、文档、示例、构建工具、安全测试和发布元数据原则上
在该仓库统一治理。除非未来 ADR 证明必须拆分，否则不另建组件仓库。

开发并发遵循 ADR-001：

- 一个任务对应一个 Issue、一个分支、一个主写入者和一个 PR；
- 每个并行开发者使用独立 worktree 或 clone；
- 每个工作区使用独立虚拟环境、运行目录、缓存和端口；
- Issue 必须声明写入范围、依赖关系和集成顺序；
- 写入范围重叠或修改同一公共契约时禁止并行；
- 公共契约和基础能力先合并，依赖任务再同步；
- 开发可以并行，进入 `main` 的集成必须串行；
- 最终合并权属于项目负责人。

单仓库不等于已经确认单 distribution、`packages/`、`src/` 或最终源码目录。

## 5. 运行时并发模型

P0-D2 已通过 ADR-002 和 PR #35 接受。

### 5.1 标准语义基线

- Python 标准库 `asyncio` 语义是正确性基线；
- 灵枢必须在没有第三方事件循环时正确运行；
- 未来可选加速器必须另立 ADR，并保持相同可观察语义。

### 5.2 Worker 与事件循环

- 每个 Worker 进程拥有一个事件循环和一个 Application Runtime；
- Supervisor 管理 Worker、就绪状态、信号、有限重启和最终退出状态；
- Worker 之间不共享可变 Python 应用状态；
- 跨 Worker 协作必须通过明确 IPC、数据库、缓存、消息或操作系统机制；
- 单 Worker 是语义基线，多 Worker 只扩展吞吐，不改变请求、取消和关闭语义。

### 5.3 结构化所有权

```text
Supervisor
└─ Worker
   └─ Application Runtime
      ├─ Listener / Infrastructure tasks
      ├─ Application-owned background tasks
      └─ Connection
         └─ Request
            └─ Operation / child tasks
```

- 所有任务必须有明确 Scope；
- 子 Scope 默认不能超过父 Scope 生命周期；
- 未登记 fire-and-forget 任务被禁止；
- 请求处理中创建的任务默认归 Request 所有；
- 长期后台任务必须显式登记为 Application 或 Worker 所有，并声明启动、停止、失败、重启和关闭策略；
- 脱离请求的后台任务不得继承请求上下文，除非显式复制安全值。

### 5.4 HTTP/1.1 并发

- 一个 HTTP/1.1 连接同一时刻最多执行一个请求；
- 多个连接可以并发；
- Keep-Alive 请求按顺序处理；
- 初始版本不并发执行 pipelined 请求，也不乱序输出响应；
- read-ahead、请求体和响应缓冲必须有界；
- HTTP/2 与 HTTP/3 多路复用另立决策。

### 5.5 准入与背压

并发限制至少覆盖：

- Worker 数和连接数；
- Worker、Application 与 Route 活跃请求数；
- 后台任务；
- 线程与进程执行器；
- 外部依赖调用；
- Telemetry 与 Runtime Record 队列。

所有等待队列必须有上限和等待 Deadline。容量耗尽时必须背压、有限等待、明确
拒绝或安全关闭连接，不能无限排队。

网络读取、解析、请求体、业务准入、执行器、外部依赖、响应流和网络写入形成
完整背压链。慢客户端不得无限占用 Worker 资源。

### 5.6 Deadline 与取消

- Deadline 使用绝对 monotonic time；
- 子操作只能继承或缩短 Deadline；
- 排队、中间件、路由、扩展、外部调用、流式处理和清理共同消耗剩余预算；
- wall-clock 只用于人类可读时间，不用于超时测量；
- 取消原因至少区分客户端断开、请求超时、服务排空、Worker 停止、父任务取消、应用取消和准入失败；
- 取消从所有者传播到子任务；
- 允许有限、明确的 cleanup shielding，但不能形成无限关闭延迟。

### 5.7 Blocking 与 CPU 工作

- Blocking 工作不得直接运行在 Worker event loop；
- Blocking I/O 进入有界线程执行器；
- CPU 密集工作进入有界进程执行器或外部任务系统；
- 执行器 Worker 数、提交队列和等待时间必须有界；
- 已运行线程任务的取消是 best-effort，结果可丢弃，但任务必须持续被统计和追踪。

### 5.8 Worker 崩溃与重启

- Worker 只有完成初始化后才能声明 ready；
- 启动失败按逆序清理；
- 异常退出可以有限重启，并带速率限制和退避；
- 重启预算耗尽后停止自动重启并标记服务不健康；
- 正确性语义不得依赖 fork 继承可变状态。

### 5.9 优雅关闭

运行状态：

```text
STARTING → RUNNING → DRAINING → STOPPING → STOPPED
```

关闭顺序：

1. 标记服务不再 ready；
2. 停止接受新连接；
3. 停止新请求和后台任务准入；
4. 在 graceful Deadline 内排空请求和响应流；
5. 取消剩余 Request 与 Operation Scope；
6. 停止 Application 后台任务；
7. 按启动逆序关闭扩展和外部资源；
8. 在有界预算内刷新 Runtime Record 与 Telemetry；
9. 关闭监听、Transport 和执行器；
10. Worker 退出，Supervisor 汇总状态；
11. hard-stop Deadline 到达后终止残留进程并记录强制关闭。

关闭操作必须幂等；重复信号可缩短宽限期，但必须保留清理结果记录。

### 5.10 Context、记录与测试

Connection、Request、Operation、Deadline、取消原因、身份和 Runtime Record 都是
Scope-local。

Runtime Record 与 Telemetry 管道必须有界，并报告队列深度、截断、丢弃、失败和
flush timeout。

实现验收必须覆盖并发短请求、Keep-Alive、pipelining、慢客户端、客户端断开、
容量打满、执行器饱和、父子取消、Deadline 不重置、Context 不串线、Worker 启动
失败、崩溃重启、排空与强停，以及任务、连接、文件、执行器和上下文泄漏。

详细规范见：

- `docs/decisions/ADR-002-runtime-concurrency-model.md`；
- `docs/architecture/RUNTIME_CONCURRENCY_MODEL.md`。

## 6. Request ID 与 Runtime Record

每个进入业务处理的请求必须拥有内部 Request ID，并建立独立、可审计的
Runtime Record。

记录范围覆盖连接、解析、路由、中间件、业务、外部调用、响应、异常、取消、
准入、队列等待、子任务和最终清理状态。

Runtime Record 必须具备：

- 捕获策略与默认脱敏；
- 大小、容量和队列限制；
- TTL 与清理；
- 原子写入；
- 权限和路径安全；
- 背压与过载策略；
- 崩溃恢复；
- 磁盘安全线；
- 写入失败和 flush timeout 处理。

具体目录、存储格式、独立 distribution 还是内部模块仍待确认。

## 7. 当前禁止事项

P0 冻结前禁止：

- 创建生产源码或暗示最终架构的目录骨架；
- 引入运行时依赖；
- 实现 Kernel、HTTP Runtime、Native Server、Router、Middleware 或扩展；
- 发布安装包；
- 建立 Sanic 适配、迁移层或旧 API 兼容层；
- 按历史候选稿直接创建 `packages/`、`src/` 或其他未确认目录；
- 多个开发者共享同一可写工作目录；
- 多个主写入者同时写同一分支；
- 两个并行任务修改重叠路径或同一公共契约；
- 启动 P1。

## 8. 尚未确认的架构决策

### 8.1 打包与源码布局

已经确认：只有一个规范仓库 `qianhuaqi/lingshu`。

仍未确认：

- 一个 Python distribution 还是同仓多 distribution；
- 是否使用 `packages/`；
- 是否使用 `src/` layout；
- 是否直接采用根级 `lingshu/`；
- tests、examples、tools、templates、benchmarks、fuzz 等目录位置；
- 一个还是多个 `pyproject.toml`。

### 8.2 组件边界

- Core、HTTP、Server、Record、CLI 是内部模块还是独立 distribution；
- 它们之间的最终依赖方向和公共导出；
- Runtime Record 是否默认内置；
- WebSocket、OpenAPI、Observability 等能力的归属。

### 8.3 官方能力与扩展

- Auth；
- Tenant 与 Tenant-Auth bridge；
- RBAC；
- Data、SQL 和数据库驱动；
- Cache 与 Redis；
- i18n；
- OpenAPI；
- Observability；
- Resilience；
- Scheduler 与 Storage。

这里列出的是能力候选，不代表已经批准独立 distribution。

### 8.4 P0-D2 明确延后

- Python 最低版本；
- Scope、Deadline、Limiter 与 Cancellation 的公共 API 名称；
- 默认并发和超时数值；
- 是否支持强制第三方事件循环或解析器；
- Worker 监听 Socket 分发策略；
- HTTP/2 与 HTTP/3 多路复用；
- 并发能力的物理模块和 distribution 位置。

### 8.5 发布与支持

- P1 后的实施阶段与 v0.x 映射；
- Python 与操作系统支持范围；
- 首个公开安装包的时机；
- v1.0 公共 API 冻结范围；
- License、贡献、安全披露、变更日志和发布政策。

## 9. P0 Hardening 合并要求

`P0_HARDENING_CHECKLIST.md` 是临时收敛清单，不是第二份总体架构。

P0-D2 已确认 monotonic Deadline、Async Context 隔离、Worker/连接/队列预算和
Telemetry 的部分要求。

冻结前仍须把其余确认内容并入本文件，包括：

- Request、Connection、Trace、Operation 等标识标准；
- 异常分类和敏感信息处理；
- 配置版本、校验、热更新和回滚；
- 序列化规则；
- Runtime Record 存储预算和磁盘策略。

并入完成后，清单必须归档或改为验收记录，避免形成双重事实源。

## 10. 决策确认流程

候选决策只有同时满足以下条件才成为 Confirmed：

1. GitHub Issue 中写明问题和选项；
2. Blueprint 修改或 ADR 记录最终选择；
3. 多多明确确认；
4. PR 经过审查并合并；
5. `P0_DECISION_STATUS.md` 同步状态。

聊天中的临时讨论不能直接覆盖仓库事实源。

## 11. P0 退出条件

P0 只有满足以下条件才能结束：

1. 本总纲由多多确认；
2. 所有已确认 hardening 内容已并入本文件；
3. 不存在第二份具有相同权威级别的总体设计；
4. 单仓库内的 distribution、源码和扩展结构已经确认；
5. Kernel、HTTP、Server、Runtime Record 的职责边界已经确认；
6. 启动、请求、响应、并发、关闭和崩溃恢复语义已经确认；
7. P1 范围和验收标准可直接写入 Issue；
8. 旧实施 Issue 已关闭或历史化；
9. 多多明确授权启动 P1。

在此之前，所有开发模型只允许执行 P0 文档和治理工作。
