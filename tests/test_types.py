"""Tests for gbp_notifications.types"""

# pylint: disable=missing-docstring

from unittest_fixtures import Fixtures, given, params, where

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

    def test_from_name(self) -> None:
        r = Recipient(name="foo")
        settings = Settings(RECIPIENTS=(r,))

        self.assertEqual(Recipient.from_name("foo", settings), r)

    def test_from_name_lookuperror(self) -> None:
        settings = Settings(RECIPIENTS=())

        with self.assertRaises(LookupError):
            Recipient.from_name("foo", settings)


RECIPIENTS = (
    ("", ()),
    (":email=bob@host.invalid", (("", (("email", "bob@host.invalid"),)),)),
    ("bob:email=bob@host.invalid", (("bob", (("email", "bob@host.invalid"),)),)),
    (
        "bob:email=bob@host.invalid albert:email=marduk@host.invalid",
        (
            ("bob", (("email", "bob@host.invalid"),)),
            ("albert", (("email", "marduk@host.invalid"),)),
        ),
    ),
    ("bob", (("bob", ()),)),
    (
        "bob:email=bob@host.invalid,tel=212-555-1212",
        (("bob", (("email", "bob@host.invalid"), ("tel", "212-555-1212"))),),
    ),
)


@params(recipients=RECIPIENTS)
class RecipientFromStringTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        string, values = fixtures.recipients

        recipients = Recipient.from_string(string)

        expected = {Recipient(name=v[0], config=dict(v[1])) for v in values}
        self.assertEqual(set(recipients), expected)
