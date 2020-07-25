import itertools
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import Type
from typing import Union

from bs4 import BeautifulSoup  # type: ignore
from docutils.core import publish_parts
from pydantic.error_wrappers import ValidationError

from buglog.utils import Bug
from buglog.utils import str_to_bug


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
