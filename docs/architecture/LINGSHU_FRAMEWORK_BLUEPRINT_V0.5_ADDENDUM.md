# LingShu Framework Blueprint v0.5 规范性增补

- 对应基础总纲：`LINGSHU_FRAMEWORK_BLUEPRINT.md` v0.4
- Issue：#25
- 状态：规范性架构增补，待多多最终确认
- 优先级：本文件对 v0.4 中同类主题具有更高优先级
- 后续动作：总纲冻结前必须把本增补合并回唯一 Blueprint 文件

本增补不是功能愿望清单，而是对 Rust、Go、Elixir/Erlang、Java、.NET、Node.js、Ruby 和 Python 代表性框架的机制审查后，正式吸收进 LingShu 的长期架构合同。

---

## 1. Application Plan：把动态工作前移

LingShu 吸收 Micronaut、Quarkus 的“尽量在构建或启动阶段处理元数据”的思想，但不复制 JVM 字节码生成模式。

定义确定性的 `ApplicationPlan`：

```text
discover
→ validate
→ compile
→ fingerprint
→ freeze
```

Plan 必须包含：

```text
extension dependency DAG
provider/scope graph
route tree
module context tree
service/layer graph
handler extraction plan
input validators
output serializers
error/catalog registry
configuration schema
telemetry event registry
health check registry
runtime record policy
security policy summary
```

硬性规则：

- 请求热路径禁止重新扫描模块、装饰器、类型签名和扩展；
- 路由冲突、依赖循环、Scope 捕获、Layer 顺序、Schema 覆盖和错误码冲突在启动前失败；
- 同一输入必须得到同一 fingerprint；
- 开发模式可启动时编译；生产环境支持 `lingshu build-plan`；
- 启动时验证源码、配置、扩展、Python 版本和 Plan fingerprint；
- fingerprint 不一致时拒绝旧 Plan；
- 不使用不安全 `pickle` 作为持久化格式；
- 第一阶段只生成可读、可审计的结构化 Plan；
- 任何不透明代码生成、C/Rust 加速或二进制 Plan 必须另立 ADR。

配置字段必须标记：

```text
build_time
startup_fixed
runtime_reloadable
secret
```

---

## 2. Service / Layer / Permit：统一容量与横切策略

LingShu 吸收 Rust Tower 的 `Service`、`Layer` 和 readiness/backpressure 思想。

Python 合同：

```python
class Service(Protocol[RequestT, ResponseT]):
    async def acquire(self, context: ExecutionContext) -> ServicePermit:
        ...

class ServicePermit(Protocol[RequestT, ResponseT]):
    async def call(self, request: RequestT) -> ResponseT:
        ...

class Layer(Protocol):
    def wrap(self, inner: Service) -> Service:
        ...
```

先取得 Permit，再调用服务。Permit 表示容量已经为当前调用预留，避免单独 `ready()` 与 `call()` 之间的并发竞态。

用途：

```text
handler service
middleware/layer
timeout
concurrency limit
rate limit
load shedding
retry
circuit breaker
outbound HTTP
message producer
extension capability
runtime record writer
```

规则：

- 容量和背压必须向调用方传播；
- 无容量时不得无限排队；
- Layer 顺序进入 Application Plan；
- 请求已发送响应字节后禁止自动重试；
- Layer 必须声明 Streaming 安全性；
- Service/Layer 是 Core 机制，具体重试、熔断等策略属于独立扩展。

---

## 3. Typed Extractor / Pipe：Handler 参数就是输入合同

LingShu 吸收 Axum Extractor 与 NestJS Pipe 的优点。

目标用法：

```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: Path[int],
    page: Query[int] = 1,
    principal: Principal = Inject(),
) -> UserOutput:
    ...
```

启动时编译 `ExtractionPlan`：

```text
path/query/header/cookie extraction
→ type conversion
→ structural validation
→ capability injection
→ body decode
→ handler
→ output serialization
```

硬性规则：

