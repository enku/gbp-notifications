"""Access to the Gentoo Build Publisher Worker"""

from typing import Any, Callable, ParamSpec

from gentoo_build_publisher.settings import Settings
from gentoo_build_publisher.worker import Worker

P = ParamSpec("P")


def run(func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:
    """Run the given func with args as a GBP worker task"""
    worker = Worker(Settings.from_environ())
    worker.run(func, *args, **kwargs)
