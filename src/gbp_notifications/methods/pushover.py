"""Pushover notifications

Pushover is a service for sending push notifications to Andriod, IOS and desktop
devices.

See https://pushover.net
"""

from typing import Any

from gentoo_build_publisher.settings import Settings as GBPSettings
from gentoo_build_publisher.worker import Worker

from gbp_notifications import tasks
from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient

URL = "https://api.pushover.net/1/messages.json"


class PushoverMethod:  # pylint: disable=too-few-public-methods
    """Pushover notification method"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, event: Event, recipient: Recipient) -> Any:
        """Send the given Event to the given Recipient"""
        worker = Worker(GBPSettings.from_environ())
        worker.run(
            tasks.send_pushover_notification,
            recipient.config["pushover"],
            "Gentoo Build Publisher",
            f"{event.machine}: {event.name.replace('_', ' ')}",
        )
