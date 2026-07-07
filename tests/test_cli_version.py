from __future__ import annotations

import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

EXPECTED = "lingshu 0.1.0.dev0"


def _environment_without_pythonpath() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return environment


def _find_lingshu_executable() -> Path | None:
    executable_names = ("lingshu", "lingshu.exe", "lingshu.cmd", "lingshu.bat")
    script_dir = Path(sys.executable).parent

    for name in executable_names:
        candidate = script_dir / name
        if candidate.is_file():
            return candidate

    scripts_dir = Path(sysconfig.get_path("scripts"))
    for name in executable_names:
        candidate = scripts_dir / name
        if candidate.is_file():
            return candidate

    located = shutil.which("lingshu")
    if located:
        return Path(located)

    return None


def test_module_version_outside_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "lingshu", "--version"],
        cwd=tmp_path,
        env=_environment_without_pythonpath(),
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == EXPECTED


def test_version_subcommand_outside_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "lingshu", "version"],
        cwd=tmp_path,
        env=_environment_without_pythonpath(),
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == EXPECTED


def test_console_script_reports_installed_version(tmp_path: Path) -> None:
    executable = _find_lingshu_executable()
    assert executable is not None
    result = subprocess.run(
        [str(executable), "--version"],
        cwd=tmp_path,
        env=_environment_without_pythonpath(),
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == EXPECTED
