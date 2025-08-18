"""Tests for the methods.pushover module"""

# pylint: disable=missing-docstring
from gbp_testkit import fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.signals import send_event_to_recipients

from . import lib


@given(testkit.environ, lib.event, worker_run=testkit.patch)
@where(environ=lib.PUSHOVER_ENVIRON)
@where(worker_run__target="gentoo_build_publisher.worker.run")
class SendTests(lib.TestCase):
    """Tests for the PushoverMethod.send method"""

    def test(self, fixtures: Fixtures) -> None:
        worker_run = fixtures.worker_run
        send_event_to_recipients(fixtures.event)

        worker_run.assert_called_once_with(
            tasks.send_pushover_notification,
            lib.PUSHOVER_PARAMS["device"],
            lib.PUSHOVER_PARAMS["title"],
            lib.PUSHOVER_PARAMS["message"],
        )
