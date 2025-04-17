"""Fixtures for gbp-notifications"""

# pylint: disable=missing-docstring,redefined-outer-name

from importlib import import_module
from typing import Any
from unittest import mock

import gentoo_build_publisher.worker
from gbp_testkit import fixtures as testkit
from gentoo_build_publisher.types import Build, GBPMetadata, Package, PackageMetadata
from unittest_fixtures import FixtureContext, Fixtures, fixture

from gbp_notifications.methods import email
from gbp_notifications.types import Event

environ = testkit.environ
tmpdir = testkit.tmpdir


@fixture()
def worker(
    _fixtures: Fixtures, target=gentoo_build_publisher.worker
) -> FixtureContext[mock.Mock]:
    with mock.patch.object(target, "Worker") as mock_worker:
        yield mock_worker


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


@fixture("package")
def packages(fixtures: Fixtures) -> PackageMetadata:
    package: Package = fixtures.package
    return PackageMetadata(total=1, size=package.size, built=[package])


@fixture("packages")
def gbp_metadata(fixtures: Fixtures, build_duration: int = 3600) -> GBPMetadata:
    packages: PackageMetadata = fixtures.packages
    return GBPMetadata(build_duration=build_duration, packages=packages)


@fixture("gbp_metadata")
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
