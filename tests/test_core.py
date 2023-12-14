"""Tests for gbp-notifications core"""
# pylint: disable=missing-docstring
from gbp_notifications import Event, Recipient, Subscription
from gbp_notifications.methods.email import EmailMethod

from . import TestCase


class SubscriptionTests(TestCase):
    def test_registry(self) -> None:
        event1 = Event(name="pull_build", machine="babette")
        event2 = Event(name="pull_build", machine="lighthouse")
        sub1 = Subscription(event=event1)
        sub2 = Subscription(event=event2)

        # pylint: disable=protected-access
        self.assertEqual(Subscription._registry, {event1: sub1, event2: sub2})

    def test_for_event(self) -> None:
        event1 = Event(name="pull_build", machine="babette")
        Event(name="pull_build", machine="lighthouse")
        subscription = Subscription(event=event1)

        self.assertEqual(Subscription.for_event(event1), subscription)

    def test_from_string(self) -> None:
        r1 = Recipient(name="foo")
        r2 = Recipient(name="bar")
        s = "babette.build_pulled=foo lighthouse.died=bar"

        result = Subscription.from_string(s, [r1, r2])

        expected = (
            Subscription(
                event=Event(name="build_pulled", machine="babette"),
                subscribers=(Recipient(name="foo", email=None),),
            ),
            Subscription(
                event=Event(name="died", machine="lighthouse"),
                subscribers=(Recipient(name="bar", email=None),),
            ),
        )
        self.assertEqual(result, expected)


class RecipientTests(TestCase):
    def test_methods(self) -> None:
        recipient = Recipient(name="foo")
        self.assertEqual(recipient.methods, ())

        recipient = Recipient(name="foo", email="foo@host.invalid")
        self.assertEqual(recipient.methods, (EmailMethod,))

    def test_from_string(self) -> None:
        s = "bob:email=bob@host.invalid albert:email=marduk@host.invalid"

        result = Recipient.from_string(s)

        expected = (
            Recipient(name="albert", email="marduk@host.invalid"),
            Recipient(name="bob", email="bob@host.invalid"),
        )

        self.assertEqual(result, expected)
