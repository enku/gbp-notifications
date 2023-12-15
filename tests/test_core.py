"""Tests for gbp-notifications core"""
# pylint: disable=missing-docstring
from gbp_notifications import Event, Recipient, Subscription
from gbp_notifications.methods.email import EmailMethod

from . import TestCase


class SubscriptionTests(TestCase):
    def test_from_string(self) -> None:
        r1 = Recipient(name="foo")
        r2 = Recipient(name="bar")
        s = "babette.build_pulled=foo lighthouse.died=bar"

        result = Subscription.from_string(s, [r1, r2])

        ev1 = Event(name="build_pulled", machine="babette")
        ev2 = Event(name="died", machine="lighthouse")
        expected = {
            ev1: Subscription(subscribers=()),
            ev2: Subscription(subscribers=()),
        }
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
