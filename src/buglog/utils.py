import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec
from importlib.util import spec_from_loader
from types import ModuleType
from typing import Any
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from pydantic import BaseModel
from xdg import XDG_CONFIG_HOME

from buglog.bootstrap import ensure_config
from buglog.bootstrap import ensure_fzf


class Bug(BaseModel):
    pass


ensure_fzf()


def import_config() -> ModuleType:
    """Import module as object.

    src: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly

    Returns:
        The ``${XDG_CONFIG_HOME:-${HOME}/.config}/buglog/config.py``
        module object (assuming it is present).
    """

    file_path = XDG_CONFIG_HOME / __package__ / "config.py"
    module_name = "config"

    loader = SourceFileLoader(module_name, str(file_path))
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    loader.exec_module(module)

    return module


def get_bug_subclasses() -> List[Type[Bug]]:
    ensure_config()
    import_config()
    return Bug.__subclasses__()


T1 = TypeVar("T1")
T2 = TypeVar("T2")


def split_to_types(
    items: Iterable[Union[T1, T2, Any]], *, t1: Type[T1], t2: Type[T2]
) -> Tuple[List[T1], List[T2]]:
    """Split list into two lists, based on type.

    Parameters:
        items: Elements of two types.
        t1: first type
        t2: second type

    Returns:
        Two lists, each with object of it's own type.
        All objects which are not either of type t1 or t2 are dropped.

    Example:
        >>> nums = iter([
        ...     1, 2, 3, 4, 5, 6, 7, 8, 9,
        ...     'A', 'B', 'C', 'D', 'E', 'F',
        ...     None, print
        ... ])
        >>> split_to_types(nums, t1=int, t2=str)
        ([1, 2, 3, 4, 5, 6, 7, 8, 9], ['A', 'B', 'C', 'D', 'E', 'F'])
    """
    items = list(items)
    items_t1 = [item for item in items if isinstance(item, t1)]
    items_t2 = [item for item in items if isinstance(item, t2)]
    return items_t1, items_t2


def str_to_bug(bug_name: str) -> Type[Bug]:
    """Convert string containing bug class name to a class itself.

    Parameters:
        bug_name: The name of the Bug subclass.

    Returns:
        The bug's subclass object.
    """
    return {
        bug_class.__name__: bug_class for bug_class in get_bug_subclasses()
    }[bug_name]
