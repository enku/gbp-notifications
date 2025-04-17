"""Tests for the methods.webhook module"""

# pylint: disable=missing-docstring

import json
from unittest import mock

from gentoo_build_publisher.types import Build, GBPMetadata, Package, PackageMetadata
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import webhook
from gbp_notifications.signals import send_event_to_recipients
from gbp_notifications.types import Event, Recipient

from . import TestCase

ENVIRON = {
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk"
    ":webhook=http://host.invalid/webhook|X-Pre-Shared-Key=1234",
    "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "*.build_pulled=marduk",
}


@given("environ", "worker")
@where(environ=ENVIRON, worker__target=webhook)
class SendTests(TestCase):
    """Tests for the WebhookMethod.send method"""

    package = Package(
        build_id=1,
        build_time=0,
        cpv="net-libs/nghttp2-1.65.0",
        path="net-libs/nghttp2/nghttp2-1.65.0-1.gpkg.tar",
        repo="gentoo",
        size=174080,
    )
    packages = PackageMetadata(total=1, size=174080, built=[package])
    gbp_metadata = GBPMetadata(build_duration=600, packages=packages)
    data = {
        "build": Build(machine="polaris", build_id="30557"),
        "gbp_metadata": gbp_metadata,
    }
    event = Event(name="build_pulled", machine="polaris", data=data)

    def test(self, fixtures: Fixtures) -> None:
        worker = fixtures.worker
        send_event_to_recipients(self.event)

        worker.return_value.run.assert_called_once()
        args, kwargs = worker.return_value.run.call_args
        body = webhook.create_body(self.event, mock.Mock(spec=Recipient))
        self.assertEqual(args, (tasks.send_http_request, "marduk", body))
        self.assertEqual(kwargs, {})


class CreateBodyTests(TestCase):
    def test(self) -> None:
        data = {"build": Build(machine="polaris", build_id="30557")}
        event = Event(name="build_pulled", machine="polaris", data=data)

        body = webhook.create_body(event, mock.Mock())

        expected = {
            "name": "build_pulled",
            "machine": "polaris",
            "data": {"build": {"build_id": "30557", "machine": "polaris"}},
        }
        self.assertEqual(expected, json.loads(body))
