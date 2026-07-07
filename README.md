# LingShu Framework

Canonical repository: `qianhuaqi/lingshu`

LingShu is a greenfield, independently implemented Python Web/API framework. It
does not depend on Sanic, FastAPI, Flask, Django, Starlette, or another
upper-level Web framework.

## Current state

- Current phase: P5-10 Minimal MySQL transaction boundary (completed / accepted)
- Final P5 issue: #135
- Closing PR: #138
- Current status: P5 implementation and closeout are accepted; this issue performs post-P5 audit and release-readiness cleanup.
- Next action: complete cleanup in #140, then wait for project-owner authorization for the next backend track.

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
