import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

sender = os.getenv("MAIL_USERNAME")
password = os.getenv("MAIL_PASSWORD")
receiver = os.getenv("MAIL_DEFAULT_RECIPIENT", sender)
smtp_server = os.getenv("MAIL_SERVER", "smtpout.secureserver.net")
smtp_port = int(os.getenv("MAIL_PORT", 587))

# Формируем сообщение
msg = MIMEText("This is a test message sent via SMTP using Python.")
msg["Subject"] = "SMTP Test"
msg["From"] = sender
msg["To"] = receiver

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()
    print("Test email sent successfully!")

except smtplib.SMTPAuthenticationError as e:
    print("Authentication error:", e)
except Exception as e:
    print("An error occurred:", e)
