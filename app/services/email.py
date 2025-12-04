"""Email service for sending verification and notification emails."""

import logging
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader

from app.constants import (
    FRONTEND_URL,
    SMTP_LOCAL_DEBUG,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_STARTTLS,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)

logger = logging.getLogger(__name__)

# Get the templates directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates" / "emails"

# Initialize Jinja2 environment
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def is_smtp_configured() -> bool:
    """Check if SMTP is properly configured.
    Returns:
        True if SMTP settings are configured, False otherwise.
    SMTP_LOCAL_DEBUG indicates if SMTP is in local debug mode (no actual email sending).
    """
    if SMTP_LOCAL_DEBUG:
        return bool(SMTP_HOST)

    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def get_mail_config() -> ConnectionConfig | None:
    """Get email configuration if SMTP is configured."""
    if not is_smtp_configured():
        return None

    return ConnectionConfig(
        MAIL_USERNAME=SMTP_USER,
        MAIL_PASSWORD=SMTP_PASSWORD,
        MAIL_FROM=SMTP_FROM_EMAIL,
        MAIL_PORT=SMTP_PORT,
        MAIL_SERVER=SMTP_HOST,
        MAIL_FROM_NAME=SMTP_FROM_NAME,
        MAIL_STARTTLS=SMTP_STARTTLS,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=bool(SMTP_USER and SMTP_PASSWORD),
        VALIDATE_CERTS=True,
    )


async def send_verification_email(email: str, token: str) -> None:
    """
    Send email verification link to user.

    If SMTP is not configured, logs the verification link to console.

    Args:
        email: User's email address
        token: Email verification token
    """
    # Generate verification link
    verification_link = f"{FRONTEND_URL}/api/v1/auth/verify-email?token={token}"

    # Render email template
    template = jinja_env.get_template("verify_email.html")
    html_content = template.render(verification_link=verification_link)

    if not is_smtp_configured():
        # Log warning and print link to console
        logger.warning(
            "SMTP is not configured. Email verification link will be printed to console."
        )
        logger.warning(f"SMTP configuration missing: SMTP_HOST={SMTP_HOST}, SMTP_USER={SMTP_USER}")
        print("\n" + "=" * 80)
        print("EMAIL VERIFICATION LINK (Debug Mode)")
        print("=" * 80)
        print(f"To: {email}")
        print(f"Subject: Email Verification")
        print(f"Verification Link: {verification_link}")
        print("=" * 80 + "\n")
        return

    # Send actual email
    try:
        mail_config = get_mail_config()
        fast_mail = FastMail(mail_config)

        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html,
        )

        await fast_mail.send_message(message)
        logger.info(f"Verification email sent successfully to {email}")

    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")
        # Fallback to console output on error
        print("\n" + "=" * 80)
        print("EMAIL SENDING FAILED - VERIFICATION LINK (Debug Mode)")
        print("=" * 80)
        print(f"To: {email}")
        print(f"Subject: Email Verification")
        print(f"Verification Link: {verification_link}")
        print(f"Error: {e}")
        print("=" * 80 + "\n")

        raise
