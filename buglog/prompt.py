from typing import Optional
from datetime import datetime

import readchar  # type: ignore
from timefhuman import timefhuman  # type: ignore
from prompt_toolkit import prompt  # type: ignore
from prompt_toolkit.validation import Validator  # type: ignore
from prompt_toolkit.application.current import get_app  # type: ignore


def date_to_filename(bug_name: str, date: datetime) -> str:
    pretty_date = date.isoformat("_", "seconds")
    return f"{pretty_date}_{bug_name}.json"


def decode_timedate(text: str) -> Optional[datetime]:
    if text == "":
        return datetime.now()

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass

    try:
        parsed = timefhuman(text)
        if isinstance(parsed, datetime):
            return parsed
    except (AssertionError, ValueError):
        pass

    return None


def get_toolbar_text(bug_name: str) -> str:
    text = get_app().current_buffer.text
    date = decode_timedate(text)
    if date is not None:
        return date_to_filename(bug_name, date)
    return "???"


validator = Validator.from_callable(
    decode_timedate,
    error_message="This input is not a timedate",
    move_cursor_to_end=True,
)


def edit_filename_date(bug_name: str) -> str:
    text = prompt(
        "Give a number: ",
        default=datetime.now().isoformat("_", "seconds"),
        validator=validator,
        bottom_toolbar=lambda: get_toolbar_text(bug_name),
    )
    date = decode_timedate(text)
    assert date is not None
    return date_to_filename(bug_name, date)


def user_edit_write_cancel() -> str:
    while True:
        print("Some errors found. Watcha gonna do?")
        print("[e]dit/[w]rite Valid/[c]ancel: ", end="", flush=True)

        char = readchar.readchar().lower()
        if char in "ewc":
            print(char.upper())
            return char

        print("Type either 'E', 'W' or 'C'.")
        print()


def user_keep_toggle() -> str:
    while True:
        print("[K]eep current date or [t]oggle: ", end="", flush=True)

        char = readchar.readchar().lower()
        if char in "kt\r":
            if char == "\r":
                char = "k"
            print(char.upper())
            return char

        print("Type either 'K' or 'T'")
        print()
