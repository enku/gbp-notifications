"""Tests for the signal handlers"""

# pylint: disable=missing-docstring
import os
from unittest import mock

from gentoo_build_publisher.types import Build, GBPMetadata, Package, PackageMetadata

from gbp_notifications.methods import get_method
from gbp_notifications.signals import dispatcher
from gbp_notifications.types import Event, Recipient

from . import TestCase

COMMON_SETTINGS = {
    "BUILD_PUBLISHER_JENKINS_BASE_URL": "https://jenkins.invalid",
    "BUILD_PUBLISHER_STORAGE_PATH": "/dev/null",
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk:email=marduk@host.invalid",
}


def settings(**kwargs: str):
    def wrap(func):
        mock.patch.dict(os.environ, {**COMMON_SETTINGS, **kwargs}, clear=True)(func)

    return wrap


@mock.patch("gbp_notifications.methods.email.EmailMethod")
class HandlerTests(TestCase):
    @settings(GBP_NOTIFICATIONS_SUBSCRIPTIONS="*.build_published=marduk")
    def test_wildcard_machine(self, mock_get_method: mock.Mock) -> None:
        build = Build(machine="babette", build_id="934")
        event = Event(name="build_published", machine="babette")
        recipient = Recipient(name="marduk", config={"email": "marduk@host.invalid"})

        get_method.cache_clear()
        dispatcher.emit("published", build=build)

        mock_get_method.return_value.send.assert_called_once_with(event, recipient)

    @settings(GBP_NOTIFICATIONS_SUBSCRIPTIONS="babette.*=marduk")
    def test_wildcard_name(self, mock_get_method: mock.Mock) -> None:
        build = Build(machine="babette", build_id="934")
        event = Event(name="build_published", machine="babette")
        recipient = Recipient(name="marduk", config={"email": "marduk@host.invalid"})

        get_method.cache_clear()
        dispatcher.emit("published", build=build)

        mock_get_method.return_value.send.assert_called_once_with(event, recipient)

    @settings(
        GBP_NOTIFICATIONS_SUBSCRIPTIONS="babette.*=marduk *.build_published=marduk"
    )
    def test_wildcard_machine_and_name(self, mock_get_method: mock.Mock) -> None:
        # Multiple matches should only send one message per recipient
        build = Build(machine="babette", build_id="934")
        event = Event(name="build_published", machine="babette")
        recipient = Recipient(name="marduk", config={"email": "marduk@host.invalid"})

        get_method.cache_clear()
        dispatcher.emit("published", build=build)

        mock_get_method.return_value.send.assert_called_once_with(event, recipient)

    @settings(GBP_NOTIFICATIONS_SUBSCRIPTIONS="*.*=marduk")
    def test_wildcard_double(self, mock_get_method: mock.Mock) -> None:
        # Double wildcard is sent exactly once
        build = Build(machine="babette", build_id="934")
        event = Event(name="build_published", machine="babette")
        recipient = Recipient(name="marduk", config={"email": "marduk@host.invalid"})

        get_method.cache_clear()
        dispatcher.emit("published", build=build)

        mock_get_method.return_value.send.assert_called_once_with(event, recipient)

    @settings(GBP_NOTIFICATIONS_SUBSCRIPTIONS="*.*=bogus")
    def test_sub_when_recipient_does_not_exist(self, mock_get_method) -> None:
        """When subscription has a non-exisent recipient it doesn't error"""
        build = Build(machine="babette", build_id="934")

        get_method.cache_clear()
        dispatcher.emit("published", build=build)

        mock_get_method.return_value.send.assert_not_called()

    @mock.patch("gbp_notifications.signals.send_event_to_recipients")
    def test_sends_event_data(self, send_event_to_recipients, _mock_get_method) -> None:
        build = Build(machine="babette", build_id="934")
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
        self.assertEqual(event.name, "build_pulled")
        self.assertEqual(event.machine, "babette")
        self.assertEqual(event.data, data)