- 提取顺序确定且可解释；
- Request Body 只能被一个消费型 Extractor 消耗；
- 消费 Body 的 Extractor 必须位于计划末端，否则启动失败；
- Path/Query/Header 转换失败时 Handler 不执行；
- 结构校验禁止访问数据库和外部服务；
- 业务校验必须进入显式 PreHandler Service；
- 自定义 Extractor 必须声明是否消费 Body、是否异步、所需 Capability 和失败类型；
- Extractor 失败进入统一 Error Pipeline、Telemetry 和 Request Record。

---

## 4. Schema 编译与响应字段白名单

LingShu 吸收 Fastify 的 Schema 驱动验证与序列化思想。

每个 Route 可声明：

```text
path schema
query schema
header schema
cookie schema
body schema per content-type
response schema per status/content-type
```

启动时编译：

```text
validator
normalizer
serializer
redaction policy
OpenAPI metadata
```

安全规则：

- Parser 接受的每一种 Content-Type 必须有对应 Schema 或显式标记；
- Production 默认拒绝“已解析但未验证”的内容类型；
- 初始结构校验禁止异步数据库访问，避免验证阶段 DoS；
- Response Serializer 以输出 Schema 作为字段白名单；
- Unknown Field 策略必须显式：`reject / ignore / preserve`；
- 类型转换必须可审计，不进行含糊转换；
- 动态用户 Schema 不得直接编译执行；
- Validator/Serializer 编译结果进入 Application Plan；
- Schema Engine 不强制绑定 Pydantic，官方可以提供适配扩展。

---

## 5. ModuleContext：模块和路由组默认隔离

LingShu 吸收 Fastify Encapsulation Context 的作用域隔离思想。

子 Context 默认继承父 Context 的：

```text
providers
layers
hooks
schemas
configuration view
error handlers
telemetry policy
```

但：

- 父 Context 不得看到子 Context 私有能力；
- 兄弟 Context 互相隔离；
- 子能力只有显式 `export` 才能向上或跨模块公开；
- Route Group 绑定到唯一 ModuleContext；
- 配置覆盖只作用于当前 Context 和后代；
- Context 泄漏、循环依赖和重复导出在 System Check 阶段失败。

因此可以安全表达：

```text
/admin → Auth + RBAC
/public → 无 Auth
/v1 → 旧 Schema
/v2 → 新 Schema
```

而不是在 Handler 中堆条件判断。

---

## 6. Supervision Tree：后台组件必须受监督

LingShu 吸收 Erlang/Elixir OTP 的监督树思想，用于 Runtime Writer、连接维护器、消费者、Poller、Telemetry Reporter 和扩展后台任务。

每个组件声明 `ChildSpec`：

```text
name
factory
dependencies
scope
restart_policy
restart_strategy
shutdown_timeout
health_check
significant
```

重启策略：

```text
never
on_failure
always
```

监督策略：

```text
one_for_one
rest_for_one
one_for_all
```

并必须配置：

```text
max_restarts
restart_window
backoff
jitter
escalation
```

规则：

- Request Handler 失败只结束当前请求，绝不自动重新执行；
- 有副作用任务重启前必须满足幂等合同；
- 连续崩溃超过阈值后停止重启并标记 unhealthy；
- 监督事件进入 Telemetry 和 Runtime Record；
- 关闭时按依赖逆序 drain/stop/close；
- Supervisor 不得吞掉 `CancelledError` 或退出信号。

---

## 7. System Check Framework：问题在启动前暴露

LingShu 吸收 Django System Check 的思想并扩展到框架底层。

命令：

```bash
lingshu check
lingshu check --tag security
lingshu check --deploy
lingshu check --format json
```

类别：

```text
architecture
configuration
extensions
providers
routes
schemas
security
runtime
storage
server
packaging
deployment
```

每条检查有稳定编号，例如：

```text
LSH-CFG-001
LSH-ROUTE-003
LSH-SEC-012
```

返回：

```text
severity
message
hint
location
evidence
documentation
```

规则：

- `run`、`build-plan`、测试和发布前执行必要检查；
- ERROR/CRITICAL 默认阻止启动；
- Production 安全关键检查不得静默忽略；
- 抑制检查必须记录原因、责任人和到期时间；
- 扩展可以注册检查，但不得覆盖其他编号；
- 检查不得进入请求热路径。

---

## 8. Unified Telemetry Event Bus

