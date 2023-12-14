"""Settings for gbp-notifications"""
import dataclasses as dc
import typing as t
from pathlib import Path

from gentoo_build_publisher.settings import BaseSettings

from . import Event, Recipient, Subscription


@dc.dataclass(frozen=True, kw_only=True)
class Settings(BaseSettings):
    """Settings for gbp-notifications"""

    # pylint: disable=invalid-name,too-many-instance-attributes
    env_prefix: t.ClassVar = "GBP_NOTIFICATIONS_"

    RECIPIENTS: tuple[Recipient, ...]
    SUBSCRIPTIONS: dict[Event, Subscription]

    EMAIL_FROM: str = ""
    EMAIL_SMTP_HOST: str = ""
    EMAIL_SMTP_PORT: int = 465
    EMAIL_SMTP_USERNAME: str = ""
    EMAIL_SMTP_PASSWORD: str = ""
    EMAIL_SMTP_PASSWORD_FILE: str = ""

    @classmethod
    def from_dict(cls, prefix: str, data_dict: dict[str, t.Any]) -> t.Self:
        data = data_dict.copy()

        if isinstance(recipients := data_dict.get(f"{prefix}RECIPIENTS"), str):
            data[f"{prefix}RECIPIENTS"] = Recipient.from_string(recipients)

        if isinstance(subscriptions := data_dict.get(f"{prefix}SUBSCRIPTIONS"), str):
            data[f"{prefix}SUBSCRIPTIONS"] = Subscription.from_string(
                subscriptions, data.get(f"{prefix}RECIPIENTS", ())
            )

        if data != data_dict:
            return cls.from_dict(prefix, data)
        return super().from_dict(prefix, data)

    @property
    def email_password(self) -> str:
        """Return the email password depending on the settings"""
        if path := self.EMAIL_SMTP_PASSWORD_FILE:
            return Path(path).read_text(encoding="UTF-8")
        return self.EMAIL_SMTP_PASSWORD
