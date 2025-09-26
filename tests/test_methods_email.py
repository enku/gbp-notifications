"""Tests for the methods.email module"""

# pylint: disable=missing-docstring,unused-argument
from dataclasses import replace

import gbp_testkit.fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import email
from gbp_notifications.settings import Settings
from gbp_notifications.types import Subscription

from . import lib


@given(method=lambda f: email.EmailMethod(f.settings))
@given(
    settings=lambda f: Settings(
        RECIPIENTS=(f.recipient,),
        SUBSCRIPTIONS={f.event: Subscription([f.recipient])},
        EMAIL_FROM="gbp@host.invalid",
    )
)
@given(lib.event, lib.recipient, worker_run=testkit.patch, logger=testkit.patch)
@where(worker_run__target="gentoo_build_publisher.worker.run")
@where(logger__target="gbp_notifications.methods.email.logger")
class SendTests(lib.TestCase):
    """Tests for the EmailMethod.send method"""

    def test(self, fixtures: Fixtures) -> None:
        fixtures.method.send(fixtures.event, fixtures.recipient)
        msg = fixtures.method.compose(fixtures.event, fixtures.recipient)

        self.assertEqual("gbp@host.invalid", msg["from"])
        self.assertEqual("marduk <marduk@host.invalid>", msg["to"])
        self.assertEqual("Gentoo Build Publisher: postpull", msg["subject"])
        fixtures.worker_run.assert_called_once_with(
            tasks.sendmail,
            "gbp@host.invalid",
            ["marduk <marduk@host.invalid>"],
            msg.as_string(),
        )

    def test_with_missing_template(self, fixtures: Fixtures) -> None:
        event = replace(fixtures.event, name="bogus")
        fixtures.method.send(event, fixtures.recipient)

        fixtures.worker_run.assert_not_called()
        fixtures.logger.warning.assert_called_once_with(
            "No template found for event: %s", "bogus"
        )


@given(lib.event, lib.package, lib.recipient)
class GenerateEmailContentTests(lib.TestCase):
    def test(self, fixtures: Fixtures) -> None:
        result = email.generate_email_content(fixtures.event, fixtures.recipient)

        self.assertIn(f"• {fixtures.package.cpv}", result)


@given(lib.pw_file)
class EmailPasswordTests(lib.TestCase):
    def test_email_password_string(self, fixtures: Fixtures) -> None:
        settings = Settings(EMAIL_SMTP_PASSWORD="foobar")

        self.assertEqual(email.email_password(settings), "foobar")

    def test_email_password_from_file(self, fixtures: Fixtures) -> None:
        settings = Settings(EMAIL_SMTP_PASSWORD_FILE=str(fixtures.pw_file))

        self.assertEqual(email.email_password(settings), "secret")

    def test_email_password_prefer_file(self, fixtures: Fixtures) -> None:
        settings = Settings(
            EMAIL_SMTP_PASSWORD="string", EMAIL_SMTP_PASSWORD_FILE=str(fixtures.pw_file)
        )

        self.assertEqual(email.email_password(settings), "secret")
