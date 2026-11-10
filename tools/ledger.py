"""The Dart snapshot ledger (src/dart-snapshots.csv) and the dart-snapshot SQL that build.sh generates from it.

One row per Dart SDK version (the raw `dart_sdk_version` string of Flutter's releases_linux.json): the Flutter release
built to read its snapshot hash, that release's date, and the hash. An empty hash means the version was looked at and
deliberately skipped: it gives no SQL row and the action does not build it again.

Usage: python3 -m tools.ledger sql <ledger.csv>   prints the INSERT for version_tables, or nothing when no row has a hash
"""
import csv
import re
import sys
from dataclasses import dataclass

HEADER = ("dart_version", "flutter_version", "release_date", "hash")

_FLUTTER_VERSION = re.compile(r"\d+\.\d+\.\d+")
_RELEASE_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_HASH = re.compile(r"[0-9a-f]{32}")


class LedgerError(ValueError):
    pass


@dataclass(frozen=True)
class LedgerRow:
    dart_version: str
    flutter_version: str
    release_date: str
    hash: str


def version_key(version: str) -> tuple[int, ...]:
    """`"3.10"` -> `(3, 10)`, so versions compare as numbers (3.9 < 3.10)."""
    return tuple(int(part) for part in version.split("."))


def minor_of(flutter_version: str) -> str:
    """`"3.47.8"` -> `"3.47"`, the value a dart-snapshot row holds."""
    return ".".join(flutter_version.split(".")[:2])


def _check_row(fields: list[str], line: int) -> LedgerRow:
    if len(fields) != len(HEADER):
        raise LedgerError(f"line {line}: expected {len(HEADER)} fields, found {len(fields)}")
    dart_version, flutter_version, release_date, snapshot_hash = fields
    if not dart_version.strip():
        raise LedgerError(f"line {line}: dart_version is empty")
    if not _FLUTTER_VERSION.fullmatch(flutter_version):
        raise LedgerError(f"line {line}: flutter_version must be M.m.p, found '{flutter_version}'")
    if not _RELEASE_DATE.fullmatch(release_date):
        raise LedgerError(f"line {line}: release_date must be YYYY-MM-DD, found '{release_date}'")
    if snapshot_hash and not _HASH.fullmatch(snapshot_hash):
        raise LedgerError(f"line {line}: hash must be 32 characters [0-9a-f] or empty, found '{snapshot_hash}'")
    return LedgerRow(dart_version, flutter_version, release_date, snapshot_hash)


def read_ledger(path: str) -> list[LedgerRow]:
    with open(path, encoding="utf-8", newline="") as f:
        records = list(csv.reader(f))
    if not records or tuple(records[0]) != HEADER:
        raise LedgerError(f"line 1: header must be {','.join(HEADER)}")
    rows: list[LedgerRow] = []
    seen: set[str] = set()
    for line, fields in enumerate(records[1:], start=2):
        ledger_row = _check_row(fields, line)
        if ledger_row.dart_version in seen:
            raise LedgerError(f"line {line}: dart_version '{ledger_row.dart_version}' appears twice")
        seen.add(ledger_row.dart_version)
        rows.append(ledger_row)
    return rows


def write_ledger(path: str, rows: list[LedgerRow]) -> None:
    ordered = sorted(rows, key=lambda r: (r.release_date, r.dart_version))
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(HEADER)
        for r in ordered:
            writer.writerow((r.dart_version, r.flutter_version, r.release_date, r.hash))


def to_sql(rows: list[LedgerRow]) -> str:
    """The dart-snapshot INSERT: one row per distinct hash, valued with the Flutter minor that built it."""
    minors: dict[str, str] = {}
    for r in rows:
        if not r.hash:
            continue
        minor = minor_of(r.flutter_version)
        known = minors.setdefault(r.hash, minor)
        if known != minor:
            first, second = sorted((known, minor), key=version_key)
            raise LedgerError(f"dart-snapshot hash {r.hash} maps to {first} and {second}")
    if not minors:
        return ""
    ordered = sorted(minors.items(), key=lambda item: (version_key(item[1]), item[0]))
    values = ",\n".join(f"  ('dart-snapshot', '{h}', '{minor}')" for h, minor in ordered)
    return f"INSERT INTO version_tables (table_name, key, value) VALUES\n{values};\n"


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "sql":
        print("usage: python3 -m tools.ledger sql <ledger.csv>", file=sys.stderr)
        return 2
    try:
        sys.stdout.write(to_sql(read_ledger(argv[1])))
    except (LedgerError, OSError) as e:
        print(f"ledger: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
