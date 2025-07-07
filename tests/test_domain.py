# pylint: disable=missing-docstring
from unittest import mock

from gentoo_build_publisher.signals import dispatcher
from gentoo_build_publisher.types import Build
from unittest_fixtures import Fixtures, given

from gbp_notifications import tasks

from . import lib


@given(lib.worker_run)
class DomainTests(lib.TestCase):
    """Tests for the general domain"""

    def test(self, fixtures: Fixtures) -> None:
        build = Build(machine="babette", build_id="666")

        dispatcher.emit("postpull", build=build, packages=[], gbp_metadata=None)

        fixtures.worker_run.assert_called_once_with(
            tasks.sendmail,
            "marduk@host.invalid",
            ["albert <marduk@host.invalid>"],
            mock.ANY,
        )
