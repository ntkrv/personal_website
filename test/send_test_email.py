import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True") == "True",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "False") == "True",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
)

mail = Mail(app)

with app.app_context():
    msg = Message(
        subject="Test Email",
        recipients=[os.getenv("MAIL_USERNAME")],
        body="✅ This is a test email. If you received it, SMTP is working.",
    )
    mail.send(msg)
    print("📬 Test email sent successfully.")
