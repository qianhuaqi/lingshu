# Development Handoff

Updated at: 2026-06-28
Project: LingShu Framework
Phase: P1 - Single-Worker Minimum Vertical Slice
Active Issue: #52
Active Pull Request: #53
Branch: `human/dodo/p1-00-package-tooling-ci`
Primary writer: qianhuaqi / 小顾
Base commit: `4c925c20e53b5c3fc6005c5c07f2b32d5175a0f5`
Latest implementation commit: `85703eeadfe90234c7cc99c57ed30f82e2446392`
Status: implementation complete; all required CI checks green; awaiting review and project-lead merge

## Completed

- Created `pyproject.toml` with Hatchling, PEP 621, Apache-2.0 metadata, CPython >=3.12, version `0.1.0.dev0`, no mandatory runtime dependencies, and a development extra.
- Created root-level `lingshu/`; no `src/` directory.
- Created component package markers for core, runtime, HTTP, server, record, extensions, CLI, and testing.
- Added `py.typed`.
- Added installed-version access through `importlib.metadata` without a duplicate version literal.
- Added `python -m lingshu --version`, `python -m lingshu version`, and console-script version reporting only.
- Added package metadata, CLI, import-safety, artifact, and DCO checks.
- Added required Linux/Windows/macOS test matrix, quality job, Python 3.15 preview, build, sdist rebuild, artifact inventory, clean-install, and uninstall workflow.
- Synchronized stale P0 wording in README, AGENTS, Development Constitution, Current Phase, Handoff, and Changelog.
- All branch commits contain a DCO sign-off.

## Local evidence

An offline staging copy successfully:

- parsed `pyproject.toml` with `tomllib`;
- compiled every new Python file with `py_compile`;
- passed Ruff lint and formatting after the CI-reported corrections;
- passed mypy for the package.

A direct local pytest run before editable installation correctly failed to import the package. This is not counted as a product failure because the declared developer and CI workflow installs the project before testing. GitHub Actions performed the authoritative installed-package test.

## GitHub Actions evidence

CI run #2 passed every job:

```text
Quality and governance                   success
Build and clean install                  success
Linux Python 3.12                        success
Linux Python 3.13                        success
Linux Python 3.14                        success
Windows Python 3.12                      success
Windows Python 3.14                      success
macOS Python 3.12                        success
macOS Python 3.14                        success
Python 3.15 preview                      success
```

The successful build job verified:

- current Hatchling accepts the PEP 639 Apache-2.0 metadata;
- LICENSE and NOTICE are included under wheel license metadata;
- one `py3-none-any` wheel and one sdist are produced;
- forbidden files are absent from the wheel;
- a wheel rebuilt from the sdist has matching metadata and inventory;
- a non-editable wheel imports and reports its version outside checkout;
- the console script works outside checkout;
- uninstall completes.

## Scope amendments

Issue #52 includes `AGENTS.md` and `DEVELOPMENT_CONSTITUTION.md` because both retained stale P0-only prohibitions after Final Freeze. Their architecture and governance controls remain active; only phase authority was synchronized.

## Remaining action

1. independent review of PR #53;
2. resolve any blocking review finding inside Issue #52 scope;
3. project lead performs final merge;
4. only after merge, close P1-00 and create P1-01 from the resulting `main` commit.

## Protected facts

- Production source is `lingshu/`, never `src/lingshu/`.
- P1-00 contains no framework behavior assigned to later Issues.
- Archive branch `archive/legacy-sanic-20260628` remains untouched.
- Public package-index publication remains unauthorized.
- No auto-merge; final merge belongs to the project lead.
