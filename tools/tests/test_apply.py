import contextlib
import io
import json
import os
import tempfile
import unittest

from tools.apply import Added, BuildResult, Conflict, main, merge, pr_body, pr_title, read_results
from tools.ledger import LedgerRow, read_ledger, write_ledger
from tools.tests.test_meta import SAMPLE

SEED = [
    LedgerRow("3.6.2", "3.27.4", "2025-02-05", "f956f595844a2f845a55707faaaa51e4"),
    LedgerRow("3.7.2", "3.29.3", "2025-04-14", "d91c0e6f35f0eb2e44124e8f42aa44a7"),
    LedgerRow("3.8.1", "3.32.8", "2025-07-25", "830f4f59e7969c70b595182826435c19"),
]
C = "c" * 32
D = "d" * 32
NOW = "2026-11-10T03:30:00Z"
TABLE_HEADER = "| Flutter | Dart | Release | Hash | Trong bảng |"


def ok(dart, flutter, date, h):
    return BuildResult(dart, flutter, date, "ok", h, None)


def failed(dart, flutter, date, error="flutter build apk failed"):
    return BuildResult(dart, flutter, date, "failed", None, error)


def build(dart, flutter, date):
    return {"dart_version": dart, "flutter_version": flutter, "release_date": date,
            "archive_url": f"https://example.invalid/flutter_linux_{flutter}-stable.tar.xz", "sha256": "0" * 64}


class MergeTest(unittest.TestCase):
    def test_merge_adds_new_hash_as_new_sql_row(self):
        outcome = merge(SEED, [], [ok("3.13.7", "3.47.8", "2026-10-23", C)])
        row = LedgerRow("3.13.7", "3.47.8", "2026-10-23", C)
        self.assertEqual([Added(row, True)], outcome.added)
        self.assertEqual(SEED + [row], outcome.ledger)

    def test_merge_same_hash_same_minor_is_not_new_sql_row(self):
        main_ledger = SEED + [LedgerRow("3.13.5", "3.47.6", "2026-10-01", C)]
        outcome = merge(main_ledger, [], [ok("3.13.7", "3.47.8", "2026-10-23", C)])
        self.assertEqual([Added(LedgerRow("3.13.7", "3.47.8", "2026-10-23", C), False)], outcome.added)

    def test_merge_conflict_is_not_added(self):
        main_ledger = SEED + [LedgerRow("3.12.2", "3.44.2", "2026-06-11", C)]
        outcome = merge(main_ledger, [], [ok("3.13.7", "3.47.8", "2026-10-23", C)])
        self.assertEqual([Conflict(LedgerRow("3.13.7", "3.47.8", "2026-10-23", C), "3.44")], outcome.conflicts)
        self.assertEqual([], outcome.added)
        self.assertEqual(main_ledger, outcome.ledger)

    def test_merge_conflict_between_two_new_results(self):
        outcome = merge(SEED, [], [ok("3.12.2", "3.44.2", "2026-06-11", D), ok("3.13.7", "3.47.8", "2026-10-23", D)])
        self.assertEqual([Added(LedgerRow("3.12.2", "3.44.2", "2026-06-11", D), True)], outcome.added)
        self.assertEqual([Conflict(LedgerRow("3.13.7", "3.47.8", "2026-10-23", D), "3.44")], outcome.conflicts)

    def test_merge_keeps_reused_rows(self):
        reused = LedgerRow("3.13.5", "3.47.6", "2026-10-01", D)
        outcome = merge(SEED, [reused], [ok("3.13.7", "3.47.8", "2026-10-23", C)])
        self.assertEqual([Added(reused, True), Added(LedgerRow("3.13.7", "3.47.8", "2026-10-23", C), True)],
                         outcome.added)

    def test_merge_sorts_ledger(self):
        outcome = merge(SEED, [], [ok("3.13.7", "3.47.8", "2026-10-23", C), ok("3.6.0", "3.27.0", "2024-12-11", D)])
        self.assertEqual(["3.6.0", "3.6.2", "3.7.2", "3.8.1", "3.13.7"], [r.dart_version for r in outcome.ledger])

    def test_merge_reports_failed(self):
        bad = failed("3.13.5", "3.47.6", "2026-10-01")
        outcome = merge(SEED, [], [bad])
        self.assertEqual([bad], outcome.failed)
        self.assertEqual([], outcome.added)


