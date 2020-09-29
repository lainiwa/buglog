from pathlib import Path
from typing import Dict

import pytest
from _pytest.monkeypatch import MonkeyPatch
from _pytest.tmpdir import TempPathFactory


@pytest.fixture(scope="function")
def mock_xdg(
    monkeypatch: MonkeyPatch, tmp_path_factory: TempPathFactory
) -> Dict[str, Path]:
    tmp_path = tmp_path_factory.mktemp("data")
    data_home = tmp_path / ".local/share"
    config_home = tmp_path / ".config"
    monkeypatch.setattr("buglog.bootstrap.XDG_DATA_HOME", data_home)
    monkeypatch.setattr("buglog.bootstrap.XDG_CONFIG_HOME", config_home)
    return {"XDG_DATA_HOME": data_home, "XDG_CONFIG_HOME": config_home}
