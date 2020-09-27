import pytest
from click.testing import CliRunner

from buglog import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    result = runner.invoke(cli.main, "--version")
    assert result.exit_code == 0
