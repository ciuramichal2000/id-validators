import datetime as dt
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from idval import ean, iban, nip, pesel, pesel_birth, regon, validate  # noqa: E402
from idval.__main__ import main  # noqa: E402


def test_nip_accepts_real_checksum_and_formatting():
    assert nip("5260250274") and nip("526-025-02-74") and nip("PL 526 025 02 74")


def test_nip_rejects_wrong_digit_length_letters_and_remainder_ten():
    assert not nip("5260250275")          # last digit changed
    assert not nip("526025027")           # too short
    assert not nip("52602502AB")
    # a body whose weighted sum is 10 modulo 11 has no valid check digit at all
    body = next(str(b) for b in range(123456780, 123457000)
                if sum(int(x) * w for x, w in zip(str(b), (6, 5, 7, 2, 3, 4, 5, 6, 7))) % 11 == 10)
    assert not any(nip(body + str(c)) for c in range(10))


def test_regon_nine_and_fourteen_digits():
    assert regon("123456785")
    assert not regon("123456784")
    assert regon("12345678512347") and not regon("12345678512340")
    assert not regon("12345678412347")        # the embedded 9-digit number is wrong


def test_pesel_checksum_and_birth_date_with_century():
    assert pesel("44051401359") and pesel_birth("44051401359") == dt.date(1944, 5, 14)
    assert not pesel("44051401358")
    assert pesel_birth("02271409862") == dt.date(2002, 7, 14)      # month 27 = July 2000s
    assert pesel_birth("44131401359") is None                       # month 13 is not a real month


def test_iban_known_examples_and_length_rule():
    assert iban("PL61109010140000071219812874") and iban("PL61 1090 1014 0000 0712 1981 2874")
    assert iban("DE89370400440532013000") and iban("GB82WEST12345698765432")
    assert not iban("PL61109010140000071219812875")                # one digit changed
    assert not iban("PL6110901014000007121981287")                 # wrong length for PL
    assert not iban("")


def test_ean_check_digit():
    assert ean("4006381333931") and ean("96385074")
    assert not ean("4006381333932") and not ean("12345")


def test_validate_dispatch_and_unknown_kind():
    assert validate("NIP", "5260250274")
    with pytest.raises(ValueError):
        validate("passport", "x")


def test_cli_single_value_and_csv(tmp_path, capsys):
    assert main(["nip", "5260250274"]) == 0
    assert main(["iban", "PL00"]) == 1
    f = tmp_path / "c.csv"
    f.write_text("name,nip\nA,5260250274\nB,5260250275\n", encoding="utf-8")
    assert main(["--csv", str(f), "--column", "nip", "--kind", "nip"]) == 1
    assert "line 3" in capsys.readouterr().out
