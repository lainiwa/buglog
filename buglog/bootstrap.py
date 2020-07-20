import platform
import tarfile
from io import BytesIO
from pathlib import Path
from shutil import copyfile

import httpx
from xdg import XDG_CONFIG_HOME
from xdg import XDG_DATA_HOME

import buglog


def ensure_fzf(*, version: str = "0.21.1") -> None:
    """Create data folder and download fzf binary into it, if not yet.

    Parameters:
        version: Version of fzf to be downloaded.
    """
    data_dir = XDG_DATA_HOME / __package__
    fzf_path = data_dir / "fzf"

    if not fzf_path.exists():
        system = platform.system().lower()
        machine = platform.machine()
        arch = {"x86_64": "amd64"}.get(machine, machine)

        asset_url = (
            "https://github.com/junegunn/fzf-bin/releases/download"
            f"/{version}/fzf-{version}-{system}_{arch}.tgz"
        )

        response = httpx.get(asset_url)

        with tarfile.open(fileobj=BytesIO(response.content)) as tar:
            tar.extract("fzf", data_dir)


def ensure_config(*, force_update: bool = False) -> None:
    """Create config folder and copy example config into it, if not yet.

    Parameters:
        force_update: Forcefully refresh the config, even if already present
            (used for debug porposes).
    """
    example = Path(buglog.__file__).parents[0] / "data" / "config.py"
    conf_dir = XDG_CONFIG_HOME / __package__
    conf_path = conf_dir / "config.py"

    if force_update or not conf_path.exists():
        conf_dir.mkdir(parents=True, exist_ok=True)
        copyfile(example, conf_path)
