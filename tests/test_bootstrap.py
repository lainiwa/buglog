
import contextlib
import os
from pathlib import Path
from hashlib import sha256
import pytest
import os
import xdg
from _pytest.monkeypatch import MonkeyPatch


@pytest.mark.slow
def test_ensure_fzf(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    # Variables
    data_home = tmp_path / ".local/share"
    fzf_path = data_home / "buglog/fzf"
    expected_hash = "755354b590c9d4c75b8a2e27374bfa1f02d3eb7a73c94ed43b17ac36aa73dede"
    # Call ensure_fzf() with alternated XDG_DATA_HOME
    monkeypatch.setattr('buglog.bootstrap.XDG_DATA_HOME', data_home)
    from buglog.bootstrap import ensure_fzf
    ensure_fzf()
    # Check fzf was created
    assert fzf_path.is_file()
    # Check fzf's checksum
    with open(fzf_path, "rb") as fzf_file:
        readable_hash = sha256(fzf_file.read()).hexdigest();
        assert readable_hash == expected_hash


def test_ensure_config(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    # Variables
    config_home = tmp_path / ".config"
    config_path = config_home / "buglog/config.py"
    expected_hash = "755354b590c9d4c75b8a2e27374bfa1f02d3eb7a73c94ed43b17ac36aa73dede"
    # Call ensure_config() with alternated XDG_CONFIG_HOME
    monkeypatch.setattr('buglog.bootstrap.XDG_CONFIG_HOME', config_home)
    from buglog.bootstrap import ensure_config
    ensure_config()
    # Check config was copied was created
    assert config_path.is_file()
    # Get original config file's contents
    import buglog
    with open(Path(buglog.__file__).parents[0] / "data/config.py", "rb") as orig_conf:
        orig_content = orig_conf.read()
    # Get copied file's contents
    with open(config_path, "rb") as copied_conf:
        copied_content = copied_conf.read()
    # Check the content is the same
    assert orig_content == copied_content
