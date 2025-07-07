"""Tests for the methods.webhook module"""

# pylint: disable=missing-docstring

import json
from unittest import mock

from gbp_testkit import fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import webhook
from gbp_notifications.signals import send_event_to_recipients
from gbp_notifications.types import Recipient

from . import lib

ENVIRON = {
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk"
    ":webhook=http://host.invalid/webhook|X-Pre-Shared-Key=1234",
    "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "*.build_pulled=marduk",
}


@given(testkit.environ, lib.worker_run, lib.event)
@where(environ=ENVIRON)
class SendTests(lib.TestCase):
    """Tests for the WebhookMethod.send method"""

    # pylint: disable=duplicate-code

    def test(self, fixtures: Fixtures) -> None:
        send_event_to_recipients(fixtures.event)

        body = webhook.create_body(fixtures.event, mock.Mock(spec=Recipient))
        worker_run = fixtures.worker_run
        worker_run.assert_called_once_with(tasks.send_http_request, "marduk", body)


@given(lib.event)
class CreateBodyTests(lib.TestCase):
    def test(self, fixtures: Fixtures) -> None:
        body = webhook.create_body(fixtures.event, mock.Mock())

        expected = {
            "name": "build_pulled",
            "machine": "polaris",
            "data": {
                "build": {"build_id": "31536", "machine": "polaris"},
                "gbp_metadata": mock.ANY,
            },
        }
        self.assertEqual(expected, json.loads(body))
