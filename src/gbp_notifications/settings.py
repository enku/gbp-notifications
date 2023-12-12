"""Settings for gbp-notifications"""
import dataclasses as dc
import typing as t

from gentoo_build_publisher.settings import BaseSettings

from . import Recipient, Subscription


@dc.dataclass(frozen=True, kw_only=True)
class Settings(BaseSettings):
    """Settings for gbp-notifications"""

    # pylint: disable=invalid-name
    env_prefix: t.ClassVar = "GBP_NOTIFICATIONS_"

    RECIPIENTS: tuple[Recipient, ...]
    SUBSCRIPTIONS: tuple[Subscription, ...]

    EMAIL_FROM: str = ""
    EMAIL_SMTP_HOST: str = ""
    EMAIL_SMTP_PORT: int = 465
    EMAIL_SMTP_USERNAME: str = ""
    EMAIL_SMTP_PASSWORD: str = ""

    @classmethod
    def from_dict(cls, prefix: str, data_dict: dict[str, t.Any]) -> t.Self:
        config = super().from_dict(prefix, data_dict)

        # pylint: disable=no-member
        if isinstance(config.RECIPIENTS, str):
            config = dc.replace(
                config, RECIPIENTS=Recipient.from_string(config.RECIPIENTS)
            )

        if isinstance(config.SUBSCRIPTIONS, str):
            config = dc.replace(
                config,
                SUBSCRIPTIONS=Subscription.from_string(
                    config.SUBSCRIPTIONS, config.RECIPIENTS
                ),
            )

        return config
