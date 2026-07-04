import inspect
import io
import sys
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from lingshu import LingShu
from lingshu.cli.core import CliError, ExitCode
from lingshu.cli.target import load_target
from lingshu.cli import main


# --- Dummy Apps for Testing ---
app_instance = LingShu()


def valid_factory() -> LingShu:
    return LingShu()


def factory_with_args(arg1: int) -> LingShu:
    return LingShu()


async def async_factory() -> LingShu:
    return LingShu()


def bad_factory_return() -> str:
    return "not an app"


def raising_factory() -> LingShu:
    raise RuntimeError("factory failed")


not_an_app = "just a string"


# --- Tests for Target Resolution ---


def test_load_target_valid_instance() -> None:
    app = load_target("tests.cli.test_cli:app_instance", is_factory=False)
    assert app is app_instance


def test_load_target_valid_factory() -> None:
    app = load_target("tests.cli.test_cli:valid_factory", is_factory=True)
    assert isinstance(app, LingShu)


def test_load_target_invalid_format() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli.app_instance", is_factory=False)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_malformed_attribute() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:app:invalid", is_factory=False)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_missing_module() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.missing_module:app", is_factory=False)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_missing_attribute() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:missing_attr", is_factory=False)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_not_callable_factory() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:app_instance", is_factory=True)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_async_factory() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:async_factory", is_factory=True)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_factory_with_args() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:factory_with_args", is_factory=True)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_factory_raises() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:raising_factory", is_factory=True)
    assert exc.value.exit_code == ExitCode.CONTRACT_ERROR


def test_load_target_bad_return_type() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:bad_factory_return", is_factory=True)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


def test_load_target_instance_bad_type() -> None:
    with pytest.raises(CliError) as exc:
        load_target("tests.cli.test_cli:not_an_app", is_factory=False)
    assert exc.value.exit_code == ExitCode.RESOLUTION_ERROR


# --- Tests for CLI Commands ---


def test_main_version() -> None:
    assert main(["version"]) == ExitCode.SUCCESS
    assert main(["--version"]) == ExitCode.SUCCESS


def test_main_check_success() -> None:
    assert main(["check", "tests.cli.test_cli:app_instance"]) == ExitCode.SUCCESS
    assert main(["check", "tests.cli.test_cli:valid_factory", "--factory"]) == ExitCode.SUCCESS


def test_main_check_resolution_error(capsys: pytest.CaptureFixture[str]) -> None:
    # Ensure no traceback is printed, just the safe error message
    assert main(["check", "invalid_format"]) == ExitCode.RESOLUTION_ERROR
    captured = capsys.readouterr()
    assert "Traceback" not in captured.err
    assert "Error:" in captured.err


def test_main_run_unsupported_workers(capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main(["run", "tests.cli.test_cli:app_instance", "--workers", "2"])
        == ExitCode.UNSUPPORTED_WORKER
    )
    captured = capsys.readouterr()
    assert "Multi-worker is not supported" in captured.err


@patch("lingshu.cli.commands.serve")
def test_main_run_success(mock_serve: Any) -> None:
    mock_serve.return_value = AsyncMock()
    assert main(["run", "tests.cli.test_cli:app_instance"]) == ExitCode.SUCCESS
    mock_serve.assert_called_once()

    # Assert server config
    app, config = mock_serve.call_args[0]
    assert app is app_instance
    assert config.host == "127.0.0.1"
    assert config.port == 8000


@patch("lingshu.cli.commands.serve")
def test_main_run_custom_host_port(mock_serve: Any) -> None:
    mock_serve.return_value = AsyncMock()
    assert (
        main(["run", "tests.cli.test_cli:app_instance", "--host", "0.0.0.0", "--port", "9000"])
        == ExitCode.SUCCESS
    )

    app, config = mock_serve.call_args[0]
    assert config.host == "0.0.0.0"
    assert config.port == 9000


@patch("lingshu.cli.commands.serve", side_effect=RuntimeError("server crashed"))
def test_main_run_runtime_failure(mock_serve: Any, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["run", "tests.cli.test_cli:app_instance"]) == ExitCode.RUNTIME_FAILURE
    captured = capsys.readouterr()
    assert "server crashed" in captured.err


@patch("lingshu.cli.commands.serve", side_effect=KeyboardInterrupt())
def test_main_run_keyboard_interrupt(mock_serve: Any) -> None:
    # KeyboardInterrupt should be handled safely and return SUCCESS
    assert main(["run", "tests.cli.test_cli:app_instance"]) == ExitCode.SUCCESS
