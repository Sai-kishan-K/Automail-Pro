import os
from typing import Dict

from dotenv import load_dotenv


def load_smtp_config() -> Dict[str, str]:
    load_dotenv()
    return {
        "smtp_server": os.getenv("SMTP_SERVER", ""),
        "smtp_port": os.getenv("SMTP_PORT", "587"),
        "email_address": os.getenv("EMAIL_ADDRESS", ""),
        "email_password": os.getenv("EMAIL_PASSWORD", ""),
        "sender_name": os.getenv("SENDER_NAME", "AutoMail Pro"),
    }


def mask_email_password(password: str) -> str:
    if not password:
        return "Not configured"
    return "*" * min(len(password), 8)
