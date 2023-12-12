"""
Notification methods are methods of notifying Recipients of Events. Examples might be
email or SMS.

Currently only email is supported.
"""
from __future__ import annotations

import importlib.metadata
import typing
from functools import lru_cache

if typing.TYPE_CHECKING:  # pragma: nocover
    from gbp_notifications import Event, Recipient
    from gbp_notifications.settings import Settings


class MethodNotFoundError(LookupError):
    """Raised when the requested method was not found"""


class NotificationMethod(typing.Protocol):  # pylint: disable=too-few-public-methods
    """Interface for notification methods"""

    def __init__(self, settings: Settings) -> None:
        """Initialize with the given Settings"""

    def send(self, event: Event, recipient: Recipient) -> typing.Any:
        """Send the given Event to the given Recipient"""


@lru_cache
def get_method(name: str) -> type[NotificationMethod]:
    """Return the NotificationMethod with the given name"""
    try:
        [entry_point] = importlib.metadata.entry_points(
            group="gbp_notifications.notification_method", name=name
        )
    except ValueError:
        raise MethodNotFoundError(name) from None

    notification_method: type[NotificationMethod] = entry_point.load()

    return notification_method
