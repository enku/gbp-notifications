"""Tests for Settings"""
# pylint: disable=missing-docstring

from pathlib import Path

from gbp_notifications.settings import Settings

from . import TestCase


class SettingTests(TestCase):
    def test_email_password_string(self) -> None:
        settings = Settings(
            SUBSCRIPTIONS={}, RECIPIENTS=(), EMAIL_SMTP_PASSWORD="foobar"
        )

        self.assertEqual(settings.email_password, "foobar")

    def test_email_password_from_file(self) -> None:
        pw_file = Path(self.tmpdir) / "password"
        pw_file.write_text("foobar", encoding="UTF-8")

        settings = Settings(
            SUBSCRIPTIONS={}, RECIPIENTS=(), EMAIL_SMTP_PASSWORD_FILE=str(pw_file)
        )

        self.assertEqual(settings.email_password, "foobar")

    def test_email_password_prefer_file(self) -> None:
        pw_file = Path(self.tmpdir) / "password"
        pw_file.write_text("file", encoding="UTF-8")

        settings = Settings(
            SUBSCRIPTIONS={},
            RECIPIENTS=(),
            EMAIL_SMTP_PASSWORD="string",
            EMAIL_SMTP_PASSWORD_FILE=str(pw_file),
        )

        self.assertEqual(settings.email_password, "file")
