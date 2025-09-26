"""Tests for gbp_notifications.types"""

# pylint: disable=missing-docstring

from unittest_fixtures import Fixtures, given, where

from gbp_notifications.methods.email import EmailMethod
from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient, Subscription

from .lib import TestCase, recipient


@given(r1=recipient, r2=recipient)
@where(r1__name="foo", r2__name="bar")
class SubscriptionTests(TestCase):
    def test_from_string(self, fixtures: Fixtures) -> None:
        r1 = fixtures.r1
        r2 = fixtures.r2
        s = "babette.postpull=foo lighthouse.died=bar"

        result = Subscription.from_string(s, [r1, r2])

        ev1 = Event(name="postpull", machine="babette")
        ev2 = Event(name="died", machine="lighthouse")
        expected = {ev1: Subscription([r1]), ev2: Subscription([r2])}
        self.assertEqual(result, expected)


class RecipientTests(TestCase):
    def test_methods(self) -> None:
        r = Recipient(name="foo")
        self.assertEqual(r.methods, ())

        r = Recipient(name="foo", config={"email": "foo@host.invalid"})
        self.assertEqual(r.methods, (EmailMethod,))

    def test_from_string(self) -> None:
        s = "bob:email=bob@host.invalid albert:email=marduk@host.invalid"

        result = Recipient.from_string(s)

        expected = (
            Recipient(name="albert", config={"email": "marduk@host.invalid"}),
            Recipient(name="bob", config={"email": "bob@host.invalid"}),
        )

        self.assertEqual(result, expected)

    def test_from_name(self) -> None:
        r = Recipient(name="foo")
        settings = Settings(RECIPIENTS=(r,))

        self.assertEqual(Recipient.from_name("foo", settings), r)

    def test_from_name_lookuperror(self) -> None:
        settings = Settings(RECIPIENTS=())

        with self.assertRaises(LookupError):
            Recipient.from_name("foo", settings)
