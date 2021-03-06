from datetime import datetime
from typing import Iterable

import click
from blessings import Terminal
from docutils.utils import SystemMessage
from pydantic.error_wrappers import ValidationError
from pydantic.main import ModelMetaclass

from buglog.dump import dump_bug
from buglog.fuzzy import fuzzy_pick_bug
from buglog.parse_rst import bugs_to_rst
from buglog.parse_rst import rst_to_bugs
from buglog.prompt import date_to_filename
from buglog.prompt import edit_filename_date
from buglog.prompt import user_read_character
from buglog.utils import Bug
from buglog.utils import split_to_types


def print_bugs_and_errors(
    bugs: Iterable[Bug], errs: Iterable[ValidationError]
) -> None:
    t = Terminal()

    for bug in bugs:
        print(t.bold_green("✔ ") + t.green(repr(bug)))

    for err in errs:
        model = err.model
        assert isinstance(model, ModelMetaclass)
        title = model.schema()["title"]
        for sub_err in err.errors():
            (loc,) = sub_err["loc"]
            msg = sub_err["msg"]
            print(t.bold_red("✘ ") + t.red(f"{title}.{loc}: {msg}"))


def bugs_save_dialog(bugs: Iterable[Bug]) -> None:
    # Let the user choose the appropriate dates
    char = user_read_character("[K]eep current date or [t]oggle: ")
    text = ""
    for bug in bugs:
        bug_name = bug.__class__.__name__
        now = datetime.now()
        if char == "k":
            file_name = date_to_filename(bug_name=bug_name, date=now)
        else:
            default = text or now.isoformat("_", "seconds")
            file_name, text = edit_filename_date(
                bug_name=bug_name, default=default
            )
            if text == default:
                text = ""
        dump_bug(bug=bug, file_name=file_name)


def cli() -> None:
    # Pick bugs via fzf
    picked_bugs = fuzzy_pick_bug()
    if not picked_bugs:
        return

    # Parsing the bugs
    rst_text = None
    while True:
        # Create .rst template from the list of picked bugs
        if rst_text is None:
            rst_text = bugs_to_rst(picked_bugs)
        # Let user fill the template
        rst_text = click.edit(rst_text)
        # If the user did not provide any input (either '' or None) then exit
        if not rst_text:
            return
        # Parse filled in template into bugs and errors
        try:
            items = list(rst_to_bugs(rst_text))
        except SystemMessage:
            char = user_read_character(
                "Could not parse text.",
                "[e]dit/[c]ancel: ",
            )
            if char == "e":
                print()
                continue
            elif char == "c":
                return
        only_bugs, only_errs = split_to_types(
            items=items,
            t1=Bug,
            t2=ValidationError,
        )
        # Print the parse results
        print_bugs_and_errors(bugs=only_bugs, errs=only_errs)
        # If no problems encountered then go further
        if not only_errs:
            break
        # else if no valid bugs could be parsed from the text
        if not only_bugs:
            char = user_read_character(
                "No meaningfull bugs found.",
                "[e]dit/[c]ancel: ",
            )
            if char == "e":
                print()
                continue
            elif char == "c":
                return
        # else put the options to the user
        char = user_read_character(
            "Some errors found. Watcha gonna do?",
            "[e]dit/[w]rite valid/[c]ancel: ",
        )
        if char == "e":
            print()
            continue
        elif char == "w":
            break
        elif char == "c":
            return

    # Let the user choose the appropriate dates
    bugs_save_dialog(only_bugs)


@click.command()
@click.version_option(prog_name=__package__)
def main() -> None:
    cli()


if __name__ == "__main__":
    main()
