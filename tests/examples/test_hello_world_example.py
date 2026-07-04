from lingshu.cli import main
from lingshu.cli.core import ExitCode


def test_hello_world_example_is_cli_checkable() -> None:
    assert main(["check", "examples.hello_world:app"]) == ExitCode.SUCCESS
