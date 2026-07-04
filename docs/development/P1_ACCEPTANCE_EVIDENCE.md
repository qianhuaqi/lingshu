# P1-10 Acceptance Evidence

This document records the acceptance matrix verification for the P1 single-worker final integration (Issue #76).

## Environment Matrix
- **OS**: Windows, Linux, macOS (via CI matrix)
- **Python**: CPython 3.12
- **Build Backend**: Hatchling
- **Linter/Formatter**: Ruff

## Test Execution Summary

> [!NOTE]
> This document provides the acceptance matrix for P1-10. 
> Evidence is based on GitHub Actions CI run #100, at head `34a9d72798c1bc686cbba1b125dd632ea29268df`.

The `pytest` integration test suite, `ruff` formatting and linting, and `mypy` typing checks passed successfully across the matrix.

## Packaging Verification

```bash
$ python -m build
$ python tests/packaging/check_artifacts.py validate dist/
All artifact integrity checks passed. Forbidden directories (including `tests/` and `examples/`) successfully excluded from production distributions.
```

## CLI Behavior

```bash
$ pip install dist/lingshu-0.1.0.dev0-py3-none-any.whl
Successfully installed lingshu-0.1.0.dev0

$ lingshu version
lingshu 0.1.0.dev0

$ lingshu check examples.hello_world:app
✓ Configuration validated
✓ Application plan frozen
✓ 1 routes registered

$ lingshu run examples.hello_world:app --workers 1
Starting LingShu application (0.1.0.dev0)
Server listening on 127.0.0.1:8000
```

## Acceptance Criteria Verified
- [x] Pure wheel / sdist builds properly.
- [x] Functional execution in non-editable installs.
- [x] Immutable Application freeze enforces safety.
- [x] Request routing, header size limits, and body bounds protected.
- [x] Core `RuntimeScope` enforces Deadlines safely.
- [x] `HTTP/1.1` keep-alive and graceful `drain()` shutdown handled natively.
- [x] Concurrency watermark rejects overflow requests (TCP EOF or safe 503).
- [x] CLI strictly rejects multi-worker usage via `--workers 2`.
- [x] Sensitive stack traces explicitly redacted.
