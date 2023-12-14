"""Tests for the methods.email module"""
# pylint: disable=missing-docstring
from unittest import mock

from gentoo_build_publisher.common import Build, GBPMetadata, Package, PackageMetadata

from gbp_notifications import Event, Recipient
from gbp_notifications.methods import email

from . import TestCase


class SendmailTests(TestCase):
    @mock.patch("smtplib.SMTP_SSL")
    def test(self, mock_smtp) -> None:
        from_addr = "from@host.invalid"
        to_addr = "to@host.invalid"
        msg = "This is a test"

        email.sendmail(from_addr, [to_addr], msg)

        mock_smtp.assert_called_once_with("smtp.email.invalid", port=465)

        smtp = mock_smtp.return_value.__enter__.return_value
        smtp.login.assert_called_once_with("marduk@host.invalid", "supersecret")
        smtp.sendmail.assert_called_once_with(from_addr, [to_addr], msg)


class GenerateEmailContentTests(TestCase):
    def test(self) -> None:
        package = Package(
            build_id=1,
            build_time=0,
            cpv="sys-kernel/vanilla-sources-6.6.7",
            path="/path/to/binary.tar.xz",
            repo="gentoo",
            size=50,
        )
        packages = PackageMetadata(total=1, size=50, built=[package])
        gbp_metadata = GBPMetadata(build_duration=600, packages=packages)
        data = {
            "build": Build(machine="babette", build_id="666"),
            "gbp_metadata": gbp_metadata,
        }
        event = Event(name="build_pull", machine="babette", data=data)
        recipient = Recipient(name="bob", email="bob@host.invalid")

        result = email.generate_email_content(event, recipient)

        self.assertIn("• sys-kernel/vanilla-sources-6.6.7", result)
