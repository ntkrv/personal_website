import os
from threading import Thread
from flask import current_app, url_for
from flask_mail import Message
from extensions import mail


def _send_in_background(msg: Message, kind: str) -> None:
    """Send off the request thread. SMTP failures are logged here —
    the request has already returned, so this is the only place they
    can surface."""
    app = current_app._get_current_object()

    def run():
        with app.app_context():
            try:
                mail.send(msg)
            except Exception:
                app.logger.exception("Failed to send %s email", kind)

    Thread(target=run, daemon=True).start()


def send_contact_email(name, email, message) -> None:
    """Notify the site owner of a new contact message. The message is
    already stored in the DB (visible in the admin dashboard), so a mail
    problem is logged rather than shown to the visitor."""
    recipient = os.getenv("MAIL_DEFAULT_RECIPIENT") or os.getenv("MAIL_USERNAME")
    if not recipient:
        current_app.logger.error(
            "Contact email not sent: MAIL_DEFAULT_RECIPIENT / MAIL_USERNAME unset."
        )
        return

    msg = Message(
        subject=f"New Contact Message from {name}",
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        recipients=[recipient],
        reply_to=email,
        body=f"From: {name} <{email}>\n\n{message}",
    )
    _send_in_background(msg, "contact")


def send_password_reset_email(recipient_email, token) -> None:
    # Sent in the background so the forgot-password response looks the
    # same (status and timing) whether or not the address matched.
    reset_url = url_for("admin_auth.reset_password", token=token, _external=True)
    subject = "Reset Your Admin Panel Password"
    body = f"To reset your password, click the link below:\n\n{reset_url}\n\nIf you didn’t request this, ignore this message."

    msg = Message(subject=subject, recipients=[recipient_email], body=body)
    _send_in_background(msg, "password reset")
