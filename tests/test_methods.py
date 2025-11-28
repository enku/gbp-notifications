"""Tests for the methods module"""

# pylint: disable=missing-docstring

from unittest_fixtures import Fixtures, params

from gbp_notifications import methods
from gbp_notifications.exceptions import MethodNotFoundError
from gbp_notifications.methods.email import EmailMethod
from gbp_notifications.methods.webhook import WebhookMethod

from .lib import TestCase


@params(method=("email", "webhook"))
@params(cls=(EmailMethod, WebhookMethod))
class GetMethodTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        method = methods.get_method(fixtures.method)

        self.assertIs(method, fixtures.cls)

        with self.assertRaises(MethodNotFoundError):
            methods.get_method("bogus")
