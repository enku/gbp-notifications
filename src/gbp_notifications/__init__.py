"""GBP Notifications"""
from __future__ import annotations

import dataclasses
import typing as t

from gbp_notifications.methods import NotificationMethod, get_method


def split_string_by(s: str, delim: str) -> tuple[str, str]:
    """Given the string <prefix><delim><suffix> return the prefix and suffix

    Raise TypeError if delim is not found in the string.
    """
    prefix, sep, suffix = s.partition(delim)

    if not sep:
        raise TypeError(f"Invalid item in string {delim!r}")

    return prefix, suffix


def find_subscribers(
    recipients: t.Iterable[Recipient], recipient_names: t.Collection[str]
) -> set[Recipient]:
    """Given the recipients return a subset of the recipients with the given names"""
    return set(
        recipient for recipient in recipients if recipient.name in recipient_names
    )


_T = t.TypeVar("_T")


def sort_items_by(items: t.Iterable[_T], field: str) -> list[_T]:
    """Sort the given items by the given attribute on the item"""
    return sorted(items, key=lambda item: getattr(item, field))


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
            machine_event, names = split_string_by(item, "=")
            event = Event.from_string(machine_event)
            recipient_names = set(names.split(","))
            subscribers = find_subscribers(recipients, recipient_names)
            subscriptions[event] = cls(sort_items_by(subscribers, "name"))

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
                subscribers = find_subscribers(recipients, recipient_names)
                subscriptions[event] = cls(sort_items_by(subscribers, "name"))

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
        machine, name = split_string_by(s, ".")

        return cls(name=name, machine=machine)

    @classmethod
    def from_build(cls, name, build, **data: t.Any) -> t.Self:
        """Instantiate an Event with the given name and Build"""
        return cls(name=name, machine=build.machine, data={"build": build, **data})


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
            name, rest = split_string_by(item, ":")

            attr_dict: dict[str, str] = {}
            for attrs in rest.split(","):
                key, value = split_string_by(attrs, "=")
                attr_dict[key] = value

            recipients.add(cls(name=name, config=attr_dict))

        return tuple(sort_items_by(recipients, "name"))

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
        recipients = (
            cls(name=name, config=dict(attrs)) for name, attrs in data.items()
        )

        return tuple(sort_items_by(recipients, "name"))
