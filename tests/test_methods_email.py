"""Tests for the methods.email module"""

# pylint: disable=missing-docstring
from unittest import mock

from gentoo_build_publisher.types import Build, GBPMetadata, Package, PackageMetadata

from gbp_notifications import tasks
from gbp_notifications.methods import email
from gbp_notifications.settings import Settings
from gbp_notifications.types import Event, Recipient, Subscription

from . import TestCase


@mock.patch.object(email, "Worker")
class SendTests(TestCase):
    """Tests for the EmailMethod.send method"""

    event = Event(
        name="build_pulled",
        machine="babette",
        data={"build": Build(machine="babette", build_id="25")},
    )
    recipient = Recipient(name="marduk", config={"email": "marduk@host.invalid"})
    settings = Settings(
        RECIPIENTS=(recipient,),
        SUBSCRIPTIONS={event: Subscription([recipient])},
        EMAIL_FROM="gbp@host.invalid",
    )
    method = email.EmailMethod(settings)
    msg = method.compose(event, recipient).as_string()

    def test(self, mock_worker) -> None:
        self.method.send(self.event, self.recipient)

        mock_worker.return_value.run.assert_called_once()
        args, kwargs = mock_worker.return_value.run.call_args
        self.assertEqual(
            args,
            (
                tasks.sendmail,
                "gbp@host.invalid",
                ["marduk <marduk@host.invalid>"],
                self.msg,
            ),
        )
        self.assertEqual(kwargs, {})

    @mock.patch.object(email, "logger")
    def test_with_missing_template(self, mock_logger, mock_worker) -> None:
        event = Event(
            name="bogus",
            machine="babette",
            data={"build": Build(machine="babette", build_id="25")},
        )
        self.method.send(event, self.recipient)

        mock_worker.return_value.run.assert_not_called()
        mock_logger.warning.assert_called_once_with(
            "No template found for event: %s", "bogus"
        )


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
        event = Event(name="build_pulled", machine="babette", data=data)
        recipient = Recipient(name="bob", config={"email": "bob@host.invalid"})

        result = email.generate_email_content(event, recipient)

        self.assertIn("• sys-kernel/vanilla-sources-6.6.7", result)
