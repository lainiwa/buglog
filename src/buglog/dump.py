import json
from contextlib import suppress
from pathlib import Path
from typing import Union

from blessings import Terminal
from xdg import XDG_DATA_HOME

from buglog.utils import Bug


def dump_bug(bug: Bug, file_name: Union[Path, str]) -> None:
    path = XDG_DATA_HOME / __package__ / file_name

    prev_dumps = []
    with suppress(FileNotFoundError):
        with open(path, "r") as fin:
            prev_dumps = json.load(fin)

    with open(path, "w") as fout:
        json.dump(prev_dumps + [bug.dict()], fout)

    t = Terminal()
    verb = "Added" if prev_dumps else "Wrote"
    print(
        t.bold_green(f"{verb} {bug.__class__.__name__} into a file: ")
        + t.on_bright_black(f"{path}")
    )
