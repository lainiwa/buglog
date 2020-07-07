import tarfile
from io import BytesIO
from shutil import copyfile
from pathlib import Path

import httpx
from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME

import buglog


def ensure_fzf() -> None:
    """Create data folder and download fzf binary into it, if not yet."""
    data_dir = XDG_DATA_HOME / __package__
    fzf_path = data_dir / "fzf"

    if not fzf_path.exists():
        asset_url = "https://github.com/junegunn/fzf-bin/releases/download/0.21.1/fzf-0.21.1-linux_amd64.tgz"
        response = httpx.get(asset_url)

        with tarfile.open(fileobj=BytesIO(response.content)) as tar:
            tar.extract("fzf", data_dir)


def ensure_config() -> None:
    """Create config folder and copy example config into it, if not yet."""
    example = Path(buglog.__file__).parents[0] / "data" / "config.py"
    conf_dir = XDG_CONFIG_HOME / __package__
    conf_path = conf_dir / "config.py"

    if not conf_path.exists():
        conf_dir.mkdir(parents=True, exist_ok=True)
        copyfile(example, conf_path)
