"""Tests for the methods.email module"""

# pylint: disable=missing-docstring,unused-argument
from dataclasses import replace
from pathlib import Path

from gbp_testkit import fixtures as testkit
from unittest_fixtures import Fixtures, given

from gbp_notifications import tasks
from gbp_notifications.methods import email
from gbp_notifications.settings import Settings
from gbp_notifications.types import Recipient, Subscription

from . import lib


@given(lib.event, lib.worker_run, lib.logger)
class SendTests(lib.TestCase):
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
        msg = method.compose(fixtures.event, self.recipient)

        self.assertEqual("gbp@host.invalid", msg["from"])
        self.assertEqual("marduk <marduk@host.invalid>", msg["to"])
        self.assertEqual("Gentoo Build Publisher: build_pulled", msg["subject"])
        fixtures.worker_run.assert_called_once_with(
            tasks.sendmail,
            "gbp@host.invalid",
            ["marduk <marduk@host.invalid>"],
            msg.as_string(),
        )

    def test_with_missing_template(self, fixtures: Fixtures) -> None:
        event = replace(fixtures.event, name="bogus")
        settings = Settings(
            RECIPIENTS=(self.recipient,),
            SUBSCRIPTIONS={fixtures.event: Subscription([self.recipient])},
            EMAIL_FROM="gbp@host.invalid",
        )
        method = email.EmailMethod(settings)
        method.send(event, self.recipient)

        fixtures.worker_run.assert_not_called()
        fixtures.logger.warning.assert_called_once_with(
            "No template found for event: %s", "bogus"
        )


@given(lib.event, lib.package)
class GenerateEmailContentTests(lib.TestCase):
    def test(self, fixtures: Fixtures) -> None:
        recipient = Recipient(name="bob", config={"email": "bob@host.invalid"})

        result = email.generate_email_content(fixtures.event, recipient)

        self.assertIn(f"• {fixtures.package.cpv}", result)


@given(testkit.tmpdir)
class EmailPasswordTests(lib.TestCase):
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
