"""Decides what one workflow run does: which Dart versions to build, which hashes to reuse, or stop.

Input is Flutter's releases_linux.json (the data behind docs.flutter.dev/install/archive), the ledger on main and,
when the branch auto/dart-snapshots exists, the ledger on that branch.

Usage: python3 -m tools.plan --releases FILE --ledger FILE [--branch-ledger FILE]
                             --branch-on-main true|false --pr-open true|false --out plan.json
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass

from tools.ledger import LedgerError, LedgerRow, read_ledger, version_key

MIN_FLUTTER = (3, 0)

_STABLE_VERSION = re.compile(r"\d+\.\d+\.\d+")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class ReleasesError(ValueError):
    pass


@dataclass(frozen=True)
class Release:
    version: str
    dart_version: str
    release_date: str
    archive_url: str
    sha256: str


@dataclass(frozen=True)
class Decision:
    action: str
    builds: list[Release]
    reused: list[LedgerRow]


def _text(entry: dict, key: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value:
        raise ReleasesError(f"release {entry.get('version', '?')}: '{key}' is missing or not a string")
    return value


def parse_releases(doc: object) -> list[Release]:
    """Stable releases from MIN_FLUTTER on that name their Dart SDK; the rest is dropped."""
    if not isinstance(doc, dict) or not isinstance(doc.get("base_url"), str) or not isinstance(doc.get("releases"), list):
        raise ReleasesError("releases JSON must be an object with a string base_url and a releases list")
    base_url = doc["base_url"].rstrip("/")
    # Keyed by archive URL: a release re-uploaded under the same path (Flutter 3.13.3 is listed twice) leaves only the
    # last upload there, so only the entry with the latest release_date has the sha256 of that file.
    by_archive: dict[str, tuple[str, Release]] = {}
    for entry in doc["releases"]:
        if not isinstance(entry, dict):
            raise ReleasesError("every release must be an object")
        version = _text(entry, "version")
        if _text(entry, "channel") != "stable" or not _STABLE_VERSION.fullmatch(version):
            continue
        if version_key(version)[:2] < MIN_FLUTTER:
            continue
        dart_version = entry.get("dart_sdk_version")
        if not isinstance(dart_version, str) or not dart_version.strip():
            print(f"plan: skipping Flutter {version}: no dart_sdk_version", file=sys.stderr)
            continue
        released_at = _text(entry, "release_date")
        release_date = released_at[:10]
        if not _DATE.fullmatch(release_date):
            raise ReleasesError(f"release {version}: release_date must start with YYYY-MM-DD")
        archive_url = f"{base_url}/{_text(entry, 'archive')}"
        release = Release(version, dart_version, release_date, archive_url, _text(entry, "sha256"))
        if archive_url not in by_archive or released_at > by_archive[archive_url][0]:
            by_archive[archive_url] = (released_at, release)
    return [release for _, release in by_archive.values()]


def earliest_per_dart(releases: list[Release]) -> dict[str, Release]:
    """For each raw Dart SDK string, the first Flutter release that shipped it."""
    earliest: dict[str, Release] = {}
    for r in sorted(releases, key=lambda r: (r.release_date, version_key(r.version))):
        earliest.setdefault(r.dart_version, r)
    return earliest


def decide(releases: list[Release], main_ledger: list[LedgerRow], branch_ledger: list[LedgerRow] | None,
           branch_on_main: bool, pr_open: bool) -> Decision:
    done = {r.dart_version for r in main_ledger}
    pending = sorted((r for d, r in earliest_per_dart(releases).items() if d not in done),
                     key=lambda r: (r.release_date, version_key(r.version)))
    if not pending:
        return Decision("stop", [], [])
    on_branch = {r.dart_version: r for r in branch_ledger or [] if r.hash}
    reused = [on_branch[r.dart_version] for r in pending if r.dart_version in on_branch]
    builds = [r for r in pending if r.dart_version not in on_branch]
    if not builds and branch_on_main and pr_open:
        return Decision("stop", [], [])
    return Decision("publish", builds, reused)


def _flag(value: str) -> bool:
    if value not in ("true", "false"):
        raise argparse.ArgumentTypeError("must be true or false")
    return value == "true"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m tools.plan")
    parser.add_argument("--releases", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--branch-ledger")
    parser.add_argument("--branch-on-main", type=_flag, required=True)
    parser.add_argument("--pr-open", type=_flag, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    try:
        with open(args.releases, encoding="utf-8") as f:
            releases = parse_releases(json.load(f))
        main_ledger = read_ledger(args.ledger)
        branch_ledger = read_ledger(args.branch_ledger) if args.branch_ledger else None
    except (ReleasesError, LedgerError, OSError, json.JSONDecodeError) as e:
        print(f"plan: {e}", file=sys.stderr)
        return 1

    decision = decide(releases, main_ledger, branch_ledger, args.branch_on_main, args.pr_open)
    plan = {
        "action": decision.action,
        "branch_on_main": args.branch_on_main,
        "pr_open": args.pr_open,
        "builds": [{"dart_version": r.dart_version, "flutter_version": r.version, "release_date": r.release_date,
                    "archive_url": r.archive_url, "sha256": r.sha256} for r in decision.builds],
        "reused": [{"dart_version": r.dart_version, "flutter_version": r.flutter_version,
                    "release_date": r.release_date, "hash": r.hash} for r in decision.reused],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
        f.write("\n")
    print(f"plan: {decision.action}, {len(decision.builds)} to build, {len(decision.reused)} reused")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
