from __future__ import annotations

import lingshu.db as db


def test_public_exports_are_stable() -> None:
    assert db.__all__ == (
        "DatabaseConfig",
        "DatabaseConfigurationError",
        "DatabaseDriver",
        "DatabaseError",
        "DatabaseLifecycleError",
        "DatabaseManager",
        "DatabaseResource",
    )
