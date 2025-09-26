"""Tests for the signal handlers"""

# pylint: disable=missing-docstring,unused-argument
import os
from unittest import mock

from gbp_testkit import fixtures as testkit
from gentoo_build_publisher.types import GBPMetadata, Package, PackageMetadata
from unittest_fixtures import Fixtures, given, where

from gbp_notifications.signals import dispatcher

from . import lib

COMMON_SETTINGS = {
    "BUILD_PUBLISHER_JENKINS_BASE_URL": "https://jenkins.invalid",
    "BUILD_PUBLISHER_STORAGE_PATH": "/dev/null",
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk:email=marduk@host.invalid",
}

environ = os.environ


@given(lib.caches, testkit.environ, lib.recipient, testkit.build, lib.event)
@given(method=testkit.patch)
@where(environ=COMMON_SETTINGS, environ__clear=True, event__name="published")
@where(method__target="gbp_notifications.methods.email.EmailMethod")
class HandlerTests(lib.TestCase):
    def test_wildcard_machine(self, fixtures: Fixtures) -> None:
        environ["GBP_NOTIFICATIONS_SUBSCRIPTIONS"] = "*.published=marduk"
        build = fixtures.build
        event = fixtures.event
        recipient = fixtures.recipient

        dispatcher.emit("published", build=build)

        fixtures.method.return_value.send.assert_called_once_with(event, recipient)

    def test_wildcard_name(self, fixtures: Fixtures) -> None:
        environ["GBP_NOTIFICATIONS_SUBSCRIPTIONS"] = "babette.*=marduk"
        build = fixtures.build
        event = fixtures.event
        recipient = fixtures.recipient

        dispatcher.emit("published", build=build)

        fixtures.method.return_value.send.assert_called_once_with(event, recipient)

    def test_wildcard_machine_and_name(self, fixtures: Fixtures) -> None:
        # Multiple matches should only send one message per recipient
        environ["GBP_NOTIFICATIONS_SUBSCRIPTIONS"] = (
            "babette.*=marduk *.published=marduk"
        )
        build = fixtures.build
        event = fixtures.event
        recipient = fixtures.recipient

        dispatcher.emit("published", build=build)

        fixtures.method.return_value.send.assert_called_once_with(event, recipient)

    def test_wildcard_double(self, fixtures: Fixtures) -> None:
        # Double wildcard is sent exactly once
        environ["GBP_NOTIFICATIONS_SUBSCRIPTIONS"] = "*.*=marduk"
        build = fixtures.build
        event = fixtures.event
        recipient = fixtures.recipient

        dispatcher.emit("published", build=build)

        fixtures.method.return_value.send.assert_called_once_with(event, recipient)

    def test_sub_when_recipient_does_not_exist(self, fixtures: Fixtures) -> None:
        """When subscription has a non-exisent recipient it doesn't error"""
        environ["GBP_NOTIFICATIONS_SUBSCRIPTIONS"] = "*.*=bogus"
        build = fixtures.build

        dispatcher.emit("published", build=build)

        fixtures.method.return_value.send.assert_not_called()

    @mock.patch("gbp_notifications.signals.send_event_to_recipients")
    def test_sends_event_data(
        self, send_event_to_recipients, fixtures: Fixtures
    ) -> None:
        build = fixtures.build
        package = Package(
            build_id=1,
            build_time=12345,
            cpv="media-sound/sox-14.4.2_p20210509-r2",
            path="/path/to/binary.tar.xz",
            repo="gentoo",
            size=120,
        )
        packages = PackageMetadata(total=1, size=50, built=[package])
        gbp_metadata = GBPMetadata(build_duration=600, packages=packages)
        dispatcher.emit(
            "postpull", build=build, packages=[package], gbp_metadata=gbp_metadata
        )
        data = {"build": build, "packages": [package], "gbp_metadata": gbp_metadata}
        event = send_event_to_recipients.call_args[0][0]
        self.assertEqual(event.name, "postpull")
        self.assertEqual(event.machine, "babette")
        self.assertEqual(event.data, data)
