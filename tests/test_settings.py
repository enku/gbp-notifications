"""Tests for Settings"""

# pylint: disable=missing-docstring,unused-argument

from pathlib import Path

from unittest_fixtures import Fixtures, given

from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient, Subscription

from . import TestCase


@given()
class SettingTests(TestCase):
    def test_email_password_string(self, fixtures: Fixtures) -> None:
        settings = Settings(EMAIL_SMTP_PASSWORD="foobar")

        self.assertEqual(settings.email_password, "foobar")

    def test_email_password_from_file(self, fixtures: Fixtures) -> None:
        pw_file = Path(fixtures.tmpdir, "password")
        pw_file.write_text("foobar", encoding="UTF-8")

        settings = Settings(EMAIL_SMTP_PASSWORD_FILE=str(pw_file))

        self.assertEqual(settings.email_password, "foobar")

    def test_email_password_prefer_file(self, fixtures: Fixtures) -> None:
        pw_file = Path(fixtures.tmpdir, "password")
        pw_file.write_text("file", encoding="UTF-8")

        settings = Settings(
            EMAIL_SMTP_PASSWORD="string", EMAIL_SMTP_PASSWORD_FILE=str(pw_file)
        )

        self.assertEqual(settings.email_password, "file")

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
