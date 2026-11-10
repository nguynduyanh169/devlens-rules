import os
import tempfile
import unittest

from tools.ledger import LedgerError, LedgerRow, read_ledger, to_sql, write_ledger

SEED_SQL = (
    "INSERT INTO version_tables (table_name, key, value) VALUES\n"
    "  ('dart-snapshot', 'f956f595844a2f845a55707faaaa51e4', '3.27'),\n"
    "  ('dart-snapshot', 'd91c0e6f35f0eb2e44124e8f42aa44a7', '3.29'),\n"
    "  ('dart-snapshot', '830f4f59e7969c70b595182826435c19', '3.32');\n"
)
H1 = "a" * 32
H2 = "b" * 32
HEADER_LINE = "dart_version,flutter_version,release_date,hash\n"


def row(dart, flutter, date="2026-01-01", h=H1):
    return LedgerRow(dart, flutter, date, h)


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def write_text(self, text):
        path = os.path.join(self.dir, "ledger.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return path

    def test_seed_ledger_is_valid(self):
        rows = read_ledger("src/dart-snapshots.csv")
        self.assertEqual(3, len(rows))
        self.assertEqual(LedgerRow("3.6.2", "3.27.4", "2025-02-05", "f956f595844a2f845a55707faaaa51e4"), rows[0])

    def test_to_sql_seed(self):
        self.assertEqual(SEED_SQL, to_sql(read_ledger("src/dart-snapshots.csv")))

    def test_to_sql_merges_same_hash_same_minor(self):
        sql = to_sql([row("3.13.0", "3.47.0"), row("3.13.4", "3.47.5")])
        self.assertEqual(1, sql.count("('dart-snapshot', '%s', '3.47')" % H1))
        self.assertEqual(1, sql.count("('dart-snapshot'"))

    def test_to_sql_conflict_raises(self):
        with self.assertRaises(LedgerError) as cm:
            to_sql([row("3.12.0", "3.44.0"), row("3.13.0", "3.47.0")])
        message = str(cm.exception)
        self.assertIn(H1, message)
        self.assertIn("3.44", message)
        self.assertIn("3.47", message)

    def test_to_sql_skips_empty_hash(self):
        sql = to_sql([row("3.13.0", "3.47.0"), row("3.13.1", "3.47.1", h="")])
        self.assertEqual(1, sql.count("('dart-snapshot'"))

    def test_to_sql_without_hashes_is_empty(self):
        self.assertEqual("", to_sql([row("3.13.1", "3.47.1", h="")]))
        self.assertEqual("", to_sql([]))

    def test_to_sql_orders_minors_numerically(self):
        sql = to_sql([row("3.1.0", "3.10.0", h=H1), row("3.0.0", "3.9.0", h=H2)])
        self.assertLess(sql.index("'3.9'"), sql.index("'3.10'"))

    def test_round_trip_keeps_odd_dart_versions(self):
        rows = [
            row("3.10.0 (build 3.10.0-290.4.beta)", "3.38.0", "2025-11-12", H1),
            row('a,b"c', "3.38.1", "2025-11-13", H2),
        ]
        path = os.path.join(self.dir, "out.csv")
        write_ledger(path, rows)
        self.assertEqual(rows, read_ledger(path))

    def test_write_sorts_by_release_date_then_dart_version(self):
        rows = [
            row("3.13.1", "3.47.1", "2026-08-19", H1),
            row("3.12.0", "3.44.0", "2026-05-18", H2),
            row("3.11.9", "3.41.9", "2026-05-18", H2),
        ]
        path = os.path.join(self.dir, "out.csv")
        write_ledger(path, rows)
        self.assertEqual(["3.11.9", "3.12.0", "3.13.1"], [r.dart_version for r in read_ledger(path)])
        with open(path, encoding="utf-8", newline="") as f:
            self.assertEqual(HEADER_LINE, f.readline())

    def test_rejects_bad_input(self):
        good = "3.13.0,3.47.0,2026-08-12," + H1 + "\n"
        cases = {
            "header": "dart,flutter,date,hash\n" + good,
            "hash": HEADER_LINE + "3.13.0,3.47.0,2026-08-12,XYZ\n",
            "flutter_version": HEADER_LINE + "3.13.0,3.47,2026-08-12," + H1 + "\n",
            "release_date": HEADER_LINE + "3.13.0,3.47.0,2026/08/12," + H1 + "\n",
            "duplicate": HEADER_LINE + good + good,
            "empty dart_version": HEADER_LINE + ",3.47.0,2026-08-12," + H1 + "\n",
        }
        for name, text in cases.items():
            with self.subTest(name):
                with self.assertRaises(LedgerError) as cm:
                    read_ledger(self.write_text(text))
                self.assertRegex(str(cm.exception), r"line \d+")


if __name__ == "__main__":
    unittest.main()
