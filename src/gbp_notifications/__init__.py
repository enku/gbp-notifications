"""GBP Notifications"""

import importlib.metadata

__version__ = importlib.metadata.version("gbp-notifications")

plugin = {
    "name": "gbp-notifications",
    "version": __version__,
    "description": "A plugin to send notifications for GBP events.",
    "app": "gbp_notifications.django.gbp_notifications",
}
