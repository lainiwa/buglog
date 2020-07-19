import sys
import json
import itertools
from types import ModuleType
from typing import Any, Dict, Type, Tuple, Union, Iterable, Iterator
from pathlib import Path
from datetime import datetime
from subprocess import PIPE, Popen
from importlib.util import module_from_spec, spec_from_loader
from importlib.machinery import SourceFileLoader

import click
from bs4 import BeautifulSoup  # type: ignore
from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME
from blessings import Terminal  # type: ignore
from docutils.core import publish_parts
from docutils.utils import SystemMessage
from pydantic.error_wrappers import ValidationError

from buglog.utils import split_by_func
from buglog.prompt import (
    date_to_filename,
    edit_filename_date,
    user_read_character,
)
from buglog.bootstrap import ensure_fzf, ensure_config
from contextlib import suppress


def import_config() -> ModuleType:
    """Import module as object.

    src: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly

    """

    file_path = XDG_CONFIG_HOME / __package__ / "config.py"
    module_name = "config"

    loader = SourceFileLoader(module_name, str(file_path))
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    loader.exec_module(module)

    return module


ensure_config()
ensure_fzf()

config = import_config()
if True:  # hide from isort
    from config import Bug  # type: ignore


def str_to_bug(bug_name: str) -> Type[Bug]:
    """Convert string containing bug class name to a class itself."""
    return {
        bug_class.__name__: bug_class for bug_class in Bug.__subclasses__()
    }[bug_name]


def bugs_to_rst(bugs_classes: Iterable[Type[Bug]]) -> str:
    """Convert a list of bug models to reStructuredText."""

    def _title(schema: Dict[str, Any]) -> Iterator[str]:
        title = schema["title"]
        if "description" in schema:
            title += ": " + schema["description"]
        yield title
        yield "-" * len(title)

    def _list_items(schema: Dict[str, Any]) -> Iterator[str]:
        for item, item_dict in schema["properties"].items():
            item_text = item_dict.get("title", item)
            default = item_dict.get("default", "")
            yield f"* {item_text}: {default}"

    def _single_bug(schema: Dict[str, Any]) -> str:
        lines = itertools.chain(_title(schema), _list_items(schema))
        return "\n".join(lines)

    return "\n\n".join(
        _single_bug(bug_cls.schema()) for bug_cls in bugs_classes
    )


def fuzzy_pick_bug() -> Iterator[Type[Bug]]:
    """Use fzf to pick Bug types."""

    def _pipe_to_fzf(schema: Dict[str, Any]) -> None:
        title = schema["title"]
        description = schema.get("description", title)
        line = f"{title} {description}\n"
        assert pipe.stdin is not None
        pipe.stdin.write(line.encode())

    def _parse_item(line: str) -> Type[Bug]:
        bug_name, _ = line.split(" ", 1)
        return str_to_bug(bug_name)

    fzf = XDG_DATA_HOME / __package__ / "fzf"
    pipe = Popen(
        [fzf, "--multi", "--with-nth", "2.."], stdout=PIPE, stdin=PIPE
    )

    for bug_class in Bug.__subclasses__():
        schema = bug_class.schema()
        _pipe_to_fzf(schema)

    stdout = pipe.communicate()[0]

    return map(_parse_item, stdout.decode().splitlines())


def rst_to_bugs(text: str) -> Iterator[Union[Bug, ValidationError]]:
    def _map_items_to_strings(
        bug_class: Type[Bug], line: str
    ) -> Tuple[str, str]:
        props = bug_class.schema()["properties"]
        for item_name, item_dict in props.items():
            if line.startswith(item_dict["title"]):
                return item_name, line[len(item_dict["title"]) + 1 :].strip()
        raise AssertionError()

    html = publish_parts(text, writer_name="html")["html_body"]
    soup = BeautifulSoup(html, "html.parser")
    sections = soup.select(".section") or soup.select(".document")
    for section in sections:
        title = section.h1.text
        bug_name = title.replace(":", " ").split(" ")[0]
        bug_class = str_to_bug(bug_name)
        bug_args = dict(
            _map_items_to_strings(bug_class, item.text)
            for item in section.select("li")
        )
        try:
            bug = bug_class(**bug_args)
            yield bug
        except ValidationError as e:
            yield e


def print_bugs_and_errors(
    bugs: Iterable[Bug], errs: Iterable[ValidationError]
) -> None:
    t = Terminal()

    for bug in bugs:
        print(t.bold_green("✔ ") + t.green(repr(bug)))

    for err in errs:
        model: Bug = err.model
        title = model.schema()["title"]
        for sub_err in err.errors():
            (loc,) = sub_err["loc"]
            msg = sub_err["msg"]
            print(t.bold_red("✘ ") + t.red(f"{title}.{loc}: {msg}"))


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


def cli() -> None:
    # Pick bugs via fzf
    picked_bugs = list(fuzzy_pick_bug())
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
                "Could not parse text.", "[e]dit/[c]ancel: ",
            )
            if char == "e":
                print()
                continue
            elif char == "c":
                return
        only_errs, only_bugs = split_by_func(
            items=items, predicate=lambda item: isinstance(item, Exception),
        )
        # Print the parse results
        print_bugs_and_errors(bugs=only_bugs, errs=only_errs)
        # If no problems encountered then go further
        if not only_errs:
            break
        # else if no valid bugs could be parsed from the text
        if not only_bugs:
            char = user_read_character(
                "No meaningfull bugs found.", "[e]dit/[c]ancel: ",
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
    char = user_read_character("[K]eep current date or [t]oggle: ")
    for bug in only_bugs:
        if char == "k":
            file_name = date_to_filename(
                bug_name=bug.__class__.__name__, date=datetime.now()
            )
        else:
            file_name = edit_filename_date(bug_name=bug.__class__.__name__)
        dump_bug(bug=bug, file_name=file_name)


if __name__ == "__main__":
    cli()
