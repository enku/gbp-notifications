"""Tests for the tasks module"""

# pylint: disable=missing-docstring


from unittest import mock

from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import pushover
from gbp_notifications.settings import Settings

from . import PUSHOVER_ENVIRON, PUSHOVER_PARAMS, TestCase

ENVIRON = {
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk"
    ":webhook=http://host.invalid/webhook|X-Pre-Shared-Key=1234",
    "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "*.build_pulled=marduk",
}


class SendmailTests(TestCase):
    @mock.patch("smtplib.SMTP_SSL")
    def test(self, mock_smtp) -> None:
        from_addr = "from@host.invalid"
        to_addr = "to@host.invalid"
        msg = "This is a test"

        tasks.sendmail(from_addr, [to_addr], msg)

        mock_smtp.assert_called_once_with("smtp.email.invalid", port=465)

        smtp = mock_smtp.return_value.__enter__.return_value
        smtp.login.assert_called_once_with("marduk@host.invalid", "supersecret")
        smtp.sendmail.assert_called_once_with(from_addr, [to_addr], msg)


@given("environ", "imports")
@where(environ=ENVIRON, imports=["requests"])
class SendHTTPRequestTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        settings = Settings.from_environ()
        tasks.send_http_request("marduk", '{"this": "that"}')

        requests = fixtures.imports["requests"]
        requests.post.assert_called_once_with(
            "http://host.invalid/webhook",
            data='{"this": "that"}',
            headers={"X-Pre-Shared-Key": "1234", "Content-Type": "application/json"},
            timeout=settings.REQUESTS_TIMEOUT,
        )


@given("environ", "imports")
@where(environ=PUSHOVER_ENVIRON, imports=["requests"])
class SendPushoverNotificationTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        settings = Settings.from_environ()

        tasks.send_pushover_notification(
            PUSHOVER_PARAMS["device"],
            PUSHOVER_PARAMS["title"],
            PUSHOVER_PARAMS["message"],
        )

        requests = fixtures.imports["requests"]
        requests.post.assert_called_once_with(
            pushover.URL, json=PUSHOVER_PARAMS, timeout=settings.REQUESTS_TIMEOUT
        )
