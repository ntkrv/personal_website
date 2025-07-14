import os
from threading import Thread
from flask import current_app, url_for
from flask_mail import Message
from extensions import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_contact_email(name, email, message):
    try:
        recipient = os.getenv("MAIL_DEFAULT_RECIPIENT") or os.getenv("MAIL_USERNAME")
        if not recipient:
            raise ValueError("Recipient email is not set in environment variables.")

        msg = Message(
            subject=f"New Contact Message from {name}",
            sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
            recipients=[recipient],
            body=f"From: {name} <{email}>\n\n{message}",
        )

        Thread(
            target=send_async_email, args=(current_app._get_current_object(), msg)
        ).start()
        return True

    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return False


def send_password_reset_email(recipient_email, token):
    reset_url = url_for("admin_auth.reset_password", token=token, _external=True)
    subject = "Reset Your Admin Panel Password"
    body = f"To reset your password, click the link below:\n\n{reset_url}\n\nIf you didn’t request this, ignore this message."

    msg = Message(subject=subject, recipients=[recipient_email], body=body)
    mail.send(msg)
