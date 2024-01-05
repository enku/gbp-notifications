"""Signal handlers for GBP Notifications"""
import typing as t

from gentoo_build_publisher.common import Build
from gentoo_build_publisher.signals import dispatcher

from gbp_notifications import Event, Recipient, Subscription
from gbp_notifications.settings import Settings


class SignalHandler(t.Protocol):  # pylint: disable=too-few-public-methods
    """Signal handler function"""

    @staticmethod
    def __call__(*, build: Build, **kwargs: t.Any) -> None:
        """We handle signals"""


def send_event_to_recipients(event: Event, recipients: t.Iterable[Recipient]) -> None:
    """Sent the given event to the given recipient given the recipient's methods"""
    settings = Settings.from_environ()
    for recipient in recipients:
        for method in recipient.methods:
            method(settings).send(event, recipient)


def handle(event_name: str) -> SignalHandler:
    """Signal handler factory"""

    def handler(*, build: Build, **kwargs: t.Any) -> None:
        event = Event.from_build(event_name, build)
        subscriptions = Settings.from_environ().SUBSCRIPTIONS
        recipients = event_recipients(event, subscriptions)

        send_event_to_recipients(event, recipients)

    handler.__doc__ = f"SignalHandler for {event_name!r}"
    return handler


def event_recipients(
    event: Event, subscriptions: dict[Event, Subscription]
) -> set[Recipient]:
    """Given the subscriptions, return all recipients to the given event"""
    return {
        recipient
        for event in (*wildcard_events(event), event)
        for recipient in subscriptions.get(event, Subscription())
    }


def wildcard_events(event: Event) -> list[Event]:
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
