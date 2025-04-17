"""Tests for the methods.webhook module"""

# pylint: disable=missing-docstring

import json
from unittest import mock

from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import webhook
from gbp_notifications.signals import send_event_to_recipients
from gbp_notifications.types import Recipient

from . import TestCase

ENVIRON = {
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk"
    ":webhook=http://host.invalid/webhook|X-Pre-Shared-Key=1234",
    "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "*.build_pulled=marduk",
}


@given("environ", "worker", "event")
@where(environ=ENVIRON, worker__target=webhook)
class SendTests(TestCase):
    """Tests for the WebhookMethod.send method"""

    # pylint: disable=duplicate-code

    def test(self, fixtures: Fixtures) -> None:
        worker = fixtures.worker
        send_event_to_recipients(fixtures.event)

        worker.return_value.run.assert_called_once()
        args, kwargs = worker.return_value.run.call_args
        body = webhook.create_body(fixtures.event, mock.Mock(spec=Recipient))
        self.assertEqual(args, (tasks.send_http_request, "marduk", body))
        self.assertEqual(kwargs, {})


@given("event")
class CreateBodyTests(TestCase):
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
