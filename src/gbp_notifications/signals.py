"""Signal handlers for GBP Notifications"""
import typing as t

from gentoo_build_publisher.common import Build
from gentoo_build_publisher.signals import dispatcher

from gbp_notifications import Event, Subscription
from gbp_notifications.settings import Settings


def postpull_handler(*, build: Build, **kwargs: t.Any) -> None:
    """Signal handler for post-pulls"""
    event = Event(
        name="build_pulled", machine=build.machine, data={"build": build, **kwargs}
    )
    settings = Settings.from_environ()
    subscription = Subscription.for_event(event)

    for recipient in subscription.subscribers:
        for method in recipient.methods:
            method(settings).send(event, recipient)


dispatcher.bind(postpull=postpull_handler)
