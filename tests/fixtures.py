"""Fixtures for gbp-notifications"""

# pylint: disable=missing-docstring,redefined-outer-name

from importlib import import_module
from unittest import mock

import gentoo_build_publisher.worker
from gbp_testkit import fixtures as testkit
from unittest_fixtures import FixtureContext, Fixtures, fixture

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
