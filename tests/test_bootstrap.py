from hashlib import sha256
from pathlib import Path
import os

import pytest
from typing import Dict

import buglog
from buglog.bootstrap import ensure_fzf, ensure_config


@pytest.mark.slow
def test_ensure_fzf(mock_xdg: Dict[str, Path]) -> None:
    fzf_path = mock_xdg["XDG_DATA_HOME"] / "buglog" / "fzf"

    # Make sure we do not have the fzf file yet
    assert not fzf_path.is_file()

    # Check calling ensure_fzf() creates a correct fzf file
    ensure_fzf()
    assert fzf_path.is_file()

    with open(fzf_path, "rb") as fzf_file:
        readable_hash = sha256(fzf_file.read()).hexdigest()
        expected_hash = (
            "755354b590c9d4c75b8a2e27374bfa1f02d3eb7a73c94ed43b17ac36aa73dede"
        )
        assert readable_hash == expected_hash

    # Clear fzf file's contents
    open(fzf_path, "w").close()
    # Call ensure_fzf again and check it would not download fzf again
    ensure_fzf()
    assert os.stat(fzf_path).st_size == 0


def test_ensure_config(mock_xdg: Dict[str, Path]) -> None:
    config_path = mock_xdg["XDG_CONFIG_HOME"] / "buglog" / "config.py"

    # Make sure we do not have the config file bootstrapped yet
    assert not config_path.is_file()

    # Check calling ensure_config() creates a correct fzf file
    ensure_config()

    # Get original config file's contents
    with open(
        Path(buglog.__file__).parents[0] / "data" / "config.py", "rb"
    ) as orig_conf:
        orig_content = orig_conf.read()
    # Get copied file's contents
    with open(config_path, "rb") as copied_conf:
        copied_content = copied_conf.read()
    # Check the content is the same
    assert orig_content == copied_content

    # Clear config file's contents
    open(config_path, "w").close()
    # Call ensure_config again and check it would not bootstrap config again
    ensure_config()
    assert os.stat(config_path).st_size == 0
