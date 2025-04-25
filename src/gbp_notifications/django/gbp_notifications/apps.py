"""AppConfigs for gbp-notifications"""

from django.apps import AppConfig


class GBPNotificationsConfig(AppConfig):
    """AppConfig for gbp-notifications"""

    name = "gbp_notifications.django.gbp_notifications"
    verbose_name = "GBP-notifications"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Django app initialization"""
        # pylint: disable=import-outside-toplevel,unused-import
        # register signal handlers
        import gbp_notifications.signals
