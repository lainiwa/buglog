from typing import Tuple, TypeVar, Callable, Iterable

T = TypeVar("T")


def split_by_func(
    items: Iterable[T], predicate: Callable[[T], bool]
) -> Tuple[Iterable[T], Iterable[T]]:
    """Split list into two lists, based on predicate.

    Parameters:
        items: Elements to run predicate agains.
        predicate: The test function.

    Returns:
        Two lists: the one which elements fit the predicate,
        and the one with don't.
    """
    mapped_items = [(predicate(item), item) for item in items]
    items_t = [item for b, item in mapped_items if b]
    items_f = [item for b, item in mapped_items if not b]
    return items_t, items_f
