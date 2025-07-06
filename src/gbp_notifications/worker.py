"""Access to the Gentoo Build Publisher Worker"""

from typing import Any, Callable

from gentoo_build_publisher.settings import Settings
from gentoo_build_publisher.worker import Worker


def run(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """Run the given func with args as a GBP worker task"""
    worker = Worker(Settings.from_environ())
    worker.run(func, *args, **kwargs)
