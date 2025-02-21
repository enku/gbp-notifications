# pylint: disable=missing-docstring
from django.test import TestCase as DjangoTestCase
from unittest_fixtures import given, where


@given("environ", "tmpdir")
@where(
    environ={
        "GBP_NOTIFICATIONS_RECIPIENTS": "albert:email=marduk@host.invalid",
        "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "babette.build_pulled=albert",
        "GBP_NOTIFICATIONS_EMAIL_FROM": "marduk@host.invalid",
        "GBP_NOTIFICATIONS_EMAIL_SMTP_HOST": "smtp.email.invalid",
        "GBP_NOTIFICATIONS_EMAIL_SMTP_USERNAME": "marduk@host.invalid",
        "GBP_NOTIFICATIONS_EMAIL_SMTP_PASSWORD": "supersecret",
        "BUILD_PUBLISHER_WORKER_BACKEND": "sync",
        "BUILD_PUBLISHER_JENKINS_BASE_URL": "http://jenkins.invalid/",
    }
)
class TestCase(DjangoTestCase):
    """Test case for gbp-notifications"""
