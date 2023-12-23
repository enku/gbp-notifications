"""Tests for the methods module"""
# pylint: disable=missing-docstring

from gbp_notifications import methods
from gbp_notifications.exceptions import MethodNotFoundError
from gbp_notifications.methods.email import EmailMethod

from . import TestCase


class GetMethodTests(TestCase):
    def test_email(self) -> None:
        method = methods.get_method("email")

        self.assertIs(method, EmailMethod)

    def test_exception(self) -> None:
        with self.assertRaises(MethodNotFoundError):
            methods.get_method("bogus")
