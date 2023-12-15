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
        data = {"build": build, **kwargs}
        event = Event(name=event_name, machine=build.machine, data=data)
        settings = Settings.from_environ()
        subscriptions = settings.SUBSCRIPTIONS
        recipients = set()

        for event in [*expand_event(event), event]:
            if subscription := subscriptions.get(event, None):
                for recipient in subscription.subscribers:
                    recipients.add(recipient)

        for recipient in recipients:
            for method in recipient.methods:
                method(settings).send(event, recipient)

    handler.__doc__ = f"SignalHandler for {event_name!r}"
    return handler


def expand_event(event: Event) -> list[Event]:
    """Return the given event's "wildcard" events

    The `data` field is not copied into the wildcard events
    """
    return [
        Event(name="*", machine="*"),
        Event(name="*", machine=event.machine),
        Event(name=event.name, machine="*"),
    ]


# Note handlers are kept as weak references in the dispatcher, so we need to keep them
# at the module level so they don't fall away
build_pulled_handler = handle("build_pulled")
dispatcher.bind(postpull=build_pulled_handler)
build_published_handler = handle("build_published")
dispatcher.bind(published=build_published_handler)
