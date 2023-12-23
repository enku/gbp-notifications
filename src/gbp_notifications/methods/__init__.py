"""
Notification methods are methods of notifying Recipients of Events. Examples might be
email or SMS.

Currently only email is supported.
"""
from __future__ import annotations

import importlib.metadata
import typing as t
from functools import lru_cache

import jinja2.exceptions
from jinja2 import Environment, PackageLoader, Template, select_autoescape

from gbp_notifications.exceptions import MethodNotFoundError, TemplateNotFoundError

if t.TYPE_CHECKING:  # pragma: nocover
    from gbp_notifications import Event, Recipient
    from gbp_notifications.settings import Settings


class NotificationMethod(t.Protocol):  # pylint: disable=too-few-public-methods
    """Interface for notification methods"""

    def __init__(self, settings: Settings) -> None:
        """Initialize with the given Settings"""

    def send(self, event: Event, recipient: Recipient) -> t.Any:
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


def load_template(name: str) -> Template:
    """Load the template with the given name"""
    loader = PackageLoader("gbp_notifications")
    env = Environment(loader=loader, autoescape=select_autoescape(["html", "xml"]))

    try:
        return env.get_template(name)
    except jinja2.exceptions.TemplateNotFound as error:
        raise TemplateNotFoundError(name, error.message) from error


def render_template(template: Template, context: dict[str, t.Any]) -> str:
    """Render the given Template given the context"""
    return template.render(**context)
