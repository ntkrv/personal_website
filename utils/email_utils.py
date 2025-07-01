import smtplib
from email.mime.text import MIMEText
from flask import current_app


def send_email(subject: str, body: str, to_email: str, from_email: str = None) -> bool:
    """
    Send an email using SMTP configuration from Flask app config.

    Args:
        subject (str): Email subject.
        body (str): Email body content.
        to_email (str): Recipient email address.
        from_email (str, optional): Sender email address.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    from_email = from_email or current_app.config.get(
        "SMTP_SENDER", "noreply@example.com"
    )
    smtp_host = current_app.config.get("SMTP_HOST", "smtp.example.com")
    smtp_port = int(current_app.config.get("SMTP_PORT", 587))
    smtp_user = current_app.config.get("SMTP_USER")
    smtp_password = current_app.config.get("SMTP_PASSWORD")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}")
        return False
