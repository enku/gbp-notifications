"""gbp-notifications utility functions"""

from typing import TYPE_CHECKING, Collection, Iterable, TypeVar

from requests.structures import CaseInsensitiveDict

if TYPE_CHECKING:  # pragma: nocover
    from gbp_notifications.types import Recipient


def split_string_by(s: str, delim: str) -> tuple[str, str]:
    """Given the string <prefix><delim><suffix> return the prefix and suffix

    Raise ValueError if delim is not found in the string.
    """
    prefix, sep, suffix = s.partition(delim)

    if not sep:
        raise ValueError(f"Invalid item in string {delim!r}")

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


def parse_config(config: str) -> tuple[str, CaseInsensitiveDict[str]]:
    """Parse the webhook config into url and headers

    The webhook config is a string that looks like this:

        "http://host.invalid/webook|X-Header-A=foo|X-Header-B=bar"

    Each item in the config is delimited by "|". The only item that is required is the
    first, which is the URL to of the webhook.  Subsequent items are headers to include
    in the request.

    Return a tuple of (url, headers) where headers is a case-insensitive dict of
    2-tuples.  For example::

        ("https://host.invalid/webook, {"X-Header-A": "foo", "X-Header-B": "bar"})
    """
    url, _, header_conf = config.partition("|")

    headers = parse_header_conf(header_conf)

    return url, headers


def parse_header_conf(header_conf: str) -> CaseInsensitiveDict[str]:
    """Parse the header portion of the webhook config.

    Return a case-insensitive dict.
    """
    return CaseInsensitiveDict(
        (key, value)
        for part in get_header_assignments(header_conf)
        for key, value in [parse_assignment(part)]
    )


def get_header_assignments(header_conf: str) -> Iterable[str]:
    """Split header_conf into it's parts.

    For example::
        >>> header_conf = "One=1 |Two=2|Three=3|"
        >>> list(get_header_assignments(header_conf))
        ['One=1', 'Two=2', 'Three=3']
    """
    for item in header_conf.split("|"):
        if item := item.strip():
            yield item


def parse_assignment(header_assignment: str) -> tuple[str, str]:
    """Parse "name=value" string into (name, value)"""
    name, equals, value = header_assignment.partition("=")
    name = name.rstrip()
    value = value.lstrip()

    if not (name and equals):
        raise ValueError(f"Invalid header assignment: {header_assignment!r}")

    return name, value
