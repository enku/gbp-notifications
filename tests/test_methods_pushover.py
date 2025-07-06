"""Tests for the methods.pushover module"""

# pylint: disable=missing-docstring
from gbp_testkit import fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.signals import send_event_to_recipients

from . import fixtures as tf
from .lib import PUSHOVER_ENVIRON, PUSHOVER_PARAMS, TestCase


@given(testkit.environ, tf.worker_run, tf.event)
@where(environ=PUSHOVER_ENVIRON)
class SendTests(TestCase):
    """Tests for the PushoverMethod.send method"""

    def test(self, fixtures: Fixtures) -> None:
        worker_run = fixtures.worker_run
        send_event_to_recipients(fixtures.event)

        worker_run.assert_called_once_with(
            tasks.send_pushover_notification,
            PUSHOVER_PARAMS["device"],
            PUSHOVER_PARAMS["title"],
            PUSHOVER_PARAMS["message"],
        )
