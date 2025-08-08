# pylint: disable=missing-docstring
from unittest import mock

from gentoo_build_publisher.signals import dispatcher
from unittest_fixtures import Fixtures, given

from gbp_notifications import tasks

from . import lib


@given(lib.worker_run, lib.build)
class DomainTests(lib.TestCase):
    """Tests for the general domain"""

    def test(self, fixtures: Fixtures) -> None:
        build = fixtures.build

        dispatcher.emit("postpull", build=build, packages=[], gbp_metadata=None)

        fixtures.worker_run.assert_called_once_with(
            tasks.sendmail,
            "marduk@host.invalid",
            ["albert <marduk@host.invalid>"],
            mock.ANY,
        )
