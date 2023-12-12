import os
from unittest import mock

import tempfile
from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):
    """Test case for gbp-notifications"""

    def setUp(self) -> None:
        super().setUp()

        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)

        env = {
            "GBP_NOTIFICATIONS_RECIPIENTS": "albert:email=marduk@host.invalid",
            "GBP_NOTIFICATIONS_SUBSCRIPTIONS": "babette.build_pulled=albert",
            "GBP_NOTIFICATIONS_EMAIL_FROM": "marduk@host.invalid",
            "GBP_NOTIFICATIONS_EMAIL_SMTP_HOST": "smtp.email.invalid",
            "GBP_NOTIFICATIONS_EMAIL_SMTP_USERNAME": "marduk@host.invalid",
            "GBP_NOTIFICATIONS_EMAIL_SMTP_PASSWORD": "supersecret",
            "BUILD_PUBLISHER_WORKER_BACKEND": "sync",
            "BUILD_PUBLISHER_JENKINS_BASE_URL": "http://jenkins.invalid/",
            "BUILD_PUBLISHER_STORAGE_PATH": tmpdir.name,
        }
        patcher = mock.patch.dict(os.environ, env, clear=True)
        self.addCleanup(patcher.stop)
        patcher.start()
