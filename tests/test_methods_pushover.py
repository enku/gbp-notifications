"""Tests for the methods.pushover module"""

# pylint: disable=missing-docstring
from gbp_testkit import fixtures as testkit
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import pushover
from gbp_notifications.signals import send_event_to_recipients

from . import fixtures as tf
from .lib import PUSHOVER_ENVIRON, PUSHOVER_PARAMS, TestCase


@given(testkit.environ, tf.worker, tf.event)
@where(environ=PUSHOVER_ENVIRON, worker__target=pushover)
class SendTests(TestCase):
    """Tests for the PushoverMethod.send method"""

    def test(self, fixtures: Fixtures) -> None:
        worker = fixtures.worker
        send_event_to_recipients(fixtures.event)

        worker.return_value.run.assert_called_once()
        args, kwargs = worker.return_value.run.call_args
        self.assertEqual(
            args,
            (
                tasks.send_pushover_notification,
                PUSHOVER_PARAMS["device"],
                PUSHOVER_PARAMS["title"],
                PUSHOVER_PARAMS["message"],
            ),
        )
        self.assertEqual(kwargs, {})
