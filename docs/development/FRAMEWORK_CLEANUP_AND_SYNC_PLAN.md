# LingShu Framework 文档同步与清理计划

状态：P5 文档治理计划
更新时间：2026-07-06

## 1. 目标

本文件用于清理过期状态、失效说明和容易误导开发者的文档。

当前原则：

```text
不删除历史决策
不改写已接受 ADR
不直接删除旧阶段证据
先同步当前状态
再标记过期内容
最后按 Issue 分批清理
```

## 2. 当前需要同步的文件

### 2.1 README.md

问题：README 仍描述项目处于 P3，但当前已经进入 P5。

处理：更新 Current status，加入 P5 总控文档入口。

### 2.2 docs/development/CURRENT_PHASE.md

问题：Current phase 已是 P5，但 active issue 仍停在 P5-00。

处理：更新为 P5 framework audit and database layer planning。

### 2.3 docs/development/HANDOFF.md

问题：仍停在 P5-01 Redis active。

处理：更新为当前 Plan 01：framework audit / plan / docs sync。

### 2.4 docs/development/P5_ROADMAP.md

问题：顶部状态仍是 P5-01 review，但底部已经指向 P5-03。

处理：改为 P5 data extension and database layer roadmap。

## 3. 当前暂不删除的内容

以下内容暂不删除，只做状态标记或入口纠偏：

```text
docs/architecture/LINGSHU_FRAMEWORK_BLUEPRINT.md
docs/decisions/*
docs/development/P1_*
docs/development/P2_*
docs/development/P3_*
docs/development/P4_*
legacy/*
archive/*
```

原因：这些是历史依据或冻结决策，不能因为当前阶段推进就直接删除。

## 4. 后续清理清单

后续应单独开 Issue 分批处理：

```text
1. README 与 docs/development 入口统一；
2. 当前阶段、handoff、roadmap 三件套同步；
3. 已完成阶段文档增加 superseded / completed 标记；
4. 旧候选文档归档索引；
5. legacy / archive 的引用路径核对；
6. 重复路线图合并；
7. 所有 active issue / active branch 描述只保留一个事实源。
```

## 5. 文档单一事实源规则

后续开发必须遵守：

```text
README：只写当前状态摘要和权威入口；
CURRENT_PHASE：当前阶段事实源；
HANDOFF：当前交接事实源；
ROADMAP：当前阶段路线事实源；
ARCHITECTURE：长期架构事实源；
ADR：已接受决策事实源。
```

任何文档不得单独声明不同的 active phase / active issue / next action。
