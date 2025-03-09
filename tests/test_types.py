"""Tests for gbp_notifications.types"""

# pylint: disable=missing-docstring

from gbp_notifications.methods.email import EmailMethod
from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient, Subscription

from . import TestCase


class SubscriptionTests(TestCase):
    def test_from_string(self) -> None:
        r1 = Recipient(name="foo")
        r2 = Recipient(name="bar")
        s = "babette.build_pulled=foo lighthouse.died=bar"

        result = Subscription.from_string(s, [r1, r2])

        ev1 = Event(name="build_pulled", machine="babette")
        ev2 = Event(name="died", machine="lighthouse")
        expected = {ev1: Subscription([r1]), ev2: Subscription([r2])}
        self.assertEqual(result, expected)


class RecipientTests(TestCase):
    def test_methods(self) -> None:
        recipient = Recipient(name="foo")
        self.assertEqual(recipient.methods, ())

        recipient = Recipient(name="foo", config={"email": "foo@host.invalid"})
        self.assertEqual(recipient.methods, (EmailMethod,))

    def test_from_string(self) -> None:
        s = "bob:email=bob@host.invalid albert:email=marduk@host.invalid"

        result = Recipient.from_string(s)

        expected = (
            Recipient(name="albert", config={"email": "marduk@host.invalid"}),
            Recipient(name="bob", config={"email": "bob@host.invalid"}),
        )

        self.assertEqual(result, expected)

    def test_from_name(self) -> None:
        recipient = Recipient(name="foo")
        settings = Settings(RECIPIENTS=(recipient,))

        self.assertEqual(Recipient.from_name("foo", settings), recipient)

    def test_from_name_lookuperror(self) -> None:
        settings = Settings(RECIPIENTS=())

        with self.assertRaises(LookupError):
            Recipient.from_name("foo", settings)
