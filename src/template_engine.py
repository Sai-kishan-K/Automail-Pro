from typing import Dict


def personalize_text(template: str, recipient: Dict[str, str]) -> str:
    """Replace placeholders like {first_name} with recipient values."""
    result = template
    for key, value in recipient.items():
        placeholder = "{" + str(key) + "}"
        result = result.replace(placeholder, str(value))
    return result


def find_placeholders(template: str) -> list:
    """Find unique placeholders in a template string."""
    placeholders = []
    start = 0
    while True:
        open_idx = template.find("{", start)
        close_idx = template.find("}", open_idx + 1)
        if open_idx == -1 or close_idx == -1:
            break
        placeholder = template[open_idx + 1:close_idx].strip()
        if placeholder and placeholder not in placeholders:
            placeholders.append(placeholder)
        start = close_idx + 1
    return placeholders
