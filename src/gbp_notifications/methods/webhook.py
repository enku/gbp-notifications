"""Webhook NotificationMethod"""

from typing import Any, cast

import orjson
from gentoo_build_publisher.settings import Settings as GBPSettings
from gentoo_build_publisher.worker import Worker

from gbp_notifications import tasks
from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient


class WebhookMethod:  # pylint: disable=too-few-public-methods
    """Webhook method"""

    def __init__(self, settings: Settings) -> None:
        """Initialize with the given Settings"""
        self.settings = settings

    def send(self, event: Event, recipient: Recipient) -> Any:
        """Send the given Event to the given Recipient"""
        if body := create_body(event, recipient):
            worker = Worker(GBPSettings.from_environ())
            worker.run(tasks.send_http_request, recipient.name, body)


def create_body(event: Event, _recipient: Recipient) -> str:
    """Return the JSON body for the recipient

    Return None if no message could be created for the event/recipient combo.
    """
    return cast(str, orjson.dumps(event).decode("utf8"))  # pylint: disable=no-member
