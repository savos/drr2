"""Email service for sending transactional emails."""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails."""

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        # Support both SMTP_HOST and SMTP_SERVER for backward compatibility
        self.smtp_host = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        # Support both SMTP_FROM_EMAIL and SMTP_FROM
        self.from_email = os.getenv("SMTP_FROM_EMAIL") or os.getenv("SMTP_FROM", self.smtp_user)
        self.from_name = os.getenv("SMTP_FROM_NAME", "Domain Renewal Reminder")

        # Get the path to email templates
        self.templates_dir = Path(__file__).parent / "email_templates"

        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured - emails will not be sent")
        else:
            logger.info(f"Email service configured with SMTP host: {self.smtp_host}:{self.smtp_port}")

    def _is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.smtp_user and self.smtp_password)

    def _load_template(self, template_name: str, **kwargs) -> tuple[str, str]:
        """
        Load email template and replace placeholders.

        Args:
            template_name: Name of the template file (without extension)
            **kwargs: Variables to replace in the template

        Returns:
            Tuple of (html_body, text_body)
        """
        html_path = self.templates_dir / f"{template_name}.html"
        text_path = self.templates_dir / f"{template_name}.txt"

        try:
            # Load HTML template
            with open(html_path, 'r', encoding='utf-8') as f:
                html_body = f.read()

            # Load text template
            text_body = ""
            if text_path.exists():
                with open(text_path, 'r', encoding='utf-8') as f:
                    text_body = f.read()

            # Replace placeholders (simple {{ variable }} style)
            for key, value in kwargs.items():
                placeholder = f"{{{{ {key} }}}}"
                html_body = html_body.replace(placeholder, str(value))
                text_body = text_body.replace(placeholder, str(value))

            return html_body, text_body

        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            raise

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content of the email
            text_body: Optional plain text fallback

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self._is_configured():
            logger.warning(f"Email not sent to {to_email}: SMTP not configured")
            # In development, log the email content for testing
            logger.info(f"[DEV] Email to {to_email}: {subject}")
            logger.debug(f"[DEV] Email body: {html_body}")
            return True  # Return True in dev mode so flow continues

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Add plain text part if provided
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))

            # Add HTML part
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_password_reset_email(
        self,
        to_email: str,
        reset_url: str,
        user_name: str = "User"
    ) -> bool:
        """
        Send a password reset email.

        Args:
            to_email: Recipient email address
            reset_url: URL for password reset (includes token)
            user_name: User's name for personalization

        Returns:
            True if email was sent successfully
        """
        subject = "Reset Your Password - Domain Renewal Reminder"

        # Load template and replace variables
        html_body, text_body = self._load_template(
            "reset_password",
            user_email=to_email,
            reset_link=reset_url
        )

        return self.send_email(to_email, subject, html_body, text_body)

    def send_verification_email(
        self,
        to_email: str,
        verify_url: str
    ) -> bool:
        """
        Send an email verification email.

        Args:
            to_email: Recipient email address
            verify_url: URL for email verification (includes token)

        Returns:
            True if email was sent successfully
        """
        subject = "Verify Your Email - Domain Renewal Reminder"

        # Load template and replace variables
        html_body, text_body = self._load_template(
            "verify_email",
            user_email=to_email,
            verify_link=verify_url
        )

        return self.send_email(to_email, subject, html_body, text_body)


# Global instance
email_service = EmailService()
