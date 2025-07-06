"""Tests for gbp_notifications.worker"""

# pylint: disable=missing-docstring
from unittest import TestCase, mock

from gentoo_build_publisher.settings import Settings

from gbp_notifications import worker


class RunTests(TestCase):
    def test_instantiate_worker_and_call_run(self) -> None:
        with mock.patch.object(worker, "Worker") as worker_class:
            worker.run(func, 1, b=2)

        worker_class.assert_called_once_with(Settings.from_environ())
        worker_obj = worker_class.return_value
        worker_obj.run.assert_called_once_with(func, 1, b=2)


def func(a, b):  # pylint: disable=unused-argument
    pass
