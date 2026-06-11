import re
from typing import Dict, List, Tuple

REQUIRED_COLUMNS = ["first_name", "last_name", "company_name", "email"]
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_columns(columns: List[str]) -> Tuple[bool, List[str]]:
    """Check whether all required columns are present."""
    normalized_columns = [str(col).strip().lower() for col in columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in normalized_columns]
    return len(missing) == 0, missing


def is_valid_email(email: str) -> bool:
    """Validate a basic email format."""
    if not isinstance(email, str):
        return False
    email = email.strip()
    return bool(EMAIL_PATTERN.match(email))


def validate_recipient(row: Dict[str, str]) -> Tuple[bool, str]:
    """Validate one recipient row."""
    for col in REQUIRED_COLUMNS:
        value = row.get(col, "")
        if value is None or str(value).strip() == "":
            return False, f"Missing required field: {col}"

    if not is_valid_email(str(row.get("email", ""))):
        return False, "Invalid email address"

    return True, "Valid"
