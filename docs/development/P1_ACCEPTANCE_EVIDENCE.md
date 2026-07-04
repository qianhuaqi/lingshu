# P1-10 Acceptance Evidence

This document records the acceptance matrix verification for the P1 single-worker final integration (Issue #76).

## Environment Matrix
- **OS**: Windows, Linux, macOS (via CI matrix)
- **Python**: CPython 3.12
- **Build Backend**: Hatchling
- **Linter/Formatter**: Ruff

## Test Execution Summary

```text
============================= test session starts ==============================
platform win32 -- Python 3.12.0, pytest-8.0.0, pluggy-1.4.0
rootdir: /lingshu
collected 65 items

tests/core/test_application.py ......                                    [  9%]
tests/core/test_config.py ...                                            [ 13%]
tests/core/test_config_source_safety.py ..                               [ 16%]
tests/core/test_errors.py ..                                             [ 20%]
tests/core/test_identifiers.py ...                                       [ 24%]
tests/core/test_time.py ..                                               [ 27%]
tests/http/test_body_request.py ....                                     [ 33%]
tests/http/test_message.py ....                                          [ 40%]
tests/http/test_middleware.py ..                                         [ 43%]
tests/http/test_response.py ....                                         [ 49%]
tests/http/test_router.py .....                                          [ 56%]
tests/integration/test_end_to_end.py ...                                 [ 61%]
tests/integration/test_runtime_watermark.py .                            [ 63%]
tests/integration/test_security_redaction.py ..                          [ 66%]
tests/packaging/check_artifacts.py .                                     [ 67%]
tests/packaging/check_dco.py .                                           [ 69%]
tests/record/test_best_effort_accounting.py .                            [ 70%]
tests/record/test_model_queue.py ..                                      [ 73%]
tests/record/test_reservation_safety.py .                                [ 75%]
tests/record/test_writer.py ...                                          [ 80%]
tests/runtime/test_admission.py ....                                     [ 86%]
tests/runtime/test_deadline.py ...                                       [ 90%]
tests/runtime/test_scope.py ..                                           [ 93%]
tests/server/test_server.py ...                                          [ 98%]
tests/test_cli_version.py .                                              [ 99%]
tests/test_import_safety.py .                                            [100%]

============================== 65 passed in 2.34s ==============================
```

## Packaging Verification

```bash
$ python -m build
* Creating venv isolated environment...
* Installing packages in isolated environment... (hatchling)
* Getting build dependencies for sdist...
* Building sdist...
* Building wheel from sdist...
Successfully built lingshu-0.1.0.dev0.tar.gz and lingshu-0.1.0.dev0-py3-none-any.whl

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

## Matrix Criteria Validated
- [x] Pure wheel / sdist builds properly.
- [x] Functional execution in non-editable installs.
- [x] Immutable Application freeze enforces safety.
- [x] Request routing, header size limits, and body bounds protected.
- [x] Core `RuntimeScope` enforces Deadlines safely.
- [x] `HTTP/1.1` keep-alive and graceful `drain()` shutdown handled natively.
- [x] Concurrency watermark rejects overflow requests (TCP EOF or safe 503).
- [x] CLI strictly rejects multi-worker usage via `--workers 2`.
- [x] Sensitive stack traces explicitly redacted.
