# LingShu Framework / 灵枢框架

Canonical repository: `qianhuaqi/lingshu`

LingShu is a greenfield, independently implemented Python Web/API framework. It does not depend on Sanic, FastAPI, Flask, Django, Starlette, or another upper-level Web framework.

## Current status

LingShu is in **P1: Single-Worker Minimum Vertical Slice**.

P1-10 marks the final integration of the P1 baseline. The framework provides immutable route plans, native single-worker HTTP/1.1 serving, request/response core primitives, scopes, and a CLI foundation.

Current development version:

```text
0.1.0.dev0
```

> [!WARNING]
> This is a development milestone for P1 only. The framework is strictly single-worker, lacks production performance optimizations, and is not authorized for public PyPI publication.

## Quick Start

You can create a basic application (see `examples/hello_world.py`):

```python
from lingshu import LingShu, Request, Response

app = LingShu()

@app.get("/")
async def index(request: Request) -> Response:
    return Response.text("hello")
```

Validate the application and run it with the LingShu CLI:

```bash
lingshu check examples.hello_world:app
lingshu run examples.hello_world:app --workers 1
```

## Development setup

Requirements:

```text
CPython 3.12 or newer
```

The supported development toolchain and Ruff formatting baseline are documented in [`docs/development/TOOLCHAIN.md`](docs/development/TOOLCHAIN.md).

Create and activate a virtual environment, then install the development extra:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the baseline checks:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy lingshu
python -m pytest
python -m build
python tests/packaging/check_artifacts.py validate dist
git diff --check
```

An editable installation is for development only. Release evidence comes from the CI clean-install job, which builds wheel and sdist, installs the wheel outside the checkout, validates artifact inventory, and rebuilds a wheel from the sdist.

## Authoritative entry points

Read these before contributing:

1. [Development Constitution](docs/development/DEVELOPMENT_CONSTITUTION.md)
2. the active GitHub Issue
3. [Current Phase](docs/development/CURRENT_PHASE.md)
4. [Concurrent Development](docs/development/CONCURRENT_DEVELOPMENT.md)
5. [Frozen Framework Blueprint](docs/architecture/LINGSHU_FRAMEWORK_BLUEPRINT.md)
6. accepted ADRs under [`docs/decisions/`](docs/decisions/)
7. [P1 Implementation Plan](docs/development/P1_IMPLEMENTATION_PLAN.md)
8. [Development Handoff](docs/development/HANDOFF.md)

## Contribution rules

- One task uses one Issue, one primary writer, one writer-prefixed branch, one isolated worktree/environment, and one Pull Request.
- Never commit directly to `main`.
- Never enable auto-merge.
- Every commit requires a DCO sign-off created with `git commit -s`.
- Final merge authority belongs to the project lead.
- Work must remain inside the active Issue's write scope and dependency order.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Architecture baseline

```text
Distribution:        lingshu
Import package:      lingshu
Production source:   lingshu/
Package metadata:    pyproject.toml
Build backend:       Hatchling
Minimum Python:      CPython 3.12
Mandatory runtime dependencies: none in P1-00
```

The target component boundaries are:

```text
lingshu.core
lingshu.runtime
lingshu.http
lingshu.server
lingshu.record
lingshu.extensions
lingshu.cli
lingshu.testing
```

The packages are placeholders in P1-00. Component behavior is implemented only by its assigned later Issue.

## Legacy archive

The previous Sanic-based repository state remains preserved at:

```text
legacy/sanic_framework/
```
