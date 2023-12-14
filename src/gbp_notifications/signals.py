"""Signal handlers for GBP Notifications"""
import typing as t

from gentoo_build_publisher.common import Build
from gentoo_build_publisher.signals import dispatcher

from gbp_notifications import Event
from gbp_notifications.settings import Settings


class SignalHandler(t.Protocol):  # pylint: disable=too-few-public-methods
    """Signal handler function"""

    def __call__(self, *, build: Build, **kwargs: t.Any) -> None:
        """We handle signals"""


def handle(event_name: str) -> SignalHandler:
    """Signal handler factory"""

    def handler(*, build: Build, **kwargs: t.Any) -> None:
        event = Event(
            name=event_name, machine=build.machine, data={"build": build, **kwargs}
        )
        settings = Settings.from_environ()
        subscriptions = settings.SUBSCRIPTIONS

        if subscription := subscriptions.get(event, None):
            for recipient in subscription.subscribers:
                for method in recipient.methods:
                    method(settings).send(event, recipient)

    handler.__doc__ = f"SignalHandler for {event_name!r}"
    return handler


# Note handlers are kept as weak references in the dispatcher, so we need to keep them
# at the module level so they don't fall away
build_pulled_handler = handle("build_pulled")
dispatcher.bind(postpull=build_pulled_handler)
