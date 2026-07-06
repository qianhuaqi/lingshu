from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path


def test_lingshu_db_import_has_no_process_side_effects(tmp_path: Path) -> None:
    code = r"""
import importlib
import json
import os
import sys
import threading

before_environment = dict(os.environ)
before_threads = {thread.ident for thread in threading.enumerate()}
module = importlib.import_module("lingshu.db")

forbidden_clients = ("aiomysql", "motor", "pymongo", "pymysql", "redis")
print(json.dumps({
    "environment_changed": before_environment != dict(os.environ),
    "thread_count_changed": before_threads != {thread.ident for thread in threading.enumerate()},
    "forbidden_clients": [name for name in forbidden_clients if name in sys.modules],
    "exports": sorted(module.__all__),
}))
"""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    evidence = json.loads(result.stdout)
    assert evidence == {
        "environment_changed": False,
        "thread_count_changed": False,
        "forbidden_clients": [],
        "exports": [
            "DatabaseConfig",
            "DatabaseConfigurationError",
            "DatabaseDriver",
            "DatabaseError",
            "DatabaseLifecycleError",
            "DatabaseManager",
            "DatabaseResource",
        ],
    }


def test_database_clients_are_not_required_for_import() -> None:
    lingshu_db = importlib.import_module("lingshu.db")
    assert lingshu_db.DatabaseConfig(name="db.mysql.main", backend="mysql")
    for client in ("aiomysql", "motor", "pymongo", "pymysql", "redis"):
        assert client not in sys.modules
