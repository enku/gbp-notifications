"""Webhook NotificationMethod"""

from typing import Any, Iterable, cast

import orjson
from gentoo_build_publisher.settings import Settings as GBPSettings
from gentoo_build_publisher.worker import Worker
from requests.structures import CaseInsensitiveDict

from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient

REQUEST_TIMEOUT = 10


class WebhookMethod:  # pylint: disable=too-few-public-methods
    """Webhook method"""

    def __init__(self, settings: Settings) -> None:
        """Initialize with the given Settings"""
        self.settings = settings

    def send(self, event: Event, recipient: Recipient) -> Any:
        """Send the given Event to the given Recipient"""
        if body := create_body(event, recipient):
            worker = Worker(GBPSettings.from_environ())
            worker.run(send_request, recipient.name, body)


def send_request(recipient_name: str, body: str) -> None:
    """Worker function to call the webhook"""
    # pylint: disable=reimported,import-outside-toplevel,redefined-outer-name,import-self
    import requests

    from gbp_notifications.methods.email import logger
    from gbp_notifications.settings import Settings

    recipient = Recipient.from_name(recipient_name, Settings.from_environ())
    url, headers = parse_config(recipient.config["webhook"])
    post = requests.post
    headers["Content-Type"] = "application/json"

    logger.info("Sending webook notification to %s", url)
    post(url, data=body, headers=headers, timeout=REQUEST_TIMEOUT).raise_for_status()
    logger.info("Sent webhook notification to %s", url)


def create_body(event: Event, _recipient: Recipient) -> str:
    """Return the JSON body for the recipient

    Return None if no message could be created for the event/recipient combo.
    """
    return cast(str, orjson.dumps(event).decode("utf8"))  # pylint: disable=no-member


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