LingShu 吸收 Phoenix Telemetry 和 Rails Instrumentation 的事件解耦思想。

组件只发出稳定、版本化事件；Request Record、日志、指标和 Trace 都是订阅者。

事件合同：

```text
name
schema_version
phase
monotonic_ns
system_time
measurements
safe_metadata
request_id
trace_id
span_id
operation_id
```

需要计时的操作统一发出：

```text
start
stop
exception
```

示例：

```text
lingshu.http.request.start
lingshu.http.request.stop
lingshu.http.request.exception
lingshu.router.match.stop
lingshu.service.call.stop
lingshu.extension.start.exception
```

规则：

- 事件名和字段属于公共合同；
- 单调时钟用于耗时；
- 组件不得绑定特定 Metrics/Tracing 厂商；
- Request Record Writer 是强一致订阅者，服从写入背压；
- 可选 Reporter 失败不得改变业务结果，但必须计数和告警；
- 高基数字段不得默认成为 Metrics Tag；
- 订阅者不得执行无界阻塞工作；
- 敏感数据在事件产生前脱敏；
- 扩展必须登记事件 Schema。

Request Record 的正确结构变为：

```text
Component
→ Telemetry Event
→ Request Record Sink
→ Structured Log Sink
→ Metrics Sink
→ Trace Sink
```

避免 Router、数据库、Cache 等分别直接操作请求目录。

---

## 9. Startup / Liveness / Readiness / Degraded

LingShu 正式分离四类健康状态：

```text
startup
liveness
readiness
degraded
```

语义：

- Startup：初始化是否完成；
- Liveness：进程和事件循环是否仍能工作，失败通常需要重启；
- Readiness：是否可以接收新流量；
- Degraded：仍可服务，但部分非关键能力下降。

规则：

- Liveness 不依赖数据库或外部 API，避免外部故障造成重启风暴；
- Readiness 聚合 required 扩展、磁盘、Request Record Writer、连接池等；
- 每个检查有 timeout、cache_ttl、tags 和安全详情；
- Startup 未完成前不接收业务请求；
- Draining 时 Liveness 可以健康，但 Readiness 必须失败；
- 健康变化进入 Telemetry 和审计记录。

---

## 10. Resilience Extension：弹性不是散落的装饰器

新增官方 `lingshu-resilience`，基于 Service/Layer 提供：

```text
timeout
concurrency limit
queue limit
rate limit
load shedding
retry
circuit breaker
bulkhead
fallback
```

硬性规则：

- Deadline 是总预算，Layer 不得各自重新获得完整超时；
- Retry 只能用于幂等操作或明确 Idempotency Contract；
- 已发送响应字节后禁止重试；
- Retry 有次数、总时间和全局预算；
- Circuit Breaker 状态范围必须声明 app/worker/route；
- Fallback 不得掩盖安全错误和一致性错误；
- Load Shedding 应早于昂贵 Body 解析和业务依赖；
- 每次重试、拒绝、熔断和恢复进入 Telemetry 与 Request Record。

服务器、Service、扩展和 Runtime Writer 都必须声明容量。普通请求不得通过无限排队耗尽内存。

---

## 11. Context 父子传播与所有权

LingShu 吸收 Go `context` 的 Deadline/Cancellation 父子传播思想。

`ExecutionContext` 传播：

```text
deadline
cancellation
request_id
trace context
principal snapshot
tenant snapshot
resource budget
```

规则：

- 入站请求创建根 Request Context；
- 下游调用创建派生 Context，不得丢失父 Deadline；
- 父取消传播给所有子级；
- 创建可取消子 Context 的代码负责关闭；
- 长生命周期对象不得保存 Request Context；
- Context 不是任意参数袋；
- 后台任务必须转换为独立 Operation Context。

---

## 12. Response Commit 与分支式 Pipeline

吸收 ASP.NET Core 有序 Pipeline、短路和 Response Started 的优点。

Response 状态：

```text
new
headers_committed
streaming
completed
aborted
```

Headers 一旦提交：

- 状态码和普通 Header 不得再修改；
- 后续 Layer 不得重新映射完整响应；
- 错误只能中止流或使用协议允许的 Trailer；
- Request Record 记录首次 commit 位置；
- Application Plan 检查可能在 commit 后写 Header 的非法 Layer 顺序。

