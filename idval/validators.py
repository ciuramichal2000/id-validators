import datetime as dt
import re
from typing import Callable, Dict, Optional

IBAN_LENGTH = {"PL": 28, "DE": 22, "GB": 22, "FR": 27, "ES": 24, "IT": 27, "NL": 18, "CZ": 24, "SK": 24,
               "AT": 20, "BE": 16, "DK": 18, "SE": 24, "IE": 22, "PT": 25, "CH": 21}


def _digits(value: Optional[str]) -> str:
    return re.sub(r"[\s-]", "", value or "")


def nip(value: str) -> bool:
    """Polish tax number: 10 digits, weighted sum modulo 11 equals the last digit (a remainder of 10 is never valid)."""
    d = _digits(value)
    if d.upper().startswith("PL"):
        d = d[2:]
    if not re.fullmatch(r"\d{10}", d):
        return False
    check = sum(int(x) * w for x, w in zip(d[:9], (6, 5, 7, 2, 3, 4, 5, 6, 7))) % 11
    return check != 10 and check == int(d[9])


def regon(value: str) -> bool:
    """Polish business registry number, 9 or 14 digits (the 14-digit form contains a valid 9-digit one)."""
    d = _digits(value)
    if re.fullmatch(r"\d{9}", d):
        return sum(int(x) * w for x, w in zip(d[:8], (8, 9, 2, 3, 4, 5, 6, 7))) % 11 % 10 == int(d[8])
    if re.fullmatch(r"\d{14}", d):
        if not regon(d[:9]):
            return False
        weights = (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8)
        return sum(int(x) * w for x, w in zip(d[:13], weights)) % 11 % 10 == int(d[13])
    return False


def pesel_birth(value: str) -> Optional[dt.date]:
    """Birth date encoded in a PESEL (the month carries the century), or None when it is not a real date."""
    d = _digits(value)
    if not re.fullmatch(r"\d{11}", d):
        return None
    yy, mm, dd = int(d[0:2]), int(d[2:4]), int(d[4:6])
    century = {0: 1900, 1: 2000, 2: 2100, 3: 2200, 4: 1800}.get(mm // 20)
    if century is None:
        return None
    try:
        return dt.date(century + yy, mm % 20, dd)
    except ValueError:
        return None


def pesel(value: str) -> bool:
    d = _digits(value)
    if not re.fullmatch(r"\d{11}", d) or pesel_birth(d) is None:
        return False
    total = sum(int(x) * w for x, w in zip(d[:10], (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)))
    return (10 - total % 10) % 10 == int(d[10])


def iban(value: str) -> bool:
    """ISO 13616: right length for the country, then the number formed by moving the first four characters to the end is 1 modulo 97."""
    v = re.sub(r"\s", "", value or "").upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", v):
        return False
    expected = IBAN_LENGTH.get(v[:2])
    if expected is not None and len(v) != expected:
        return False
    rearranged = v[4:] + v[:4]
    return int("".join(str(int(ch, 36)) for ch in rearranged)) % 97 == 1


def ean(value: str) -> bool:
    """EAN-8 / EAN-13 bar code check digit."""
    d = _digits(value)
    if len(d) not in (8, 13) or not d.isdigit():
        return False
    total = sum(int(x) * (3 if i % 2 == 0 else 1) for i, x in enumerate(reversed(d[:-1])))
    return (10 - total % 10) % 10 == int(d[-1])


KINDS: Dict[str, Callable[[str], bool]] = {"nip": nip, "regon": regon, "pesel": pesel, "iban": iban, "ean": ean}


def validate(kind: str, value: str) -> bool:
    try:
        return KINDS[kind.lower()](value)
    except KeyError:
        raise ValueError("unknown kind %r (choose from %s)" % (kind, ", ".join(sorted(KINDS))))
