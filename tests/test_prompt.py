from typing import Callable

import pytest
from _pytest.monkeypatch import MonkeyPatch


def rotate_chars(chars: str) -> Callable[[], str]:
    cs = list(reversed(chars))
    def _get_char() -> str:
        return cs.pop()

    return _get_char


@pytest.mark.parametrize(
    "args, chars, choice",
    [
        (("Install?", "[Y]es/[n]ope"), "lmnop", "n"),
        (("Install?", "[Y]es/[n]ope"), "vwxyz", "y"),
        (("Install?", "[Y]es/[n]ope"), "\rnop", "y"),
        (("Install?", "[y]es/[n]ope"), "\rnop", "n"),
    ],
)
def test_user_read_character(
    args, chars, choice, monkeypatch: MonkeyPatch
) -> None:
    from buglog.prompt import user_read_character

    monkeypatch.setattr("readchar.readchar", rotate_chars(chars))
    assert choice == user_read_character(*args)
