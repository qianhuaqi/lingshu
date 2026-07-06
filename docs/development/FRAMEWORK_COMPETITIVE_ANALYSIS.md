# LingShu Framework 对标分析

状态：P5 架构参考文档
更新时间：2026-07-06

## 1. 目标

本文件用于回答三个问题：

```text
1. LingShu 当前优势是什么；
2. 主流框架有哪些优点值得学习；
3. 主流框架有哪些痛点是 LingShu 应重点解决的。
```

本文件不是宣传稿，不宣称 LingShu 当前已经优于成熟框架。当前结论是：

```text
LingShu 在架构控制、生命周期、安全诊断、无强制依赖方面有潜在优势；
但在生态、数据库、OpenAPI、认证、生产运行、文档成熟度方面明显落后。
```

## 2. 对标框架

重点参考：

```text
Python: FastAPI, Starlette, Django, Flask, Sanic, SQLAlchemy
PHP: Laravel
Ruby: Rails
Java: Spring / Spring Boot
Node.js: Express, NestJS
Go: Gin, Fiber, Echo
Rust: Axum, Actix Web
```

## 3. 主流框架优点

### 3.1 Laravel / Rails / Django

优点：

- 一体化体验强；
- 数据库、模型、迁移、认证、Session、模板、命令行工具成熟；
- 开发效率高；
- 文档和生态完整。

LingShu 应学习：

- 清晰的一体化开发体验；
- 官方数据库层；
- migration / model / command 的完整路线；
- 文档入口一致。

### 3.2 Spring / NestJS

优点：

- 模块化强；
- 依赖注入和生命周期成熟；
- 数据、消息、认证、配置、测试生态完整；
- 企业级扩展能力强。

LingShu 应学习：

- capability / module / provider 的边界；
- resource lifecycle；
- 配置、诊断、启动顺序；
- 大型项目的可维护性。

### 3.3 FastAPI / Starlette / Sanic

优点：

- async-first；
- API 开发体验好；
- FastAPI 的 OpenAPI 和类型体验强；
- Starlette 的 ASGI 抽象简洁；
- Sanic 的 async Web runtime 经验丰富。

LingShu 应学习：

- 类型友好的 API；
- OpenAPI / schema / validation；
- 测试客户端；
- async-first 开发体验。

### 3.4 SQLAlchemy

优点：

- SQL Core 与 ORM 分层清晰；
- dialect / engine / connection / pool / transaction 概念成熟；
- ORM 建立在 Core 之上，而不是和底层连接混在一起。

LingShu 应学习：

- 先做 database resource / driver；
- 再做 query / transaction；
- 最后再讨论 ORM / migration；
- 不把 ORM 和数据库资源层混成一个问题。

## 4. 主流框架痛点

LingShu 应重点解决这些痛点：

### 4.1 依赖过重

很多成熟框架功能很完整，但引入成本高。LingShu 应保持 core 轻量，把数据库、OpenAPI、认证等作为可选能力接入。

### 4.2 生命周期不够显式

部分框架允许 import-time 副作用、隐式连接、隐式注册。LingShu 应坚持：

```text
import 不建连
registration 不建连
startup 才建连
shutdown 必须清理
```

### 4.3 诊断不够安全

数据库 DSN、token、password、SQL、内部拓扑容易泄漏。LingShu 应把 redaction 作为底层契约，而不是后补功能。

### 4.4 魔法过多

部分框架为了开发效率加入大量隐式行为。LingShu 应保持显式、可审计、可测试。

### 4.5 扩展风格不统一

很多框架的第三方扩展体验不一致。LingShu 应建立统一入口：

```text
lingshu.db.mysql
lingshu.db.redis
lingshu.db.mongodb
```

## 5. LingShu 当前潜在优势

当前 LingShu 还不能说整体优于成熟框架，但有几个方向可以做得更好：

```text
1. 自主内核，不依赖上层 Web framework；
2. mandatory runtime dependencies 为空；
3. Application lifecycle 显式；
4. freeze / immutable plan 方向正确；
5. extension startup/shutdown 顺序已有基础；
6. redaction / safe diagnostics 已成为早期原则；
7. 可以从一开始把数据库、OpenAPI、Auth 做成可选模块，而不是污染 core。
```

## 6. LingShu 当前明显短板

```text
1. 生态为空；
2. 数据库层未实现；
3. OpenAPI / Validation 未实现；
4. Auth / Tenant / RBAC 未实现；
5. 生产 runtime 未实现；
6. 文档状态不同步；
7. 扩展契约还没有转化为统一资源层代码；
8. 还没有形成类似 Laravel / Django / Rails 的开发闭环。
```

## 7. 设计结论

LingShu 后续不能只追求“像某一个框架”。正确路线是：

```text
学习 Laravel / Rails / Django 的完整开发闭环；
学习 Spring / NestJS 的模块和资源生命周期；
学习 FastAPI 的类型和 OpenAPI 体验；
学习 SQLAlchemy 的数据库分层；
保持 LingShu 自己的轻量 core、安全诊断、显式生命周期。
```

当前最应该做的是：

```text
先建立 `lingshu.db` 数据库层总架构，
再进入 MySQL / Redis / MongoDB 驱动，
再进入 Query / ORM / Migration。
```
