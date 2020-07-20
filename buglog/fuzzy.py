from subprocess import check_output
from typing import Iterator
from typing import List

from xdg import XDG_DATA_HOME

from buglog.utils import Bug
from buglog.utils import get_bug_subclasses


def fuzzy_pick_bug() -> List[Bug]:
    def fzf_input() -> Iterator[str]:
        for bug_class in get_bug_subclasses():
            schema = bug_class.schema()
            title = schema["title"]
            description = schema.get("description", title)
            yield f"{title} {description}"

    input_str = '\n'.join(fzf_input())
    fzf = XDG_DATA_HOME / "buglog" / "fzf"
    fzf_cmd = [fzf, "--multi", "--with-nth", "2.."]
    stdout = check_output(fzf_cmd, input=input_str, text=True)
    return stdout.splitlines()
