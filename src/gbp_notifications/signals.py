"""Signal handlers for GBP Notifications"""

from __future__ import annotations

import typing as t

from gentoo_build_publisher.signals import dispatcher
from gentoo_build_publisher.types import Build

from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient, Subscription


class SignalHandler(t.Protocol):  # pylint: disable=too-few-public-methods
    """Signal handler function"""

    @staticmethod
    def __call__(*, build: Build, **kwargs: t.Any) -> None:
        """We handle signals"""


class _SignalHandlers:  # pylint: disable=too-few-public-methods
    """Container for signal handlers.

    This class is mainly to encapsolate the signal handlers that need a reference
    else they get garbage collected away
    """

    @staticmethod
    def get_handler(event_name: str) -> SignalHandler:
        """Signal handler factory"""

        def handler(*, build: Build, **kwargs: t.Any) -> None:
            send_event_to_recipients(Event.from_build(event_name, build, **kwargs))

        handler.__doc__ = f"SignalHandler for {event_name!r}"
        return handler

    build_pulled_handler = get_handler("build_pulled")
    dispatcher.bind(postpull=build_pulled_handler)
    build_published_handler = get_handler("build_published")
    dispatcher.bind(published=build_published_handler)


def send_event_to_recipients(event: Event) -> None:
    """Sent the given event to the given recipient given the recipient's methods"""
    settings = Settings.from_environ()
    for recipient in event_recipients(event, settings.SUBSCRIPTIONS):
        for method in recipient.methods:
            method(settings).send(event, recipient)


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
