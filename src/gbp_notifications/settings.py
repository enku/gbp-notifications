"""Settings for gbp-notifications"""

import dataclasses as dc
import tomllib
import typing as t
from pathlib import Path

from gentoo_build_publisher.settings import BaseSettings

from .types import Event, Recipient, Subscription


@dc.dataclass(frozen=True, kw_only=True)
class Settings(BaseSettings):
    """Settings for gbp-notifications"""

    # pylint: disable=invalid-name,too-many-instance-attributes
    env_prefix: t.ClassVar = "GBP_NOTIFICATIONS_"

    RECIPIENTS: tuple[Recipient, ...] = dc.field(default_factory=tuple)
    SUBSCRIPTIONS: dict[Event, Subscription] = dc.field(default_factory=dict)

    # If initializing with .from_dict() (and .from_environ()) use this (TOML) file to
    # configure RECIPIENTS and SUBSCRIPTIONS
    CONFIG_FILE: str = ""

    EMAIL_FROM: str = ""
    EMAIL_SMTP_HOST: str = ""
    EMAIL_SMTP_PORT: int = 465
    EMAIL_SMTP_USERNAME: str = ""
    EMAIL_SMTP_PASSWORD: str = ""
    EMAIL_SMTP_PASSWORD_FILE: str = ""
    REQUESTS_TIMEOUT: int = 10

    # Pushover
    PUSHOVER_USER_KEY: str = ""
    PUSHOVER_APP_TOKEN: str = ""

    @classmethod
    def from_dict(cls, prefix: str, data_dict: dict[str, t.Any]) -> t.Self:
        data = data_dict.copy()

        if isinstance(recipients := data_dict.get(f"{prefix}RECIPIENTS"), str):
            data[f"{prefix}RECIPIENTS"] = Recipient.from_string(recipients)

        if isinstance(subscriptions := data_dict.get(f"{prefix}SUBSCRIPTIONS"), str):
            data[f"{prefix}SUBSCRIPTIONS"] = Subscription.from_string(
                subscriptions, data.get(f"{prefix}RECIPIENTS", ())
            )

        if config_file := data.get(f"{prefix}CONFIG_FILE"):
            with Path(config_file).open("rb") as fp:
                config = tomllib.load(fp)

            recipients = Recipient.from_map(config.get("recipients", {}))
            subscriptions = Subscription.from_map(
                config.get("subscriptions", {}), recipients
            )
            data[f"{prefix}RECIPIENTS"] = recipients
            data[f"{prefix}SUBSCRIPTIONS"] = subscriptions

        if data != data_dict:
            return cls.from_dict(prefix, data)
        return super().from_dict(prefix, data)

    @property
    def email_password(self) -> str:
        """Return the email password depending on the settings"""
        if path := self.EMAIL_SMTP_PASSWORD_FILE:
            return Path(path).read_text(encoding="UTF-8")
        return self.EMAIL_SMTP_PASSWORD
