"""
Notification methods are methods of notifying Recipients of Events. Examples might be
email or SMS.

Currently only email is supported.
"""

import importlib.metadata
from functools import lru_cache
from typing import TYPE_CHECKING

from gbp_notifications.exceptions import MethodNotFoundError

if TYPE_CHECKING:  # pragma: nocover
    from gbp_notifications.types import NotificationMethod


@lru_cache
def get_method(name: str) -> type["NotificationMethod"]:
    """Return the NotificationMethod with the given name"""
    try:
        [entry_point] = importlib.metadata.entry_points(
            group="gbp_notifications.notification_method", name=name
        )
    except ValueError:
        raise MethodNotFoundError(name) from None

    notification_method: type["NotificationMethod"] = entry_point.load()

    return notification_method
