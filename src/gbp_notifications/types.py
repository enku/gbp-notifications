"""Data types for gbp-notifications"""

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Iterable, Mapping, Protocol, Self

from gbp_notifications import methods, utils

if TYPE_CHECKING:  # pragma: nocover
    from gbp_notifications.settings import Settings


class NotificationMethod(Protocol):  # pylint: disable=too-few-public-methods
    """Interface for notification methods"""

    def __init__(self, settings: "Settings") -> None:
        """Initialize with the given Settings"""

    def send(self, event: "Event", recipient: "Recipient") -> Any:
        """Send the given Event to the given Recipient"""


@dataclass(frozen=True, kw_only=True)
class Event:
    """An Event that subscribers want to be notified of"""

    name: str
    machine: str
    data: dict[str, Any] = field(
        hash=False, compare=False, default_factory=dict, repr=False
    )

    @classmethod
    def from_string(cls, s: str) -> Self:
        """Create an Event from the given string

        String should look like "babette.build_pulled"
        """
        machine, name = utils.split_string_by(s, ".")

        return cls(name=name, machine=machine)

    @classmethod
    def from_build(cls, name, build, **data: Any) -> Self:
        """Instantiate an Event with the given name and Build"""
        return cls(name=name, machine=build.machine, data={"build": build, **data})


@dataclass(frozen=True, kw_only=True)
class Recipient:
    """Recipient of a notification"""

    name: str
    config: dict[str, str] = field(
        default_factory=dict, hash=False, compare=False, repr=False
    )

    @property
    def methods(self) -> tuple[type[NotificationMethod], ...]:
        """NotificationMethods this Recipient supports"""
        return tuple(methods.get_method(name) for name in self.config)

    @classmethod
    def from_string(cls: type[Self], string: str) -> tuple[Self, ...]:
        """Create a set of recipients from string"""
        recipients: set[Self] = set()

        for item in string.split():
            name, rest = utils.split_string_by(item, ":")

            attr_dict: dict[str, str] = {}
            for attrs in rest.split(","):
                key, value = utils.split_string_by(attrs, "=")
                attr_dict[key] = value

            recipients.add(cls(name=name, config=attr_dict))

        return tuple(utils.sort_items_by(recipients, "name"))

    @classmethod
    def from_map(
        cls: type[Self], data: Mapping[str, Mapping[str, str]]
    ) -> tuple[Self, ...]:
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

        return tuple(utils.sort_items_by(recipients, "name"))

    @classmethod
    def from_name(cls, name: str, settings: "Settings") -> Self:
        """Given the name, return the registered recipient"""
        recipients = [r for r in settings.RECIPIENTS if r.name == name]

        if not recipients:
            raise LookupError(name)

        assert len(recipients) == 1

        return cls(**asdict(recipients[0]))


class Subscription(tuple[Recipient, ...]):
    """Connection between an event and recipients"""

    @classmethod
    def from_string(
        cls, string: str, recipients: Iterable[Recipient]
    ) -> dict[Event, Self]:
        """Given the env-variable-like string, return a tuple of subscriptions"""
        # The string looks like this
        # "babette.build_pulled=albert lighthous.build_pulled=user2"
        subscriptions: dict[Event, Self] = {}

        for item in string.split():
            machine_event, names = utils.split_string_by(item, "=")
            event = Event.from_string(machine_event)
            recipient_names = set(names.split(","))
            subscribers = utils.find_subscribers(recipients, recipient_names)
            subscriptions[event] = cls(utils.sort_items_by(subscribers, "name"))

        return subscriptions

    @classmethod
    def from_map(
        cls: type[Self],
        data: Mapping[str, Mapping[str, str]],
        recipients: Iterable[Recipient],
    ) -> dict[Event, Self]:
        """Given the map return a dict of Event -> Subscription

        The map looks like this:

            {'babette': {'foo': ['marduk'], 'pull': ['marduk', 'bob']}}
        """
        subscriptions: dict[Event, Self] = {}

        for machine, attrs in data.items():
            for event_name, recipient_names in attrs.items():
                event = Event(name=event_name, machine=machine)
                subscribers = utils.find_subscribers(recipients, recipient_names)
                subscriptions[event] = cls(utils.sort_items_by(subscribers, "name"))

        return subscriptions
