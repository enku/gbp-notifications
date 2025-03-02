"""gbp-notifications utility functions"""

from typing import TYPE_CHECKING, Collection, Iterable, TypeVar

if TYPE_CHECKING:  # pragma: nocover
    from gbp_notifications.types import Recipient


def split_string_by(s: str, delim: str) -> tuple[str, str]:
    """Given the string <prefix><delim><suffix> return the prefix and suffix

    Raise TypeError if delim is not found in the string.
    """
    prefix, sep, suffix = s.partition(delim)

    if not sep:
        raise TypeError(f"Invalid item in string {delim!r}")

    return prefix, suffix


def find_subscribers(
    recipients: Iterable["Recipient"], recipient_names: Collection[str]
) -> set["Recipient"]:
    """Given the recipients return a subset of the recipients with the given names"""
    return set(
        recipient for recipient in recipients if recipient.name in recipient_names
    )


_T = TypeVar("_T")


def sort_items_by(items: Iterable[_T], field: str) -> list[_T]:
    """Sort the given items by the given attribute on the item"""
    return sorted(items, key=lambda item: getattr(item, field))