Pipeline 可以按 Host、Path、Route Metadata 和安全域编译分支，但分支必须进入 Application Plan，不能运行时随意拼接。

---

## 13. 可解释开发工具

LingShu 不接受无法解释的自动装配。

CLI：

```bash
lingshu check
lingshu doctor
lingshu build-plan
lingshu inspect routes
lingshu inspect route <name>
lingshu inspect extensions
lingshu inspect providers
lingshu inspect layers
lingshu inspect config <key>
lingshu inspect health
lingshu explain request <request_id>
```

必须能够解释：

- Route 为什么匹配；
- Layer 为什么在这里；
- Provider 来源和 Scope；
- 配置最终值和 Source；
- 扩展为何启用；
- Response 字段为何被过滤；
- 请求在哪一步耗时或失败。

每个 Core/Extension 配置模型必须生成统一 JSON Schema，供 CLI、IDE、文档、环境变量映射和 Plan fingerprint 使用。未知配置默认报错。

---

## 14. 实施顺序修正

后续阶段调整为：

```text
P0  总纲冻结
P1  单仓多包骨架
P2  Core Kernel + System Check + Supervision
P3  Application Plan Compiler
P4  HTTP Runtime 基础
P5  Service/Layer + Extractor/Pipe + Schema + ModuleContext
P6  Unified Telemetry + Runtime Request Record
P7  Native Server MVP + Health States
P8  Security + Admission Control + Load Shedding
P9  Extension Runtime + Contract Test Kit
P10 Auth/Tenant/RBAC/i18n/Cache/Resilience
P11 Data Extensions
P12 CLI/Scaffold/Inspect/Doctor
P13 性能、多 Worker、Plan Cache
P14 WebSocket/OpenAPI/Observability
P15 1.0 冻结
```

---

## 15. 新增冻结候选决策

1. 路由、扩展、依赖、Layer、Schema 和配置必须编译为确定性 Application Plan；
2. 请求热路径禁止模块扫描、依赖图构建和动态 Schema 编译；
3. 使用 Service/Layer + Permit 统一容量、背压和横切策略；
4. Handler 输入采用 Typed Extractor/Pipe；
5. 输出采用 Schema 白名单序列化；
6. ModuleContext 子树默认隔离，能力只能显式导出；
7. 后台组件进入 Supervision Tree，并受重启强度和退避限制；
8. System Check 在启动和发布前阻止严重错误；
9. 所有框架观测统一通过版本化 Telemetry Event Bus；
10. Startup、Liveness、Readiness、Degraded 分离；
11. Retry、Circuit Breaker、Load Shedding 属于 Resilience 扩展，不污染 Core；
12. 所有自动装配必须可通过 Inspect/Explain 解释；
13. 配置生成机器可读 Schema，并标记 build/start/reload/secret 生命周期。

---

## 16. 官方资料依据

- Rust Tower Service/Layer: https://docs.rs/tower/latest/tower/trait.Service.html
- Rust Axum Extractors: https://docs.rs/axum/latest/axum/extract/index.html
- Elixir Supervisor: https://hexdocs.pm/elixir/Supervisor.html
- Phoenix Telemetry: https://hexdocs.pm/phoenix/telemetry.html
- Fastify Encapsulation: https://fastify.dev/docs/latest/Reference/Encapsulation/
- Fastify Validation/Serialization: https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/
- NestJS Pipes/Interceptors: https://docs.nestjs.com/pipes
- ASP.NET Core Middleware: https://learn.microsoft.com/aspnet/core/fundamentals/middleware/
- ASP.NET Core Health Checks: https://learn.microsoft.com/aspnet/core/host-and-deploy/health-checks
- Go Context: https://pkg.go.dev/context
- Micronaut Core Guide: https://docs.micronaut.io/latest/guide/
- Quarkus Extension Guide: https://quarkus.io/guides/writing-extensions
- Django System Check: https://docs.djangoproject.com/en/5.2/topics/checks/
- Rails Instrumentation: https://guides.rubyonrails.org/active_support_instrumentation.html
