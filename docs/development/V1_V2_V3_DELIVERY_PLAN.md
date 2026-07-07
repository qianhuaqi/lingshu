# LingShu V1 / V2 / V3 Delivery Plan Index

Project: LingShu Framework
Owner: 多多
Planner / PM: 小顾
Status: active delivery plan index

## Purpose

This file is now only the entry index for the three-version delivery plan.

The detailed plan is split into three focused documents so V1, V2, and V3 do not mix together in one large document.

## Documents

| Version | Document | Purpose |
| --- | --- | --- |
| V1 | `docs/development/V1_CAPABILITY_PLAN.md` | Complete the missing framework business capability modules. |
| V2 | `docs/development/V2_CLI_PROJECT_PLAN.md` | Complete CLI commands and project generation experience. |
| V3 | `docs/development/V3_TESTING_STABILITY_PLAN.md` | Complete tests, stability hardening, and final acceptance. |

## Version scope

```text
V1: 补齐框架业务能力模块
V2: 补齐 CLI 与项目生成体验
V3: 补齐测试、稳定性和验收硬化
```

## Naming decision

Database backend modules use flat package names under `lingshu.db`:

```text
lingshu.db.sqlite
lingshu.db.mysql
lingshu.db.postgresql
lingshu.db.redis
lingshu.db.mongodb
```

`SQL` and `NoSQL` are documentation categories only. They are not real package path levels.

## Execution start

Current implementation starts from:

```text
#146: V1-01 / lingshu.db foundation
```
