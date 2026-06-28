# Development Handoff

Updated at: 2026-06-28
Project: LingShu Framework
Phase: P1 - Single-Worker Minimum Vertical Slice
Active Issue: #52
Branch: `human/dodo/p1-00-package-tooling-ci`
Primary writer: qianhuaqi / 小顾
Base commit: `4c925c20e53b5c3fc6005c5c07f2b32d5175a0f5`
Current implementation commit: `82d08075713d9c1d1b7393f9aae8ee513818aba9`
Status: package/tooling foundation written; documentation synchronization and CI review in progress

## Completed

- Created `pyproject.toml` with Hatchling, PEP 621, Apache-2.0 metadata, CPython >=3.12, version `0.1.0.dev0`, no mandatory runtime dependencies, and a development extra.
- Created root-level `lingshu/`; no `src/` directory.
- Created component package markers for core, runtime, HTTP, server, record, extensions, CLI, and testing.
- Added `py.typed`.
- Added installed-version access through `importlib.metadata` without a duplicate version literal.
- Added `python -m lingshu --version`, `python -m lingshu version`, and console-script version reporting only.
- Added package metadata, CLI, import-safety, artifact, and DCO checks.
- Added required Linux/Windows/macOS test matrix, quality job, Python 3.15 preview, build, sdist rebuild, artifact inventory, and clean-install workflow.
- All implementation commits include a DCO sign-off.

## Validation performed before push

A local offline staging copy was used to:

- parse `pyproject.toml` with `tomllib`;
- compile every new Python file with `py_compile`.

These checks passed.

## Checks not yet claimed

The local execution environment had no network access and did not have Hatchling, build, Ruff, or mypy installed. Therefore wheel/sdist build, Ruff, mypy, and full pytest evidence must come from GitHub Actions or a developer environment after checkout. Do not represent those checks as passing until results are available.

## Scope amendments

Issue #52 includes `AGENTS.md` and `DEVELOPMENT_CONSTITUTION.md` because both retained stale P0-only prohibitions after Final Freeze. Their architecture and governance controls remain intact; only phase authority is synchronized.

## Next action

1. complete documentation synchronization commit;
2. open the P1-00 Pull Request;
3. inspect every CI job and correct any failure without expanding scope;
4. obtain independent review;
5. project lead performs final merge;
6. only then create P1-01.

## Risks to review

- Verify current Hatchling accepts the selected PEP 639 license metadata and includes LICENSE/NOTICE under `.dist-info/licenses/`.
- Verify Python 3.14 availability on every required runner and Python 3.15 preview naming in `setup-python`.
- Verify DCO range checking works for pull-request merge strategies.
- Verify wheel rebuilt from sdist produces matching metadata and inventory.
- Verify Windows console-script subprocess behavior.

## Protected facts

- Production source remains `lingshu/`, never `src/lingshu/`.
- P1-00 contains no framework behavior assigned to later Issues.
- Archive branch `archive/legacy-sanic-20260628` remains untouched.
- No auto-merge; final merge belongs to the project lead.
