"""Email NotificationMethod"""
import logging
import typing as t
from email.message import EmailMessage

import jinja2.exceptions
from gentoo_build_publisher.common import GBPMetadata
from gentoo_build_publisher.settings import Settings as GBPSettings
from gentoo_build_publisher.worker import Worker
from jinja2 import Environment, PackageLoader, Template, select_autoescape

from gbp_notifications import Event, Recipient
from gbp_notifications.settings import Settings

logger = logging.getLogger(__name__)


def load_template(name: str) -> Template:
    """Load the template with the given name"""
    loader = PackageLoader("gbp_notifications")
    env = Environment(loader=loader, autoescape=select_autoescape(["html", "xml"]))
    return env.get_template(name)


def render_template(template: Template, context: dict[str, t.Any]) -> str:
    """Render the given Template given the context"""
    return template.render(**context)


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
        try:
            msg = self.compose(event, recipient)
        except jinja2.exceptions.TemplateNotFound:
            # We don't have an email template for this event. Oh well..
            logger.warning("No template found for event: %s", event.name)
            return

        worker = Worker(GBPSettings.from_environ())
        worker.run(sendmail, msg["From"], [msg["To"]], msg.as_string())

    def compose(self, event: Event, recipient: Recipient) -> EmailMessage:
        """Compose message for the given event"""
        msg = EmailMessage()
        msg["Subject"] = f"GBP: {event.name}"
        msg["From"] = self.settings.EMAIL_FROM
        msg["To"] = f'"{recipient.name.replace("_", " ")}" <{recipient.email}>'
        msg.set_content(generate_email_content(event, recipient))

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
    packages = []
    gbp_meta: GBPMetadata | None = event.data.get("gbp_metadata")

    if gbp_meta:
        packages = gbp_meta.packages.built

    template_name = f"email_{event.name}.eml"
    template = load_template(template_name)
    context = {"packages": packages, "recipient": recipient, "event": event.data}

    return render_template(template, context)
