"""Webhook NotificationMethod"""

from dataclasses import asdict
from typing import Any, cast

import orjson
from gentoo_build_publisher import worker

from gbp_notifications import tasks
from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient

dumps = orjson.dumps  # pylint: disable=no-member

# Build fields we want to send in the payload
WANTED_FIELDS = ("machine", "build_id", "keep", "submitted", "completed", "built")


class WebhookMethod:  # pylint: disable=too-few-public-methods
    """Webhook method"""

    def __init__(self, settings: Settings) -> None:
        """Initialize with the given Settings"""
        self.settings = settings

    def send(self, event: Event, recipient: Recipient) -> Any:
        """Send the given Event to the given Recipient"""
        body = create_body(event, recipient)
        worker.run(tasks.send_http_request, recipient.name, body)


def create_body(event: Event, _recipient: Recipient) -> str:
    """Return the JSON body for the recipient

    Return None if no message could be created for the event/recipient combo.
    """
    event_dict = asdict(event)

    if build := event_dict["data"].get("build"):
        # remove logs/notes as they take up way too much payload in the HTTP request
        build = dict((k, v) for k, v in build.items() if k in WANTED_FIELDS)
        event_dict["data"]["build"] = build

    return cast(str, dumps(event_dict).decode("utf8"))
