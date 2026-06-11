import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

DB_PATH = Path("database/email_automation.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                created_at TEXT NOT NULL,
                total INTEGER DEFAULT 0,
                sent INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                company_name TEXT,
                email TEXT,
                status TEXT,
                error TEXT,
                sent_at TEXT,
                FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
            )
            """
        )
        conn.commit()


def create_campaign(name: str, subject: str, total: int) -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO campaigns (name, subject, created_at, total, sent, failed) VALUES (?, ?, ?, ?, 0, 0)",
            (name, subject, now, total),
        )
        conn.commit()
        return int(cursor.lastrowid)


def log_email(
    campaign_id: int,
    first_name: str,
    last_name: str,
    company_name: str,
    email: str,
    status: str,
    error: str = "",
) -> None:
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "sent" else ""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO email_logs
            (campaign_id, first_name, last_name, company_name, email, status, error, sent_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (campaign_id, first_name, last_name, company_name, email, status, error, sent_at),
        )
        conn.commit()


def update_campaign_stats(campaign_id: int) -> None:
    with get_connection() as conn:
        logs = pd.read_sql_query(
            "SELECT status FROM email_logs WHERE campaign_id = ?",
            conn,
            params=(campaign_id,),
        )
        sent = int((logs["status"] == "sent").sum()) if not logs.empty else 0
        failed = int((logs["status"] == "failed").sum()) if not logs.empty else 0
        total = int(len(logs))
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE campaigns SET total = ?, sent = ?, failed = ? WHERE id = ?",
            (total, sent, failed, campaign_id),
        )
        conn.commit()


def get_campaigns() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT id, name, subject, created_at, total, sent, failed FROM campaigns ORDER BY id DESC",
            conn,
        )


def get_email_logs(campaign_id: Optional[int] = None) -> pd.DataFrame:
    with get_connection() as conn:
        if campaign_id:
            return pd.read_sql_query(
                "SELECT first_name, last_name, company_name, email, status, error, sent_at FROM email_logs WHERE campaign_id = ?",
                conn,
                params=(campaign_id,),
            )
        return pd.read_sql_query(
            "SELECT campaign_id, first_name, last_name, company_name, email, status, error, sent_at FROM email_logs ORDER BY id DESC",
            conn,
        )
