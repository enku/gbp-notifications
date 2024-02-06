"""NotificationsExceptions here"""

import jinja2.exceptions


class NotificationMethodError(Exception):
    """General exception for Notification Methods"""


class MethodNotFoundError(LookupError, NotificationMethodError):
    """Raised when the requested method was not found"""


class TemplateNotFoundError(
    jinja2.exceptions.TemplateNotFound, NotificationMethodError
):
    """Raised when the given template was not found"""
