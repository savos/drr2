"""Email service for sending transactional emails."""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails."""

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("SMTP_FROM_NAME", "Domain Renewal Reminder")

        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured - emails will not be sent")

    def _is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.smtp_user and self.smtp_password)

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

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 24px;">Password Reset Request</h1>
    </div>

    <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
        <p style="margin-top: 0;">Hi {user_name},</p>

        <p>We received a request to reset your password for your Domain Renewal Reminder account.</p>

        <p>Click the button below to reset your password:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Reset Password</a>
        </div>

        <p style="color: #666; font-size: 14px;">This link will expire in <strong>1 hour</strong> for security reasons.</p>

        <p style="color: #666; font-size: 14px;">If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>

        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">

        <p style="color: #999; font-size: 12px; margin-bottom: 0;">
            If the button doesn't work, copy and paste this URL into your browser:<br>
            <a href="{reset_url}" style="color: #667eea; word-break: break-all;">{reset_url}</a>
        </p>
    </div>

    <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
        <p style="margin: 0;">Domain Renewal Reminder</p>
        <p style="margin: 5px 0 0 0;">This is an automated message, please do not reply.</p>
    </div>
</body>
</html>
"""

        text_body = f"""
Hi {user_name},

We received a request to reset your password for your Domain Renewal Reminder account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.

---
Domain Renewal Reminder
This is an automated message, please do not reply.
"""

        return self.send_email(to_email, subject, html_body, text_body)


# Global instance
email_service = EmailService()
