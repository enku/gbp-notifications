"""Email NotificationMethod"""

import logging
from copy import deepcopy
from email.message import EmailMessage

from gentoo_build_publisher.settings import Settings as GBPSettings
from gentoo_build_publisher.types import GBPMetadata
from gentoo_build_publisher.worker import Worker

from gbp_notifications.exceptions import TemplateNotFoundError
from gbp_notifications.settings import Settings
from gbp_notifications.templates import load_template, render_template
from gbp_notifications.types import Event, Recipient

logger = logging.getLogger(__name__)


class EmailMethod:  # pylint: disable=too-few-public-methods
    """Email NotificationMethod

    Needs the following Settings:
        - EMAIL_FROM
        - EMAIL_SMTP
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def send(self, event: Event, recipient: Recipient) -> None:
        """Notify the given Recipient of the given Event"""
        if msg := self.create_message(event, recipient):
            worker = Worker(GBPSettings.from_environ())
            worker.run(sendmail, msg["From"], [msg["To"]], msg.as_string())

    def create_message(self, event: Event, recipient: Recipient) -> EmailMessage | None:
        """Return the email message for the recipient

        Return None if no message could be created for the event/recipient combo.
        """
        try:
            return self.compose(event, recipient)
        except TemplateNotFoundError:
            # We don't have an email template for this event. Oh well..
            logger.warning("No template found for event: %s", event.name)
            return None

    def compose(self, event: Event, recipient: Recipient) -> EmailMessage:
        """Compose message for the given event"""
        msg = set_headers(
            EmailMessage(),
            Subject=f"Gentoo Build Publisher: {event.name}",
            From=self.settings.EMAIL_FROM,
            To=f'{recipient.name.replace("_", " ")} <{recipient.config["email"]}>',
        )
        msg.set_content(generate_email_content(event, recipient))

        return msg


def set_headers(msg: EmailMessage, **headers: str) -> EmailMessage:
    """Set the given headers in the given message"""
    msg = deepcopy(msg)
    for name, value in headers.items():
        msg[name] = value

    return msg


def sendmail(from_addr: str, to_addrs: list[str], msg: str) -> None:
    """Worker function to sent the email message"""
    # pylint: disable=reimported,import-outside-toplevel,redefined-outer-name,import-self
    import smtplib

    from gbp_notifications.methods.email import logger
    from gbp_notifications.settings import Settings

    config = Settings.from_environ()

    logger.info("Sending email notification to %s", to_addrs)
    with smtplib.SMTP_SSL(config.EMAIL_SMTP_HOST, port=config.EMAIL_SMTP_PORT) as smtp:
        smtp.login(config.EMAIL_SMTP_USERNAME, config.EMAIL_SMTP_PASSWORD)
        smtp.sendmail(from_addr, to_addrs, msg)
    logger.info("Sent email notification to %s", to_addrs)


def generate_email_content(event: Event, recipient: Recipient) -> str:
    """Generate the email body"""
    gbp_meta: GBPMetadata | None = event.data.get("gbp_metadata")
    packages = gbp_meta.packages.built if gbp_meta else []
    template_name = f"email_{event.name}.eml"
    template = load_template(template_name)
    context = {"packages": packages, "recipient": recipient, "event": event.data}

    return render_template(template, context)
