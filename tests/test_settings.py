"""Tests for Settings"""

# pylint: disable=missing-docstring,unused-argument

from pathlib import Path

from unittest_fixtures import Fixtures, given

from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient, Subscription

from .lib import TestCase


@given()
class SettingTests(TestCase):
    def test_subs_and_reps_from_file(self, fixtures: Fixtures) -> None:
        toml = """\
[recipients]
# Comment
marduk = {email = "marduk@host.invalid"}
bob = {email = "bob@host.invalid"}

[subscriptions]
babette = {pull = ["marduk", "bob"], foo = ["marduk"]}
"""
        config_file = Path(fixtures.tmpdir, "config.toml")
        config_file.write_text(toml, encoding="UTF-8")
        settings = Settings.from_dict("", {"CONFIG_FILE": str(config_file)})

        bob = Recipient(name="bob", config={"email": "bob@host.invalid"})
        marduk = Recipient(name="marduk", config={"email": "marduk@host.invalid"})
        pull_event = Event(name="pull", machine="babette")
        foo_event = Event(name="foo", machine="babette")

        expected_subs = {
            pull_event: Subscription([bob, marduk]),
            foo_event: Subscription([marduk]),
        }
        self.assertEqual(settings.SUBSCRIPTIONS, expected_subs)

        self.assertEqual(settings.RECIPIENTS, (bob, marduk))
