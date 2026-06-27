# P0 Blueprint Review Checklist

用于多多与小顾冻结 LingShu Framework Blueprint v0.6 前的最终检查。

## 定位

- [ ] LingShu 是独立 Python Framework，不依赖 Sanic 等上层框架；
- [ ] 当前旧代码只作为素材，不形成兼容约束；
- [ ] 1.0 前不保留永久 Compat。

## 包与依赖

- [ ] 单仓多独立 distribution；
- [ ] `lingshu-core`、`lingshu-http`、`lingshu-record`、`lingshu-server` 边界清晰；
- [ ] Core 不反向依赖 HTTP、Record、Server 或扩展；
- [ ] Auth、Tenant、RBAC、Data、Cache、i18n 为独立扩展。

## 目录

- [ ] 仓库整体目录固定；
- [ ] Core 目录固定；
- [ ] HTTP 目录固定；
- [ ] Record 目录固定；
- [ ] Server 目录固定；
- [ ] CLI、总入口与扩展模板固定。

## 运行模型

- [ ] ProcessManager / Worker 模型固定；
- [ ] 启动、回滚、Readiness 和关闭流程固定；
- [ ] 单请求 28 步运行链固定；
- [ ] Request/Response 状态机固定；
- [ ] Deadline、Cancellation、Backpressure 和 Permit 语义固定；
- [ ] Supervision 与 Health 语义固定。

## Request Record

- [ ] 每请求生成内部 Request ID；
- [ ] 每请求创建独立 Runtime Record；
- [ ] 创建失败时不得进入业务；
- [ ] Telemetry Event Bus 是唯一观测入口；
- [ ] 敏感数据、原子写、恢复、容量、权限和 TTL 策略明确。

## 开发质量

- [ ] 公共 API Docstring 100%；
- [ ] 公共 API 类型标注 100%；
- [ ] 安全、并发、状态机、资源所有权必须有设计注释；
- [ ] TODO 必须关联 Issue 和删除条件；
- [ ] 严格静态类型、文档、测试和构建质量门明确。

## 准备实施

- [ ] ADR-006 与 Blueprint 一致；
- [ ] P1 Readiness 范围仅为多包骨架和质量门；
- [ ] P1 不实现 HTTP、Server、Auth、Data 或兼容；
- [ ] 多多明确确认 P0 冻结；
- [ ] 冻结后才创建 P1 实施 Issue 和开发分支。
