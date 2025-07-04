"""Tests for the methods.email module"""

# pylint: disable=missing-docstring,unused-argument
from dataclasses import replace
from pathlib import Path

from gbp_testkit import fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import email
from gbp_notifications.settings import Settings
from gbp_notifications.types import Recipient, Subscription

from . import fixtures as tf
from .lib import TestCase


@given(tf.event, tf.worker, tf.logger)
@where(worker__target=email)
class SendTests(TestCase):
    """Tests for the EmailMethod.send method"""

    recipient = Recipient(name="marduk", config={"email": "marduk@host.invalid"})

    def test(self, fixtures: Fixtures) -> None:
        settings = Settings(
            RECIPIENTS=(self.recipient,),
            SUBSCRIPTIONS={fixtures.event: Subscription([self.recipient])},
            EMAIL_FROM="gbp@host.invalid",
        )
        method = email.EmailMethod(settings)
        method.send(fixtures.event, self.recipient)
        msg = method.compose(fixtures.event, self.recipient).as_string()

        fixtures.worker.return_value.run.assert_called_once()
        args, kwargs = fixtures.worker.return_value.run.call_args
        self.assertEqual(
            args,
            (tasks.sendmail, "gbp@host.invalid", ["marduk <marduk@host.invalid>"], msg),
        )
        self.assertEqual(kwargs, {})

    def test_with_missing_template(self, fixtures: Fixtures) -> None:
        event = replace(fixtures.event, name="bogus")
        settings = Settings(
            RECIPIENTS=(self.recipient,),
            SUBSCRIPTIONS={fixtures.event: Subscription([self.recipient])},
            EMAIL_FROM="gbp@host.invalid",
        )
        method = email.EmailMethod(settings)
        method.send(event, self.recipient)

        fixtures.worker.return_value.run.assert_not_called()
        fixtures.logger.warning.assert_called_once_with(
            "No template found for event: %s", "bogus"
        )


@given(tf.event, tf.package)
class GenerateEmailContentTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        recipient = Recipient(name="bob", config={"email": "bob@host.invalid"})

        result = email.generate_email_content(fixtures.event, recipient)

        self.assertIn(f"• {fixtures.package.cpv}", result)


@given(testkit.tmpdir)
class EmailPasswordTests(TestCase):
    def test_email_password_string(self, fixtures: Fixtures) -> None:
        settings = Settings(EMAIL_SMTP_PASSWORD="foobar")

        self.assertEqual(email.email_password(settings), "foobar")

    def test_email_password_from_file(self, fixtures: Fixtures) -> None:
        pw_file = Path(fixtures.tmpdir, "password")
        pw_file.write_text("foobar", encoding="UTF-8")

        settings = Settings(EMAIL_SMTP_PASSWORD_FILE=str(pw_file))

        self.assertEqual(email.email_password(settings), "foobar")

    def test_email_password_prefer_file(self, fixtures: Fixtures) -> None:
        pw_file = Path(fixtures.tmpdir, "password")
        pw_file.write_text("file", encoding="UTF-8")

        settings = Settings(
            EMAIL_SMTP_PASSWORD="string", EMAIL_SMTP_PASSWORD_FILE=str(pw_file)
        )

        self.assertEqual(email.email_password(settings), "file")
