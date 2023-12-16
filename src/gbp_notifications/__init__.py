"""GBP Notifications"""
from __future__ import annotations

import dataclasses
import typing as t

from gbp_notifications.methods import NotificationMethod, get_method


class Subscription(tuple["Recipient", ...]):
    """Connection between an event and recipients"""

    @classmethod
    def from_string(
        cls, string: str, recipients: t.Iterable[Recipient]
    ) -> dict[Event, t.Self]:
        """Given the env-variable-like string, return a tuple of subscriptions"""
        # The string looks like this
        # "babette.build_pulled=albert lighthous.build_pulled=user2"
        subscriptions: dict[Event, t.Self] = {}

        for item in string.split():
            machine_event, eq, names = item.partition("=")
            if not eq:
                raise TypeError(f"Invalid item in string {item!r}")

            event = Event.from_string(machine_event)
            recipient_names = names.split(",")

            subscribers = set()

            for recipient in recipients:
                if recipient.name in recipient_names:
                    subscribers.add(recipient)

            subscriptions[event] = cls(sorted(subscribers, key=lambda s: s.name))

        return subscriptions

    @classmethod
    def from_map(
        cls: type[t.Self],
        data: t.Mapping[str, t.Mapping[str, str]],
        recipients: t.Iterable[Recipient],
    ) -> dict[Event, t.Self]:
        """Given the map return a dict of Event -> Subscription

        The map looks like this:

            {'babette': {'foo': ['marduk'], 'pull': ['marduk', 'bob']}}
        """
        subscriptions: dict[Event, t.Self] = {}

        for machine, attrs in data.items():
            for event_name, recipient_names in attrs.items():
                event = Event(name=event_name, machine=machine)
                subscribers = set(
                    recipient
                    for recipient in recipients
                    if recipient.name in recipient_names
                )
                subscriptions[event] = cls(sorted(subscribers, key=lambda s: s.name))

        return subscriptions


@dataclasses.dataclass(frozen=True, kw_only=True)
class Event:
    """An Event that subscribers want to be notified of"""

    name: str
    machine: str
    data: dict[str, t.Any] = dataclasses.field(
        hash=False, compare=False, default_factory=dict, repr=False
    )

    @classmethod
    def from_string(cls, s: str) -> t.Self:
        """Create an Event from the given string

        String should look like "babette.build_pulled"
        """
        machine, dot, name = s.partition(".")

        if not dot:
            raise TypeError(f"Invalid string for Event: {s!r}")

        return cls(name=name, machine=machine)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Recipient:
    """Recipient of a notification"""

    name: str
    config: dict[str, str] = dataclasses.field(
        default_factory=dict, hash=False, compare=False
    )

    @property
    def methods(self) -> tuple[type[NotificationMethod], ...]:
        """NotificationMethods this Recipient supports"""
        return tuple(get_method(name) for name in self.config)

    @classmethod
    def from_string(cls: type[t.Self], string: str) -> tuple[t.Self, ...]:
        """Create a set of recipients from string"""
        recipients: set[t.Self] = set()

        for item in string.split():
            name, colon, rest = item.partition(":")
            if not colon:
                raise TypeError(f"Invalid item in string {item!r}")

            attr_dict: dict[str, str] = {}
            for attrs in rest.split(","):
                key, eq, value = attrs.partition("=")
                if not eq:
                    raise TypeError(r"Invalid attribute {attr!r}")

                attr_dict[key] = value

            recipients.add(cls(name=name, config=attr_dict))

        return tuple(sorted(recipients, key=lambda r: r.name))

    @classmethod
    def from_map(
        cls: type[t.Self], data: t.Mapping[str, t.Mapping[str, str]]
    ) -> tuple[t.Self, ...]:
        """Given the map return a tuple of Recipients

        The map looks like this:

            {
                'bob': {'email': 'bob@host.invalid'},
                'marduk': {'email': 'marduk@host.invalid'},
            }
        """
        recipients: set[t.Self] = set()

        for name, attrs in data.items():
            recipient = cls(name=name, config=dict(attrs))
            recipients.add(recipient)

        return tuple(sorted(recipients, key=lambda r: r.name))
