# LingShu Framework

Canonical repository: `qianhuaqi/lingshu`

LingShu is a greenfield, independently implemented Python Web/API framework. It
does not depend on Sanic, FastAPI, Flask, Django, Starlette, or another
upper-level Web framework.

## Current state

- Current phase: P5-10 Minimal MySQL transaction boundary (completed / accepted)
- Final P5 issue: #135
- Closing PR: #138
- Post-P5 audit PR: #141 (merged)
- Post-P5 audit status: issue #140 closed.
- Current status: P5 completed; release baseline is recorded, and project is entering P6 planning / release-readiness work (Issue #143).
- Next action: begin P6 planning after release-baseline verification.

## Authoritative entries

- [Current phase](docs/development/CURRENT_PHASE.md)
- [Development handoff](docs/development/HANDOFF.md)
- [P5 roadmap](docs/development/P5_ROADMAP.md)
- [Repository cleanup audit](docs/development/REPOSITORY_CLEANUP_AUDIT.md)
- [Framework blueprint](docs/architecture/LINGSHU_FRAMEWORK_BLUEPRINT.md)
- [Accepted decisions](docs/decisions)

## Historical context

The frozen P0/P1/P2/P3/P4 architecture and governance record remains in the
`docs/architecture/` and `docs/decisions/` trees. Historical archive material is
documented there for reference and is not part of the active runtime surface.
