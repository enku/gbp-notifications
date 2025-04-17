"""Tests for the methods.pushover module"""

# pylint: disable=missing-docstring
from gentoo_build_publisher.types import Build, GBPMetadata, Package, PackageMetadata
from unittest_fixtures import Fixtures, given, where

from gbp_notifications import tasks
from gbp_notifications.methods import pushover
from gbp_notifications.signals import send_event_to_recipients
from gbp_notifications.types import Event

from . import PUSHOVER_ENVIRON, PUSHOVER_PARAMS, TestCase


@given("environ", "worker")
@where(environ=PUSHOVER_ENVIRON, worker__target=pushover)
class SendTests(TestCase):
    """Tests for the PushoverMethod.send method"""

    # pylint: disable=duplicate-code

    package = Package(
        build_id=1,
        build_time=0,
        cpv="llvm-core/clang-20.1.3",
        path="llvm-core/clang/clang-20.1.3-1.gpkg.tar",
        repo="gentoo",
        size=2385920,
    )
    packages = PackageMetadata(total=1, size=2385920, built=[package])
    gbp_metadata = GBPMetadata(build_duration=36000, packages=packages)
    data = {
        "build": Build(machine="polaris", build_id="31536"),
        "gbp_metadata": gbp_metadata,
    }
    event = Event(name="build_pulled", machine="polaris", data=data)

    def test(self, fixtures: Fixtures) -> None:
        worker = fixtures.worker
        send_event_to_recipients(self.event)

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
