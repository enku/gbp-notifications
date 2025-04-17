# pylint: disable=missing-docstring
from django.test import TestCase as DjangoTestCase
from unittest_fixtures import given, where

PUSHOVER_PARAMS = {
    "device": "mydevice",
    "message": "polaris: build pulled",
    "title": "Gentoo Build Publisher",
    "token": "pushoverapptoken",
    "user": "pushoveruserkey",
}


PUSHOVER_ENVIRON = {
    "GBP_NOTIFICATIONS_RECIPIENTS": "marduk" ":pushover=mydevice",
    "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "*.build_pulled=marduk",
    "GBP_NOTIFICATIONS_PUSHOVER_APP_TOKEN": "pushoverapptoken",
    "GBP_NOTIFICATIONS_PUSHOVER_USER_KEY": "pushoveruserkey",
}


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
