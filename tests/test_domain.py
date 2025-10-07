# pylint: disable=missing-docstring
from unittest import mock

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher.signals import dispatcher
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks

from . import lib


@given(testkit.build, worker_run=testkit.patch)
@where(worker_run__target="gentoo_build_publisher.worker.run")
class DomainTests(lib.TestCase):
    """Tests for the general domain"""

    def test(self, fixtures: Fixtures) -> None:
        build = fixtures.build

        dispatcher.emit("postpull", build=build, packages=[], gbp_metadata=None)

        fixtures.worker_run.assert_called_with(
            tasks.sendmail,
            "marduk@host.invalid",
            ["albert <marduk@host.invalid>"],
            mock.ANY,
        )
