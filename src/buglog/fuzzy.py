from contextlib import suppress
from subprocess import CalledProcessError
from subprocess import check_output
from typing import Iterator
from typing import List
from typing import Type

from xdg import XDG_DATA_HOME

from buglog.bootstrap import ensure_fzf
from buglog.utils import Bug
from buglog.utils import get_bug_subclasses
from buglog.utils import str_to_bug


def fuzzy_pick_bug() -> List[Type[Bug]]:
    def fzf_input() -> Iterator[str]:
        for bug_class in get_bug_subclasses():
            schema = bug_class.schema()
            title = schema["title"]
            description = schema.get("description", title)
            yield f"{title} {description}"

    def _parse_item(line: str) -> Type[Bug]:
        bug_name, _ = line.split(" ", 1)
        return str_to_bug(bug_name)

    ensure_fzf()

    input_str = "\n".join(fzf_input())
    fzf = XDG_DATA_HOME / "buglog" / "fzf"
    fzf_cmd = [str(fzf), "--multi", "--with-nth", "2.."]

    with suppress(CalledProcessError):
        stdout = check_output(fzf_cmd, input=input_str, text=True)
        return [_parse_item(line) for line in stdout.splitlines()]

    return []
