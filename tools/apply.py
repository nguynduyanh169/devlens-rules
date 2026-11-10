"""Merges the build results of one run into the ledger, bumps meta and writes the PR title and body.

Usage: python3 -m tools.apply --plan plan.json --results DIR --ledger src/dart-snapshots.csv [--branch-ledger FILE]
                              --rules src/rules.sql --now YYYY-MM-DDTHH:MM:SSZ
                              --out-title FILE --out-body FILE --out-status FILE
status.json is {"changed": bool, "has_errors": bool, "version": int}. The ledger and rules.sql are rewritten only when
changed; the workflow then runs build.sh and updates the PR, and fails the run at the end when has_errors.
"""
import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass

from tools.ledger import LedgerError, LedgerRow, minor_of, read_ledger, version_key, write_ledger
from tools.meta import MetaError, bump_meta, read_version

_HASH = re.compile(r"[0-9a-f]{32}")
NO_RESULT = "no result from build job"


@dataclass(frozen=True)
class BuildResult:
    dart_version: str
    flutter_version: str
    release_date: str
    status: str
    hash: str | None
    error: str | None


@dataclass(frozen=True)
class Added:
    row: LedgerRow
    new_sql_row: bool


@dataclass(frozen=True)
class Conflict:
    row: LedgerRow
    other_minor: str


@dataclass(frozen=True)
class Outcome:
    ledger: list[LedgerRow]
    added: list[Added]
    failed: list[BuildResult]
    conflicts: list[Conflict]


def _result(value: dict) -> BuildResult:
    dart, flutter, date = value["dart_version"], value["flutter_version"], value["release_date"]
    if value.get("status") == "ok":
        snapshot_hash = value.get("hash")
        if isinstance(snapshot_hash, str) and _HASH.fullmatch(snapshot_hash):
            return BuildResult(dart, flutter, date, "ok", snapshot_hash, None)
        return BuildResult(dart, flutter, date, "failed", None, f"invalid hash in result: {snapshot_hash!r}")
    return BuildResult(dart, flutter, date, "failed", None, str(value.get("error") or "build failed"))


def read_results(results_dir: str, builds: list[dict]) -> list[BuildResult]:
    """One result per planned build, in plan order; a build whose job left no result file counts as failed."""
    by_dart: dict[str, BuildResult] = {}
    for path in sorted(glob.glob(os.path.join(results_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            r = _result(json.load(f))
        by_dart[r.dart_version] = r
    return [by_dart.get(b["dart_version"]) or
            BuildResult(b["dart_version"], b["flutter_version"], b["release_date"], "failed", None, NO_RESULT)
            for b in builds]


def merge(main_ledger: list[LedgerRow], reused: list[LedgerRow], results: list[BuildResult]) -> Outcome:
    minors = {r.hash: minor_of(r.flutter_version) for r in main_ledger if r.hash}
    candidates = list(reused) + [LedgerRow(r.dart_version, r.flutter_version, r.release_date, r.hash)
                                 for r in results if r.status == "ok"]
    added: list[Added] = []
    conflicts: list[Conflict] = []
    for row in candidates:
        minor = minor_of(row.flutter_version)
        known = minors.get(row.hash)
        if known is not None and known != minor:
            conflicts.append(Conflict(row, known))
            continue
        minors[row.hash] = minor
        added.append(Added(row, known is None))
    ledger = sorted(main_ledger + [a.row for a in added], key=lambda r: (r.release_date, r.dart_version))
    return Outcome(ledger, added, [r for r in results if r.status != "ok"], conflicts)


def pr_title(outcome: Outcome, version: int) -> str:
    minors = sorted({minor_of(a.row.flutter_version) for a in outcome.added}, key=version_key)
    return f"Rules v{version}: Dart snapshot hashes for Flutter {', '.join(minors)}"


def pr_body(outcome: Outcome) -> str:
    lines = [
        "Hash Dart snapshot mới, đọc từ `lib/arm64-v8a/libapp.so` của một app hello-world build bằng đúng bản Flutter đó.",
        "Merge PR này là publish rules cho app.",
        "",
        "| Flutter | Dart | Release | Hash | Trong bảng |",
        "|---|---|---|---|---|",
    ]
    for a in outcome.added:
        minor = minor_of(a.row.flutter_version)
        where = f"dòng mới `{minor}`" if a.new_sql_row else f"trùng hash đã có của `{minor}`"
        lines.append(f"| {a.row.flutter_version} | {a.row.dart_version} | {a.row.release_date} | `{a.row.hash}` | {where} |")
    if outcome.failed or outcome.conflicts:
        lines += ["", "## Lỗi / xung đột", ""]
        for r in outcome.failed:
            lines.append(f"- Flutter {r.flutter_version} (Dart {r.dart_version}): build lỗi: {r.error}")
        for c in outcome.conflicts:
            lines.append(f"- Flutter {c.row.flutter_version} (Dart {c.row.dart_version}): hash `{c.row.hash}` "
                         f"đã thuộc `{c.other_minor}`, không ghi vào ledger")
    return "\n".join(lines) + "\n"


def _row(value: dict) -> LedgerRow:
    return LedgerRow(value["dart_version"], value["flutter_version"], value["release_date"], value["hash"])


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m tools.apply")
    for name in ("--plan", "--results", "--ledger", "--rules", "--now", "--out-title", "--out-body", "--out-status"):
        parser.add_argument(name, required=True)
    parser.add_argument("--branch-ledger")
    args = parser.parse_args(argv)

    try:
        with open(args.plan, encoding="utf-8") as f:
            plan = json.load(f)
        results = read_results(args.results, plan["builds"])
        main_ledger = read_ledger(args.ledger)
        branch_ledger = read_ledger(args.branch_ledger) if args.branch_ledger else None
        with open(args.rules, encoding="utf-8") as f:
            rules_sql = f.read()
        version = read_version(rules_sql) + 1
        outcome = merge(main_ledger, [_row(r) for r in plan["reused"]], results)
        same_as_open_branch = (branch_ledger is not None and plan["branch_on_main"] and plan["pr_open"]
                               and outcome.ledger == sorted(branch_ledger, key=lambda r: (r.release_date, r.dart_version)))
        changed = bool(outcome.added) and not same_as_open_branch
        if changed:
            new_rules = bump_meta(rules_sql, version, args.now)
            write_ledger(args.ledger, outcome.ledger)
            with open(args.rules, "w", encoding="utf-8") as f:
                f.write(new_rules)
    except (LedgerError, MetaError, OSError, KeyError, TypeError, json.JSONDecodeError) as e:
        print(f"apply: {e}", file=sys.stderr)
        return 1

    with open(args.out_title, "w", encoding="utf-8") as f:
        f.write(pr_title(outcome, version) + "\n")
    with open(args.out_body, "w", encoding="utf-8") as f:
        f.write(pr_body(outcome))
    status = {"changed": changed, "has_errors": bool(outcome.failed or outcome.conflicts), "version": version}
    with open(args.out_status, "w", encoding="utf-8") as f:
        json.dump(status, f)
        f.write("\n")
    print(f"apply: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