class ResultsTest(unittest.TestCase):
    def test_missing_result_counts_as_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "0.json"), "w", encoding="utf-8") as f:
                json.dump({"dart_version": "3.13.7", "flutter_version": "3.47.8", "release_date": "2026-10-23",
                           "status": "ok", "hash": C}, f)
            results = read_results(tmp, [build("3.13.7", "3.47.8", "2026-10-23"),
                                         build("3.13.5", "3.47.6", "2026-10-01")])
        self.assertEqual([ok("3.13.7", "3.47.8", "2026-10-23", C),
                          failed("3.13.5", "3.47.6", "2026-10-01", "no result from build job")], results)

    def test_missing_results_dir_fails_every_build(self):
        results = read_results("/nonexistent/results", [build("3.13.7", "3.47.8", "2026-10-23")])
        self.assertEqual([failed("3.13.7", "3.47.8", "2026-10-23", "no result from build job")], results)

    def test_ok_result_with_bad_hash_is_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "0.json"), "w", encoding="utf-8") as f:
                json.dump({"dart_version": "3.13.7", "flutter_version": "3.47.8", "release_date": "2026-10-23",
                           "status": "ok", "hash": "XYZ"}, f)
            results = read_results(tmp, [build("3.13.7", "3.47.8", "2026-10-23")])
        self.assertEqual("failed", results[0].status)
        self.assertIn("XYZ", results[0].error)


