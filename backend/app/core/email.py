"""
Email sending abstraction.

No email provider is wired into this platform (none was in the original
stack list, and picking one is a business decision — SendGrid vs SES vs
Resend vs Postmark — that shouldn't be made speculatively). This module
defines the interface every call site (auth_service) depends on, plus a
console implementation that logs the email instead of sending it — safe
for local development and CI, and enough to test the full password-reset
/ email-verification flow end-to-end without an external dependency.

To wire a real provider: implement `EmailService` and swap the instance
returned by `get_email_service()`. No router or service code changes.
"""
import abc

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("email")


class EmailService(abc.ABC):
    @abc.abstractmethod
    async def send_password_reset(self, to_email: str, reset_url: str) -> None: ...

    @abc.abstractmethod
    async def send_email_verification(self, to_email: str, verification_url: str) -> None: ...


class ConsoleEmailService(EmailService):
    """Logs the email instead of sending it. The reset/verification URL
    is logged at INFO level so it's usable during local development and
    demos without a real mail provider configured."""

    async def send_password_reset(self, to_email: str, reset_url: str) -> None:
        logger.info("email_password_reset_dispatched", to=to_email, reset_url=reset_url)

    async def send_email_verification(self, to_email: str, verification_url: str) -> None:
        logger.info(
            "email_verification_dispatched", to=to_email, verification_url=verification_url
        )


def get_email_service() -> EmailService:
    """
    Returns the configured EmailService. Currently always
    ConsoleEmailService — EMAIL_PROVIDER in .env exists as the switch
    point for when a real provider is added; branch on it here.
    """
    if settings.EMAIL_PROVIDER == "console":
        return ConsoleEmailService()
    # Future: elif settings.EMAIL_PROVIDER == "sendgrid": return SendGridEmailService()
    raise ValueError(f"Unknown EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
