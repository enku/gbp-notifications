"""Signal handlers for GBP Notifications"""

from typing import Any

from gentoo_build_publisher.signals import dispatcher
from gentoo_build_publisher.types import Build

from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient, Subscription


class SignalHandler:  # pylint: disable=too-few-public-methods
    """Signal handler callable"""

    def __init__(self, event_name: str) -> None:
        self.event_name = event_name
        self.__doc__ = f"SignalHandler for {event_name!r}"

    def __call__(self, *, build: Build, **kwargs: Any) -> None:
        """We handle signals"""
        send_event_to_recipients(Event.from_build(self.event_name, build, **kwargs))


class SignalHandlers:  # pylint: disable=too-few-public-methods
    """Container for signal handlers.

    This class is mainly to encapsolate the signal handlers that need a reference
    else they get garbage collected away
    """

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or Settings.from_environ()

        self.bind(*settings.EVENTS)

    def bind(self, *signals: str) -> None:
        """Create signal handlers and bind them to the given signals"""
        for signal in signals:
            handler = SignalHandler(signal)
            dispatcher.bind(**{signal: handler})
            setattr(self, signal, handler)


def send_event_to_recipients(event: Event) -> None:
    """Sent the given event to the given recipient given the recipient's methods"""
    settings = Settings.from_environ()
    for recipient in event_recipients(event, settings.SUBSCRIPTIONS):
        for method in recipient.methods:
            method(settings).send(event, recipient)


def event_recipients(event: Event, subs: dict[Event, Subscription]) -> set[Recipient]:
    """Given the subscriptions, return all recipients to the given event"""
    e = event
    return {r for e in (*wildcard_events(e), e) for r in subs.get(e, Subscription())}


def wildcard_events(event: Event) -> list[Event]:
    """Return the given event's "wildcard" events

    The `data` field is not copied into the wildcard events
    """
    return [
        Event(name="*", machine="*"),
        Event(name="*", machine=event.machine),
        Event(name=event.name, machine="*"),
    ]


signal_handlers = SignalHandlers()
