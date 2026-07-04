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
> The exact `pytest` and `ruff` outputs will be updated here after the CI pipeline officially passes. The expected outcome is 65+ passing tests with 100% component safety.

Expected to run:
```bash
pytest tests/integration -vv
```

## Packaging Verification

Expected outcome for packaging:
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

## Acceptance Criteria To Validate
- [ ] Pure wheel / sdist builds properly.
- [ ] Functional execution in non-editable installs.
- [ ] Immutable Application freeze enforces safety.
- [ ] Request routing, header size limits, and body bounds protected.
- [ ] Core `RuntimeScope` enforces Deadlines safely.
- [ ] `HTTP/1.1` keep-alive and graceful `drain()` shutdown handled natively.
- [ ] Concurrency watermark rejects overflow requests (TCP EOF or safe 503).
- [ ] CLI strictly rejects multi-worker usage via `--workers 2`.
- [ ] Sensitive stack traces explicitly redacted.
