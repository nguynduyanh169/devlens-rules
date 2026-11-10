import contextlib
import io
import json
import os
import tempfile
import unittest

from tools.ledger import LedgerRow, write_ledger
from tools.plan import Decision, ReleasesError, decide, earliest_per_dart, main, parse_releases

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "releases_sample.json")
SEED = [
    LedgerRow("3.6.2", "3.27.4", "2025-02-05", "f956f595844a2f845a55707faaaa51e4"),
    LedgerRow("3.7.2", "3.29.3", "2025-04-14", "d91c0e6f35f0eb2e44124e8f42aa44a7"),
    LedgerRow("3.8.1", "3.32.8", "2025-07-25", "830f4f59e7969c70b595182826435c19"),
]
BUILD_BETA = "3.10.0 (build 3.10.0-290.4.beta)"
ROW_3_10_BETA = LedgerRow(BUILD_BETA, "3.38.0", "2025-11-12", "a" * 32)
ROW_3_10 = LedgerRow("3.10.0", "3.38.1", "2025-11-13", "b" * 32)
ROW_3_13_7 = LedgerRow("3.13.7", "3.47.8", "2026-10-23", "c" * 32)
ROW_3_5_4 = LedgerRow("3.5.4", "3.24.5", "2024-11-13", "e" * 32)
ALL_PENDING = [ROW_3_5_4, ROW_3_10_BETA, ROW_3_10, ROW_3_13_7]


def load_doc():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)


def releases():
    with contextlib.redirect_stderr(io.StringIO()):
        return parse_releases(load_doc())


class ParseTest(unittest.TestCase):
    def test_keeps_stable_from_3_0(self):
        self.assertEqual({"3.47.9", "3.47.8", "3.38.0", "3.38.1", "3.27.4", "3.24.5"}, {r.version for r in releases()})

    def test_skips_release_without_dart_version(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            parse_releases(load_doc())
        self.assertIn("3.41.0", err.getvalue())

    def test_archive_url_joins_base_url(self):
        r = next(r for r in releases() if r.version == "3.47.8")
        self.assertEqual("https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/"
                         "flutter_linux_3.47.8-stable.tar.xz", r.archive_url)
        self.assertEqual("2026-10-23", r.release_date)
        self.assertEqual("3.13.7", r.dart_version)

    def test_rejects_malformed_document(self):
        doc = load_doc()
        del doc["releases"][0]["version"]
        for bad in ({}, {"base_url": "x", "releases": "nope"}, doc):
            with self.subTest(bad=str(bad)[:40]):
                with self.assertRaises(ReleasesError):
                    parse_releases(bad)

    def test_earliest_release_wins_regardless_of_order(self):
        by_dart = earliest_per_dart(releases())
        self.assertEqual("3.47.8", by_dart["3.13.7"].version)
        self.assertEqual("3.38.0", by_dart[BUILD_BETA].version)
        self.assertEqual("3.38.1", by_dart["3.10.0"].version)


class DecideTest(unittest.TestCase):
    def decide(self, main_ledger=SEED, branch=None, on_main=False, pr_open=False) -> Decision:
        return decide(releases(), main_ledger, branch, on_main, pr_open)

    def test_pending_without_branch_builds_all(self):
        d = self.decide()
        self.assertEqual("publish", d.action)
        self.assertEqual(["3.24.5", "3.38.0", "3.38.1", "3.47.8"], [r.version for r in d.builds])
        self.assertEqual([], d.reused)

    def test_no_pending_stops(self):
        d = self.decide(main_ledger=SEED + ALL_PENDING)
        self.assertEqual(Decision("stop", [], []), d)

    def test_skipped_row_is_not_pending(self):
        skipped = LedgerRow("3.13.7", "3.47.8", "2026-10-23", "")
        d = self.decide(main_ledger=SEED + [skipped])
        self.assertEqual(["3.24.5", "3.38.0", "3.38.1"], [r.version for r in d.builds])

    def test_reuses_hashes_from_branch(self):
        d = self.decide(branch=SEED + [ROW_3_13_7])
        self.assertEqual("publish", d.action)
        self.assertEqual([ROW_3_13_7], d.reused)
        self.assertEqual(["3.24.5", "3.38.0", "3.38.1"], [r.version for r in d.builds])

    def test_everything_on_branch_and_pr_open_stops(self):
        d = self.decide(branch=SEED + ALL_PENDING, on_main=True, pr_open=True)
        self.assertEqual("stop", d.action)

    def test_closed_pr_republishes(self):
        d = self.decide(branch=SEED + ALL_PENDING, on_main=True, pr_open=False)
        self.assertEqual("publish", d.action)
        self.assertEqual([], d.builds)
        self.assertEqual(4, len(d.reused))

    def test_stale_branch_republishes(self):
        d = self.decide(branch=SEED + ALL_PENDING, on_main=False, pr_open=True)
        self.assertEqual("publish", d.action)
        self.assertEqual([], d.builds)
        self.assertEqual(4, len(d.reused))


class CliTest(unittest.TestCase):
    def test_cli_writes_plan_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = os.path.join(tmp, "ledger.csv")
            branch = os.path.join(tmp, "branch.csv")
            out = os.path.join(tmp, "plan.json")
            write_ledger(ledger, SEED)
            write_ledger(branch, SEED + [ROW_3_13_7])
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                code = main(["--releases", FIXTURE, "--ledger", ledger, "--branch-ledger", branch,
                             "--branch-on-main", "true", "--pr-open", "false", "--out", out])
            self.assertEqual(0, code)
            with open(out, encoding="utf-8") as f:
                plan = json.load(f)
        self.assertEqual({"action", "branch_on_main", "pr_open", "builds", "reused"}, set(plan))
        self.assertEqual("publish", plan["action"])
        self.assertIs(True, plan["branch_on_main"])
        self.assertIs(False, plan["pr_open"])
        self.assertEqual({"dart_version": BUILD_BETA, "flutter_version": "3.38.0", "release_date": "2025-11-12",
                          "archive_url": "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/"
                                         "flutter_linux_3.38.0-stable.tar.xz",
                          "sha256": "38038038038038038038038038038038038038038038038038038038038038aa"},
                         next(b for b in plan["builds"] if b["dart_version"] == BUILD_BETA))
        self.assertEqual([{"dart_version": "3.13.7", "flutter_version": "3.47.8", "release_date": "2026-10-23",
                           "hash": "c" * 32}], plan["reused"])


if __name__ == "__main__":
    unittest.main()
