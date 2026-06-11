import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple


def send_email(
    smtp_server: str,
    smtp_port: int,
    email_address: str,
    email_password: str,
    sender_name: str,
    recipient_email: str,
    subject: str,
    body: str,
) -> Tuple[bool, str]:
    """Send a single email through SMTP."""
    try:
        message = MIMEMultipart()
        message["From"] = f"{sender_name} <{email_address}>" if sender_name else email_address
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(smtp_server, int(smtp_port), timeout=30) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(message)

        return True, "Email sent successfully"
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check email/app password."
    except smtplib.SMTPRecipientsRefused:
        return False, "Recipient email was refused by SMTP server."
    except smtplib.SMTPException as exc:
        return False, f"SMTP error: {exc}"
    except Exception as exc:
        return False, f"Unexpected error: {exc}"
