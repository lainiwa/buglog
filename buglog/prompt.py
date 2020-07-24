import re
from contextlib import suppress
from datetime import datetime
from typing import Optional
from typing import Tuple

import readchar  # type: ignore
from prompt_toolkit import prompt  # type: ignore
from prompt_toolkit.application.current import get_app  # type: ignore
from prompt_toolkit.validation import Validator  # type: ignore
from timefhuman import timefhuman  # type: ignore


def date_to_filename(bug_name: str, date: datetime) -> str:
    """Get appropriate filename for a bug dump.

    Example:
        >>> from datetime import datetime
        >>> date_to_filename('Squats', datetime(2007, 12, 6, 15, 29, 43))
        '2007-12-06_15:29:43_Squats.json'

    Parameters:
        bug_name: The class name of the bug.
        date: Bug generation time and date.

    Returns:
        Name of .json file dump.
    """
    pretty_date = date.isoformat("_", "seconds")
    return f"{pretty_date}_{bug_name}.json"


def _decode_timedate(text: str) -> Optional[datetime]:
    if text == "":
        return datetime.now()

    with suppress(ValueError):
        return datetime.fromisoformat(text)

    with suppress(AssertionError, ValueError):
        parsed = timefhuman(text)
        if isinstance(parsed, datetime):
            return parsed

    return None


def _get_toolbar_text(bug_name: str) -> str:
    text = get_app().current_buffer.text
    date = _decode_timedate(text)
    if date is not None:
        return date_to_filename(bug_name, date)
    return "???"


_validator = Validator.from_callable(
    _decode_timedate,
    error_message="This input is not a timedate",
    move_cursor_to_end=True,
)


def edit_filename_date(bug_name: str, default: str = "") -> Tuple[str, str]:
    """Prompt user to change timedate of created file.

    Parameters:
        bug_name: The class name of the bug.
        default: Default textual time.

    Returns:
        New name of the .json dump file
        and the raw text entered by user.
    """
    text = prompt(
        "Time: ",
        default=default,
        validator=_validator,
        bottom_toolbar=lambda: _get_toolbar_text(bug_name),
    )
    date = _decode_timedate(text)
    assert date is not None
    return date_to_filename(bug_name, date), text


def user_read_character(*args: str) -> str:
    """Read single character.

    Prompt user with the lines passed as parameters,
    and then wait for a valid keypress. The possible
    keypresses are searched in between of ``[]`` brackets.

    If the letter in brackets is UPPERCASE, then it is treated as
    a default choice and corrsponds to pressing Enter.

    Example:
        >>> user_read_character("Install?", "[Y]es/[n]ope")  # doctest: +SKIP

    Parameters:
        args: Lines to be printed as a prompt.

    Returns:
        The letter the user have chosen; lowercase.
    """
    # Construct prompt message from provided arguments
    prompt = "\n".join(args)
    # All letters the user specified to accept
    letters = "".join(re.findall(r"\[(.)\]", prompt))
    # The big letter (if present) or empty string
    big_letter = "".join(ch for ch in letters if ch.isupper()).lower()
    # Accepted characters with Enter as a default choice
    chars = letters.lower() + "\r" if big_letter else letters.lower()

    while True:
        # Print prompt message and wait for user input
        print(prompt, end="", flush=True)
        char = readchar.readchar().lower()
        # If user typed a valid choice - echo the typed letter and return it
        # Enter is echoed as the default choice letter
        if char in chars:
            if char == "\r":
                char = big_letter
            print(char.upper())
            return char
        # otherwise just echo the letter
        print(char.upper())

        # Print message with available choices
        char_list_str = ", ".join(f"'{let}'" for let in letters.upper()[:-1])
        last_char_str = letters[-1].upper()
        print(f"Type either {char_list_str} or '{last_char_str}'")
        print()
