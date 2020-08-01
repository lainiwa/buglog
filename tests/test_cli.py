import pytest
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner
from buglog import cli
from typing import Callable


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, "--version")
    assert result.exit_code == 0
