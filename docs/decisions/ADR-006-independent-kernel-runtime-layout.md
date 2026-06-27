# ADR-006：独立 Kernel、HTTP、Record 与 Native Server 结构

- 状态：Proposed
- Issue：#25
- Blueprint：`docs/architecture/LINGSHU_FRAMEWORK_BLUEPRINT.md` v0.6
- 决策人：多多
- 设计负责人：小顾

## 背景

LingShu 的目标不是包装现有 Python Web Framework，而是拥有自主 Application Kernel、HTTP Runtime、每请求 Runtime Record 和 Native Server。若继续把这些职责放在单一 `lingshu` 包中，会导致依赖方向不清、网络层污染 Core、请求记录与业务组件耦合、测试矩阵无法拆分。

## 决策

采用单仓多独立 distribution：

```text
lingshu-core
lingshu-http
lingshu-record
lingshu-server
lingshu-cli
lingshu-framework
```

其中：

- Core 只提供配置、生命周期、Context、Extension、Capability、Service/Layer、Supervision、Health、Telemetry 和 System Check；
- HTTP 提供 Request/Response、Router、Middleware、Extractor、Schema、ModuleContext 和请求执行引擎；
- Record 提供每请求独立目录、事件写入、脱敏、恢复、保留和查询；
- Server 提供进程、Worker、TCP、HTTP/1.1、连接、Admission、背压和优雅关闭；
- Framework 只提供稳定薄入口；
- CLI 负责创建、运行、检查、Plan 编译和解释工具。

依赖方向：

```text
http   → core
record → core + http
server → core + http
framework → core + http + record + server + cli
```

Core 不得反向依赖其他包。

## 运行模型

- ProcessManager 管理不可变 ApplicationPlan、Listener、Worker 和信号；
- 每个 Worker 拥有独立 Event Loop、WorkerKernel、Supervision Tree、Telemetry Bus、Record Writer 和扩展资源；
- Worker 之间不共享可变业务状态；
- 请求行安全识别后生成 Request ID，并在继续解析 Header/Body 前创建 Runtime Record；
- 目录创建失败时不得进入业务执行；
- 请求结束后必须清理 Request Scope 并写入 final record。

## 代码文档标准

- 公共 API Docstring 与类型标注覆盖率 100%；
- 状态机、并发、背压、安全、资源所有权和回滚逻辑必须有设计注释；
- 源码注释和公共 Docstring 使用英文；
- TODO 必须关联 Issue 和删除条件；
- 行为变化必须同步更新注释、文档与测试。

## 后果

优点：

- Core 边界稳定；
- HTTP 和网络层可独立测试；
- Request Record 不污染业务组件；
- Windows/Linux 和 Python 版本兼容差异集中；
- 后续可以独立优化 Parser 和 Server。

代价：

- 多包构建与发布复杂度提高；
- 需要严格版本矩阵和合同测试；
- Native Server 与每请求文件记录需要长期协议、安全和性能验证。

## 禁止的替代方案

- 把所有能力继续放在单一 `lingshu` 包；
- Core 直接依赖 Socket、HTTP Parser、Auth、Database；
- Router、Database、Cache 直接写请求目录；
- 依赖 import 副作用和全局 Registry；
- 为旧 Sanic 路径建立永久兼容层。
