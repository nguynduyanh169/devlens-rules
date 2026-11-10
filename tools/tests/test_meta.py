import unittest

from tools.meta import MetaError, bump_meta, read_version

SAMPLE = """-- Detection rules.
BEGIN;

INSERT INTO meta (key, value) VALUES
  ('schema_version', '1'),
  ('version', '3'),
  ('published_at', '2026-11-05T00:00:00Z');

INSERT INTO rules (id) VALUES ('flutter');
COMMIT;
"""


class MetaTest(unittest.TestCase):
    def test_read_version(self):
        self.assertEqual(3, read_version(SAMPLE))

    def test_bump_meta_changes_only_the_two_values(self):
        bumped = bump_meta(SAMPLE, 4, "2026-11-10T03:30:00Z")
        expected = SAMPLE.replace("('version', '3')", "('version', '4')").replace(
            "('published_at', '2026-11-05T00:00:00Z')", "('published_at', '2026-11-10T03:30:00Z')")
        self.assertEqual(expected, bumped)
        self.assertEqual(4, read_version(bumped))

    def test_missing_or_repeated_pattern_raises(self):
        missing_version = SAMPLE.replace("  ('version', '3'),\n", "")
        repeated_version = SAMPLE.replace("('version', '3'),", "('version', '3'),\n  ('version', '3'),")
        missing_published = SAMPLE.replace("('published_at', '2026-11-05T00:00:00Z')", "('other', 'x')")
        for name, sql in {"missing version": missing_version, "repeated version": repeated_version,
                          "missing published_at": missing_published}.items():
            with self.subTest(name):
                with self.assertRaises(MetaError):
                    bump_meta(sql, 4, "2026-11-10T03:30:00Z")
        with self.assertRaises(MetaError):
            read_version(missing_version)

    def test_bad_published_at_raises(self):
        for bad in ("2026-11-10", "2026-11-10T03:30:00", "2026-11-10 03:30:00Z", "2026-11-10T03:30:00.5Z"):
            with self.subTest(bad):
                with self.assertRaises(MetaError):
                    bump_meta(SAMPLE, 4, bad)


if __name__ == "__main__":
    unittest.main()
