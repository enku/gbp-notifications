# pylint: disable=missing-docstring,redefined-outer-name
from importlib import import_module
from typing import Any
from unittest import mock

from django.test import TestCase as DjangoTestCase
from gbp_testkit import fixtures as testkit
from gentoo_build_publisher.types import Build, GBPMetadata, Package, PackageMetadata
from unittest_fixtures import FixtureContext, Fixtures, fixture, given, where

from gbp_notifications.methods import email, get_method
from gbp_notifications.types import Event

PUSHOVER_PARAMS = {
    "device": "mydevice",
    "message": "polaris: build pulled",
    "title": "Gentoo Build Publisher",
    "token": "pushoverapptoken",
    "user": "pushoveruserkey",
}


PUSHOVER_ENVIRON = {
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk" ":pushover=mydevice",
    "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "*.build_pulled=marduk",
    "GBP_NOTIFICATIONS_PUSHOVER_APP_TOKEN": "pushoverapptoken",
    "GBP_NOTIFICATIONS_PUSHOVER_USER_KEY": "pushoveruserkey",
}


@given(testkit.environ, testkit.tmpdir)
@where(
    environ={
        "GBP_NOTIFICATIONS_RECIPIENTS": "albert:email=marduk@host.invalid",
        "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "babette.build_pulled=albert",
        "GBP_NOTIFICATIONS_EMAIL_FROM": "marduk@host.invalid",
        "GBP_NOTIFICATIONS_EMAIL_SMTP_HOST": "smtp.email.invalid",
        "GBP_NOTIFICATIONS_EMAIL_SMTP_USERNAME": "marduk@host.invalid",
        "GBP_NOTIFICATIONS_EMAIL_SMTP_PASSWORD": "supersecret",
        "BUILD_PUBLISHER_WORKER_BACKEND": "sync",
        "BUILD_PUBLISHER_JENKINS_BASE_URL": "http://jenkins.invalid/",
    }
)
class TestCase(DjangoTestCase):
    """Test case for gbp-notifications"""


@fixture()
def worker_run(_fixtures: Fixtures) -> FixtureContext[mock.Mock]:
    """Mock gbp_notifications.worker.run"""
    with mock.patch("gentoo_build_publisher.worker.run") as mock_obj:
        yield mock_obj


@fixture()
def imports(
    _fixtures: Fixtures, imports: list[str] | None = None
) -> FixtureContext[dict[str, mock.Mock]]:
    imports = imports or []
    imported: dict[str, mock.Mock] = {}

    def side_effect(*args, **kwargs):
        module = args[0]
        if module in imports:
            imported[module] = mock.Mock()
            return imported[module]
        return import_module(module)

    with mock.patch("builtins.__import__", side_effect=side_effect):
        yield imported


@fixture()
def package(_fixtures: Fixtures, **options: Any) -> Package:
    return Package(
        build_id=1,
        build_time=0,
        cpv="llvm-core/clang-20.1.3",
        repo="gentoo",
        path="lvm-core/clang/clang-20.1.3-1.gpkg.tar",
        size=238592,
        **options,
    )


@fixture(package)
def packages(fixtures: Fixtures) -> PackageMetadata:
    package: Package = fixtures.package
    return PackageMetadata(total=1, size=package.size, built=[package])


@fixture(packages)
def gbp_metadata(fixtures: Fixtures, build_duration: int = 3600) -> GBPMetadata:
    packages: PackageMetadata = fixtures.packages
    return GBPMetadata(build_duration=build_duration, packages=packages)


@fixture(gbp_metadata)
def event(
    fixtures: Fixtures, name: str = "build_pulled", machine: str = "polaris"
) -> Event:
    return Event(
        name=name,
        machine=machine,
        data={
            "build": Build(machine=machine, build_id="31536"),
            "gbp_metadata": fixtures.gbp_metadata,
        },
    )


@fixture()
def logger(_fixtures: Fixtures, target=email) -> FixtureContext[mock.Mock]:
    with mock.patch.object(target, "logger") as mock_logger:
        yield mock_logger


@fixture()
def caches(_fixtures: Fixtures) -> FixtureContext[None]:
    get_method.cache_clear()
    yield
    get_method.cache_clear()
