# src/security.py
from __future__ import annotations
import re
from typing import Dict, List

CANARY_PATTERNS: List[str] = [
    r"blue-cat-42",
    r"PII_CANARY",
    r"PHONE-FAKE-",
    r"RRN-FAKE-",
    r"BANK-FAKE-",
    r"INTERNAL_SECRET",
]

_canary_re = re.compile("|".join(CANARY_PATTERNS), re.IGNORECASE)

def leak_detect(text: str) -> bool:
    if text is None:
        return False
    return _canary_re.search(text) is not None
