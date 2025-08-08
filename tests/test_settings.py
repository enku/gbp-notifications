"""Tests for Settings"""

# pylint: disable=missing-docstring,unused-argument

from pathlib import Path

from unittest_fixtures import Fixtures, given, where

from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Subscription

from .lib import TestCase, recipient


@given(bob=recipient, marduk=recipient)
@where(bob__name="bob", bob__email="bob@host.invalid")
@where(marduk__name="marduk", marduk__email="marduk@host.invalid")
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
        bob = fixtures.bob
        marduk = fixtures.marduk
        pull_event = Event(name="pull", machine="babette")
        foo_event = Event(name="foo", machine="babette")

        expected_subs = {
            pull_event: Subscription([bob, marduk]),
            foo_event: Subscription([marduk]),
        }
        self.assertEqual(settings.SUBSCRIPTIONS, expected_subs)

        self.assertEqual(settings.RECIPIENTS, (bob, marduk))
