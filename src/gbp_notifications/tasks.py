"""gbp-notification tasks"""

# pylint: disable=cyclic-import


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


def send_http_request(recipient_name: str, body: str) -> None:
    """Worker function to call the webhook"""
    # pylint: disable=reimported,import-outside-toplevel,redefined-outer-name,import-self
    import requests

    from gbp_notifications import utils
    from gbp_notifications.methods.email import logger
    from gbp_notifications.settings import Settings
    from gbp_notifications.types import Recipient

    settings = Settings.from_environ()
    recipient = Recipient.from_name(recipient_name, settings)
    url, headers = utils.parse_config(recipient.config["webhook"])
    post = requests.post
    headers["Content-Type"] = "application/json"

    logger.info("Sending webook notification to %s", url)
    post(
        url, data=body, headers=headers, timeout=settings.REQUESTS_TIMEOUT
    ).raise_for_status()
    logger.info("Sent webhook notification to %s", url)
