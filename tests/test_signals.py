"""Tests for the signal handlers"""
# pylint: disable=missing-docstring
import os
from unittest import mock

from gentoo_build_publisher.common import Build

from gbp_notifications import Event, Recipient
from gbp_notifications.methods import get_method
from gbp_notifications.signals import dispatcher

from . import TestCase

COMMON_SETTINGS = {
    "BUILD_PUBLISHER_JENKINS_BASE_URL": "https://jenkins.invalid",
    "BUILD_PUBLISHER_STORAGE_PATH": "/dev/null",
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk:email=marduk@host.invalid",
}


def settings(**kwargs: str):
    return mock.patch.dict(os.environ, {**COMMON_SETTINGS, **kwargs}, clear=True)


@mock.patch("gbp_notifications.methods.email.EmailMethod")
class HandlerTests(TestCase):
    @settings(GBP_NOTIFICATIONS_SUBSCRIPTIONS="*.build_published=marduk")
    def test_wildcard_machine(self, mock_get_method: mock.Mock) -> None:
        build = Build(machine="babette", build_id="934")
        event = Event(name="build_published", machine="babette")
        recipient = Recipient(name="marduk", email="marduk@host.invalid")

        get_method.cache_clear()
        dispatcher.emit("published", build=build)

        mock_get_method.return_value.send.assert_called_once_with(event, recipient)

    @settings(GBP_NOTIFICATIONS_SUBSCRIPTIONS="babette.*=marduk")
    def test_wildcard_name(self, mock_get_method: mock.Mock) -> None:
        build = Build(machine="babette", build_id="934")
        event = Event(name="build_published", machine="babette")
        recipient = Recipient(name="marduk", email="marduk@host.invalid")

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
        recipient = Recipient(name="marduk", email="marduk@host.invalid")

        get_method.cache_clear()
        dispatcher.emit("published", build=build)

        mock_get_method.return_value.send.assert_called_once_with(event, recipient)

    @settings(GBP_NOTIFICATIONS_SUBSCRIPTIONS="*.*=marduk")
    def test_wildcard_double(self, mock_get_method: mock.Mock) -> None:
        # Double wildcard is sent exactly once
        build = Build(machine="babette", build_id="934")
        event = Event(name="build_published", machine="babette")
        recipient = Recipient(name="marduk", email="marduk@host.invalid")

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
