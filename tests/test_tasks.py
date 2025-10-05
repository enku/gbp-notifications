"""Tests for the tasks module"""

# pylint: disable=missing-docstring


from gbp_testkit import fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import plugin, tasks
from gbp_notifications.methods import pushover
from gbp_notifications.settings import Settings

from . import lib

ENVIRON = {
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk"
    ":webhook=http://host.invalid/webhook|X-Pre-Shared-Key=1234",
    "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "*.postpull=marduk",
}


@given(SMTP=testkit.patch)
@where(SMTP__target="smtplib.SMTP_SSL")
class SendmailTests(lib.TestCase):
    def test(self, fixtures: Fixtures) -> None:
        from_addr = "from@host.invalid"
        to_addr = "to@host.invalid"
        msg = "This is a test"

        tasks.sendmail(from_addr, [to_addr], msg)

        fixtures.SMTP.assert_called_once_with("smtp.email.invalid", port=465)

        smtp = fixtures.SMTP.return_value.__enter__.return_value
        smtp.login.assert_called_once_with("marduk@host.invalid", "supersecret")
        smtp.sendmail.assert_called_once_with(from_addr, [to_addr], msg)


@given(testkit.environ, lib.imports)
@where(environ=ENVIRON, imports=["requests"])
class SendHTTPRequestTests(lib.TestCase):
    def test(self, fixtures: Fixtures) -> None:
        settings = Settings.from_environ()
        tasks.send_http_request("marduk", '{"this": "that"}')

        requests = fixtures.imports["requests"]
        requests.post.assert_called_once_with(
            "http://host.invalid/webhook",
            data='{"this": "that"}',
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"{plugin['name']}/{plugin['version']}",
                "X-Pre-Shared-Key": "1234",
            },
            timeout=settings.REQUESTS_TIMEOUT,
        )


@given(testkit.environ, lib.imports)
@where(environ=lib.PUSHOVER_ENVIRON, imports=["requests"])
class SendPushoverNotificationTests(lib.TestCase):
    def test(self, fixtures: Fixtures) -> None:
        settings = Settings.from_environ()

        tasks.send_pushover_notification(
            lib.PUSHOVER_PARAMS["device"],
            lib.PUSHOVER_PARAMS["title"],
            lib.PUSHOVER_PARAMS["message"],
        )

        requests = fixtures.imports["requests"]
        requests.post.assert_called_once_with(
            pushover.URL, json=lib.PUSHOVER_PARAMS, timeout=settings.REQUESTS_TIMEOUT
        )
