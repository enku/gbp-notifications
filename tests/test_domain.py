# pylint: disable=missing-docstring
from unittest import mock

from gentoo_build_publisher.signals import dispatcher
from gentoo_build_publisher.types import Build

from . import TestCase


class DomainTests(TestCase):
    """Tests for the general domain"""

    @mock.patch("gbp_notifications.tasks.sendmail")
    def test(self, mock_sendmail: mock.Mock) -> None:
        build = Build(machine="babette", build_id="666")

        dispatcher.emit("postpull", build=build, packages=[], gbp_metadata=None)

        mock_sendmail.assert_called_once()
        call_args = mock_sendmail.call_args
        from_addr, to_addr, message = call_args[0]
        self.assertEqual(from_addr, "marduk@host.invalid")
        self.assertEqual(to_addr, ["albert <marduk@host.invalid>"])
        self.assertIsInstance(message, str)
        self.assertEqual(call_args[1], {})
