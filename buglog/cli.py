import os
import sys
import json
import tempfile
import itertools
import subprocess
from types import ModuleType
from typing import Any, Dict, Type, Tuple, Union, Iterable, Iterator
from pathlib import Path
from datetime import datetime
from subprocess import PIPE, Popen
from importlib.util import module_from_spec, spec_from_loader
from importlib.machinery import SourceFileLoader

from bs4 import BeautifulSoup  # type: ignore
from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME
from blessings import Terminal  # type: ignore
from docutils.core import publish_parts
from pydantic.error_wrappers import ValidationError

from buglog.prompt import (
    date_to_filename,
    user_keep_toggle,
    edit_filename_date,
    user_edit_write_cancel,
)
from buglog.bootstrap import ensure_fzf, ensure_config


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


def read_user_writing(template_text: str) -> str:
    """Interactively input bugs."""
    try:
        # Create temporary file and write prompts to it
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(template_text.encode())
        # Open the file with vim
        subprocess.call([os.environ.get("EDITOR", "vi"), tf.name])
        # Parse the edited file and extract the Bugs
        with open(tf.name, "r") as tf_:
            return tf_.read()

    finally:
        os.remove(tf.name)


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


def db_path() -> Path:
    """Get path to current database."""
    time_str = datetime.now().isoformat("_", "seconds")
    return XDG_DATA_HOME / __package__ / f"{time_str}.json"


def dump_bugs(path: Union[Path, str], bugs: Iterable[Bug]) -> None:
    """Dump Bugs into a JSON file."""
    data = {bug.__class__.__name__: bug.dict() for bug in bugs}

    with open(path, "w") as fout:
        json.dump(data, fout)


def cli() -> None:
    t = Terminal()

    picked_bugs = list(fuzzy_pick_bug())
    if not picked_bugs:
        return

    rst_text = None
    while True:
        # Create .rst template from the list of picked bugs
        if rst_text is None:
            rst_text = bugs_to_rst(picked_bugs)
        # Let user fill the template
        rst_text = read_user_writing(rst_text)
        # Parse filled in template into bugs and errors
        bugs_or_errs = list(rst_to_bugs(rst_text))
        only_errs = [
            item for item in bugs_or_errs if isinstance(item, ValidationError)
        ]
        only_bugs = [
            item
            for item in bugs_or_errs
            if not isinstance(item, ValidationError)
        ]
        # If no problems encountered then go further
        if not only_errs:
            break
        # Print the parse results
        print_bugs_and_errors(bugs=only_bugs, errs=only_errs)

        char = user_edit_write_cancel()
        if char == "e":
            print()
            continue
        elif char == "w":
            break
        elif char == "c":
            return

    char = user_keep_toggle()

    for bug in only_bugs:
        bug_name = bug.__class__.__name__
        data = bug.dict()

        if char == "k":
            file_name = date_to_filename(
                bug_name=bug_name, date=datetime.now()
            )
        elif char == "t":
            file_name = edit_filename_date(bug_name=bug_name)
        else:
            raise AssertionError()

        path = XDG_DATA_HOME / __package__ / file_name

        with open(path, "w") as fout:
            json.dump(data, fout)

        print(
            t.bold_green(f"Wrote {bug_name} into a file: ")
            + t.on_bright_black(f"{path}")
        )


if __name__ == "__main__":
    cli()
