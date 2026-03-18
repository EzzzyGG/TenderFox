from __future__ import annotations

import re

# Minimal E.164 normalization with CIS focus.
# NOTE: This is a first MVP version. It does not guarantee validity, only normalization.


_CIS_PREFIXES = (
    "+7",   # RU/KZ
    "+375", # BY
    "+380", # UA
    "+374", # AM
    "+994", # AZ
    "+995", # GE
    "+996", # KG
    "+998", # UZ
    "+992", # TJ
    "+993", # TM
    "+373", # MD
)


def normalize_phone_to_e164(raw: str) -> str:
    if not raw or not raw.strip():
        raise ValueError("phone is empty")

    s = raw.strip()

    # Keep +, digits only.
    s = re.sub(r"[^\d+]", "", s)

    # Convert leading 8 (RU local) to +7
    if s.startswith("8") and len(re.sub(r"\D", "", s)) == 11:
        s = "+7" + s[1:]

    # If starts with 7 and length 11 digits, assume RU/KZ
    digits = re.sub(r"\D", "", s)
    if s.startswith("7") and len(digits) == 11:
        s = "+" + digits

    if not s.startswith("+"):
        # As MVP default: assume RU/KZ if 11 digits
        if len(digits) == 11 and digits.startswith("7"):
            s = "+" + digits
        else:
            raise ValueError("phone must include country code (E.164) or be RU 8XXXXXXXXXX")

    # Final sanity: must be + and 10-15 digits.
    digits = re.sub(r"\D", "", s)
    if len(digits) < 10 or len(digits) > 15:
        raise ValueError("phone length is invalid")

    # Basic CIS check (optional, but helpful)
    if not any(s.startswith(p) for p in _CIS_PREFIXES):
        # Allow non-CIS too, but keep normalized
        return "+" + digits

    return "+" + digits
