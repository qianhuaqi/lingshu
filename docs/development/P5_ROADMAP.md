# P5 Roadmap

Status: active for framework audit and database layer planning
Context: framework capability planning before further data-driver work

## 1. Why this document exists

P5 starts after the P4 extension foundation is accepted. The previous P5 sequence listed Redis, MySQL, and MongoDB directly. That was not enough for a framework-level plan because it skipped the common `lingshu.db` database layer and broader framework completeness audit.

This roadmap now defines the safer order:

```text
framework audit
framework implementation plan
stale documentation synchronization
lingshu.db database layer architecture
lingshu.db minimal code skeleton
specific database drivers
query / command / ORM / production layers
```

## 2. P4 closeout summary

P4 established the extension boundary, lifecycle rules, redaction rules, and packaging policy that P5 resource and data extensions must follow.

Accepted P4 baseline:

```text
P4-02 extension contract and package boundary
P4-03 application resource lifecycle
P4-04 configuration redaction for extensions
P4-05 official extension packaging and dependency policy
```

## 3. P5 goals

- Record what the framework has already implemented.
- Identify missing framework capabilities.
- Compare LingShu with mature frameworks and record what to learn.
- Synchronize stale README / phase / handoff / roadmap state.
- Define `lingshu.db` as the official database layer before isolated MySQL / Redis / MongoDB driver work continues.
- Keep the core package free of accidental mandatory runtime dependencies.

## 4. P5 non-goals for the current audit branch

- Implementing real database clients.
- Implementing ORM / ODM / Migration.
- Implementing OpenAPI, Auth, multi-worker, reload, or adapters.
- Making production-ready or performance claims.

These are not rejected forever; they are scheduled into later Plans after the correct lower layers exist.

## 5. Revised P5 order

```text
Plan 01: framework completeness audit and documentation sync
Plan 02: lingshu.db database layer architecture
Plan 03: lingshu.db minimal code skeleton
Plan 04: lingshu.db.mysql driver contract and skeleton
Plan 05: lingshu.db.redis alignment
Plan 06: lingshu.db.mongodb driver contract and skeleton
Plan 07: real runtime adapter strategy
Plan 08: SQL query and transaction layer
Plan 09: NoSQL command layer
Plan 10: ORM / ODM / Migration ADR
Plan 11: OpenAPI / Schema / Validation
Plan 12: Auth / Tenant / RBAC
Plan 13: Production runtime
```

## 6. Current active Plan

Current active Plan:

```text
Plan 01: framework completeness audit and documentation sync
```

Active branch:

```text
human/dodo/framework-audit-plan-sync
```

## 7. Next implementable Plan

After Plan 01 is merged, the next implementable Plan is:

```text
Plan 02: lingshu.db database layer architecture
```

That Plan must create `docs/architecture/DATABASE_LAYER_ARCHITECTURE.md` before continuing isolated MySQL, Redis, or MongoDB driver work.
