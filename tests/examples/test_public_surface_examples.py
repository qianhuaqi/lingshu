from lingshu.cli import main
from lingshu.cli.core import ExitCode


def test_json_response_example_is_cli_checkable() -> None:
    result = main(["check", "examples.json_response:app"])
    assert result == ExitCode.SUCCESS


def test_body_echo_example_is_cli_checkable() -> None:
    result = main(["check", "examples.body_echo:app"])
    assert result == ExitCode.SUCCESS
