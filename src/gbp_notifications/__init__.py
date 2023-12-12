"""GBP Notifications"""
from __future__ import annotations

import dataclasses
import typing as t

from gbp_notifications.methods import NotificationMethod, get_method


@dataclasses.dataclass(frozen=True, kw_only=True)
class Subscription:
    """Connection between an event and recipients"""

    event: Event
    subscribers: set[Recipient] = dataclasses.field(default_factory=set, compare=False)
    _registry: t.ClassVar = {}

    def __post_init__(self) -> None:
        self._registry[self.event] = self

    @classmethod
    def for_event(cls, event: Event) -> t.Self:
        """Return the subscription for the given event"""
        return cls._registry.get(event) or cls(event=event)

    @classmethod
    def from_string(
        cls, string: str, recipients: t.Iterable[Recipient]
    ) -> tuple[t.Self, ...]:
        """Given the env-variable-like string, return a tuple of subscriptions"""
        subscriptions: set[t.Self] = set()

        for item in string.split():
            machine_event, eq, names = item.partition("=")
            if not eq:
                raise TypeError(f"Invalid item in string {item!r}")

            machine, dot, event_name = machine_event.partition(".")
            if not dot:
                raise TypeError(f"Invalid item in string {item!r}")

            recipient_names = names.split(",")

            event = Event(name=event_name, machine=machine)
            subscription = cls.for_event(event)
            subscriptions.add(subscription)

            for recipient in recipients:
                if recipient.name in recipient_names:
                    subscription.subscribers.add(recipient)

        return tuple(
            sorted(subscriptions, key=lambda s: (s.event.name, s.event.machine))
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Event:
    """An Event that subscribers want to be notified of"""

    name: str
    machine: str
    data: dict[str, t.Any] = dataclasses.field(
        hash=False, compare=False, default_factory=dict, repr=False
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Recipient:
    """Recipient of a notification"""

    name: str
    email: str | None = None

    @property
    def methods(self) -> tuple[type[NotificationMethod], ...]:
        """NotificationMethods this Recipient supports"""
        my_methods: set[type[NotificationMethod]] = set()

        for field in dataclasses.fields(self):
            if field.name == "name" or getattr(self, field.name, None) is None:
                continue

            recipient_method = get_method(field.name)
            my_methods.add(recipient_method)

        return tuple(my_methods)

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

            recipients.add(cls(**attr_dict, name=name))

        return tuple(sorted(recipients, key=lambda r: r.name))
