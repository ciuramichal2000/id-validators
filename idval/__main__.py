"""python -m idval nip 526-025-02-74     |     python -m idval --csv file.csv --column nip --kind nip"""
import argparse
import csv
import sys

from .validators import KINDS, validate


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="idval")
    p.add_argument("kind", nargs="?", choices=sorted(KINDS))
    p.add_argument("value", nargs="?")
    p.add_argument("--csv")
    p.add_argument("--column")
    p.add_argument("--kind", dest="csv_kind", choices=sorted(KINDS))
    a = p.parse_args(argv)
    if a.csv:
        bad = 0
        with open(a.csv, newline="", encoding="utf-8-sig") as f:
            for n, row in enumerate(csv.DictReader(f), start=2):
                if not validate(a.csv_kind, row.get(a.column, "")):
                    bad += 1
                    print("line %d: %r is not a valid %s" % (n, row.get(a.column, ""), a.csv_kind))
        print("%d invalid" % bad)
        return 1 if bad else 0
    ok = validate(a.kind, a.value or "")
    print("valid" if ok else "invalid")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
