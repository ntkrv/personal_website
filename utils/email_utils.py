from flask_mail import Message
from extensions import mail
import os


def send_contact_email(name, email, message):
    recipient = os.getenv("MAIL_DEFAULT_RECIPIENT", os.getenv("MAIL_USERNAME"))
    msg = Message(
        subject=f"New Contact Message from {name}",
        recipients=[recipient],
        body=f"From: {name} <{email}>\n\n{message}",
    )
    mail.send(msg)
