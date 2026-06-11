from pathlib import Path
from typing import Tuple

import pandas as pd

from src.validator import validate_columns, validate_recipient


def load_recipients(uploaded_file) -> Tuple[pd.DataFrame, list]:
    """Load recipients from CSV or Excel and validate rows."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")

    df.columns = [str(col).strip().lower() for col in df.columns]
    is_valid, missing_columns = validate_columns(list(df.columns))
    if not is_valid:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df = df.fillna("")
    statuses = []
    errors = []

    for _, row in df.iterrows():
        valid, message = validate_recipient(row.to_dict())
        statuses.append("pending" if valid else "failed")
        errors.append("" if valid else message)

    df["status"] = statuses
    df["error"] = errors
    return df, missing_columns


def load_sample_recipients() -> pd.DataFrame:
    sample_path = Path("data/sample_recipients.csv")
    return pd.read_csv(sample_path)
