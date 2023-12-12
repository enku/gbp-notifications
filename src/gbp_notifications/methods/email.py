"""Email NotificationMethod"""
import typing as t
from email.message import EmailMessage

from gentoo_build_publisher.common import GBPMetadata
from gentoo_build_publisher.settings import Settings as BPSettings
from gentoo_build_publisher.worker import Worker
from jinja2 import Environment, PackageLoader, Template, select_autoescape

from gbp_notifications import Event, Recipient
from gbp_notifications.settings import Settings


def load_template(name: str) -> Template:
    """Load the teamplate with the given name"""
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
        settings = self.settings

        msg = EmailMessage()
        msg["Subject"] = "GBP: build pulled"
        msg["From"] = settings.EMAIL_FROM
        to = recipient.name.replace("_", " ")
        msg["To"] = f'"{to}" <{recipient.email}>'
        msg.set_content(generate_email_content(event, recipient))

        worker = Worker(BPSettings.from_environ())
        worker.run(sendmail, msg["From"], [msg["To"]], msg.as_string())


def sendmail(from_addr: str, to_addrs: list[str], msg) -> None:
    """Worker function to sent the email message"""
    # pylint: disable=reimported,import-outside-toplevel,redefined-outer-name
    import logging
    import smtplib

    logger = logging.getLogger(__name__)

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

    template = load_template("pulled.eml")
    context = {"packages": packages, "recipient": recipient, "event": event.data}

    return render_template(template, context)