class TextTest(unittest.TestCase):
    def test_pr_title_lists_minors_numerically(self):
        outcome = merge([], [], [ok("3.1.0", "3.10.0", "2026-01-02", C), ok("3.0.0", "3.9.0", "2026-01-01", D),
                                 ok("3.0.1", "3.9.1", "2026-01-03", D)])
        self.assertEqual("Rules v4: Dart snapshot hashes for Flutter 3.9, 3.10", pr_title(outcome, 4))

    def test_pr_body_table(self):
        main_ledger = SEED + [LedgerRow("3.13.5", "3.47.6", "2026-10-01", D)]
        outcome = merge(main_ledger, [], [ok("3.13.7", "3.47.8", "2026-10-23", D),
                                          ok("3.12.2", "3.44.2", "2026-06-11", C)])
        body = pr_body(outcome)
        self.assertIn(TABLE_HEADER, body.splitlines())
        self.assertIn(f"| 3.44.2 | 3.12.2 | 2026-06-11 | `{C}` | dòng mới `3.44` |", body.splitlines())
        self.assertIn(f"| 3.47.8 | 3.13.7 | 2026-10-23 | `{D}` | trùng hash đã có của `3.47` |", body.splitlines())
        self.assertNotIn("## Lỗi / xung đột", body)

    def test_pr_body_lists_failures_and_conflicts(self):
        main_ledger = SEED + [LedgerRow("3.12.2", "3.44.2", "2026-06-11", C)]
        outcome = merge(main_ledger, [], [ok("3.13.7", "3.47.8", "2026-10-23", C),
                                          failed("3.13.5", "3.47.6", "2026-10-01", "flutter build apk failed")])
        body = pr_body(outcome)
        self.assertIn("## Lỗi / xung đột", body)
        self.assertIn("3.47.6", body)
        self.assertIn("flutter build apk failed", body)
        self.assertIn("3.44", body)


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.ledger = self.path("ledger.csv")
        self.rules = self.path("rules.sql")
        self.results = self.path("results")
        os.mkdir(self.results)
        write_ledger(self.ledger, SEED)
        with open(self.rules, "w", encoding="utf-8") as f:
            f.write(SAMPLE)

    def tearDown(self):
        self._tmp.cleanup()

    def path(self, name):
        return os.path.join(self.dir, name)

    def write_json(self, name, value):
        with open(self.path(name), "w", encoding="utf-8") as f:
            json.dump(value, f)

    def read_bytes(self, path):
        with open(path, "rb") as f:
            return f.read()

    def run_cli(self, builds, reused=(), branch=None, on_main=False, pr_open=False):
        self.write_json("plan.json", {"action": "publish", "branch_on_main": on_main, "pr_open": pr_open,
                                      "builds": builds, "reused": list(reused)})
        argv = ["--plan", self.path("plan.json"), "--results", self.results, "--ledger", self.ledger,
                "--rules", self.rules, "--now", NOW, "--out-title", self.path("title.txt"),
                "--out-body", self.path("body.md"), "--out-status", self.path("status.json")]
        if branch is not None:
            write_ledger(self.path("branch.csv"), branch)
            argv += ["--branch-ledger", self.path("branch.csv")]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, main(argv))
        with open(self.path("status.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_cli_mixed_ok_and_failed_publishes_ok_ones(self):
        self.write_json("results/0.json", {"dart_version": "3.13.7", "flutter_version": "3.47.8",
                                           "release_date": "2026-10-23", "status": "ok", "hash": C})
        self.write_json("results/1.json", {"dart_version": "3.13.5", "flutter_version": "3.47.6",
                                           "release_date": "2026-10-01", "status": "failed",
                                           "error": "flutter build apk failed"})
        status = self.run_cli([build("3.13.7", "3.47.8", "2026-10-23"), build("3.13.5", "3.47.6", "2026-10-01")])
        self.assertEqual({"changed": True, "has_errors": True, "version": 4}, status)
        self.assertIn(LedgerRow("3.13.7", "3.47.8", "2026-10-23", C), read_ledger(self.ledger))
        with open(self.rules, encoding="utf-8") as f:
            rules = f.read()
        self.assertIn("('version', '4')", rules)
        self.assertIn(f"('published_at', '{NOW}')", rules)
        with open(self.path("title.txt"), encoding="utf-8") as f:
            self.assertEqual("Rules v4: Dart snapshot hashes for Flutter 3.47", f.read().strip())
        with open(self.path("body.md"), encoding="utf-8") as f:
            self.assertIn("flutter build apk failed", f.read())

    def test_cli_all_failed_changes_nothing(self):
        before = (self.read_bytes(self.ledger), self.read_bytes(self.rules))
        self.write_json("results/0.json", {"dart_version": "3.13.7", "flutter_version": "3.47.8",
                                           "release_date": "2026-10-23", "status": "failed", "error": "boom"})
        status = self.run_cli([build("3.13.7", "3.47.8", "2026-10-23"), build("3.13.5", "3.47.6", "2026-10-01")])
        self.assertEqual({"changed": False, "has_errors": True, "version": 4}, status)
        self.assertEqual(before, (self.read_bytes(self.ledger), self.read_bytes(self.rules)))

    def test_cli_same_as_open_branch_changes_nothing(self):
        before = (self.read_bytes(self.ledger), self.read_bytes(self.rules))
        reused = LedgerRow("3.13.7", "3.47.8", "2026-10-23", C)
        self.write_json("results/0.json", {"dart_version": "3.13.5", "flutter_version": "3.47.6",
                                           "release_date": "2026-10-01", "status": "failed", "error": "boom"})
        status = self.run_cli([build("3.13.5", "3.47.6", "2026-10-01")],
                              reused=[{"dart_version": reused.dart_version, "flutter_version": reused.flutter_version,
                                       "release_date": reused.release_date, "hash": reused.hash}],
                              branch=SEED + [reused], on_main=True, pr_open=True)
        self.assertEqual({"changed": False, "has_errors": True, "version": 4}, status)
        self.assertEqual(before, (self.read_bytes(self.ledger), self.read_bytes(self.rules)))


if __name__ == "__main__":
    unittest.main()
