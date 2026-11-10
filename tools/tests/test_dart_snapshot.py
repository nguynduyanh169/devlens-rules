import json
import os
import struct
import tempfile
import unittest
import zipfile

from tools.dart_snapshot import SnapshotError, engine_has_hash, main, read_apk_hash, read_hash

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "libapp-3.27.4-prefix.so")
HASH_3_27 = "f956f595844a2f845a55707faaaa51e4"
HEX = "0123456789abcdef0123456789abcdef"


def big_endian_elf(snapshot_hash: bytes = HEX.encode()) -> bytes:
    head = b"\x7fELF\x02\x02" + bytes(64 - 6)
    return head + struct.pack(">I", 0xDCDCF5F5) + bytes(16) + snapshot_hash


def fixture_bytes() -> bytes:
    with open(FIXTURE, "rb") as f:
        return f.read()


class ReadHashTest(unittest.TestCase):
    def test_fixture_gives_the_3_27_hash(self):
        data = fixture_bytes()
        self.assertEqual(HASH_3_27, read_hash(data, len(data)))

    def test_not_elf_is_none(self):
        data = b"PK\x03\x04" + bytes(200)
        self.assertIsNone(read_hash(data, len(data)))

    def test_shorter_than_six_bytes_is_none(self):
        self.assertIsNone(read_hash(b"\x7fELF\x02", 5))

    def test_unknown_ei_data_is_none(self):
        data = bytearray(big_endian_elf())
        data[5] = 3
        self.assertIsNone(read_hash(bytes(data), len(data)))

    def test_elf_without_magic_is_none(self):
        data = b"\x7fELF\x02\x01" + bytes(200)
        self.assertIsNone(read_hash(data, len(data)))

    def test_big_endian_header(self):
        data = big_endian_elf()
        self.assertEqual(HEX, read_hash(data, len(data)))

    def test_header_past_file_size_is_none(self):
        data = big_endian_elf()
        self.assertIsNone(read_hash(data, 64 + 51))
        self.assertEqual(HEX, read_hash(data, 64 + 52))

    def test_non_hex_hash_is_none(self):
        data = big_endian_elf(b"g" * 32)
        self.assertIsNone(read_hash(data, len(data)))


class ApkTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def apk(self, entries: dict[str, bytes]) -> str:
        path = os.path.join(self.dir, "app-release.apk")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in entries.items():
                z.writestr(name, data)
        return path

    def flutter_apk(self, engine: bytes = b"xx" + HASH_3_27.encode() + b"yy") -> str:
        return self.apk({"lib/arm64-v8a/libapp.so": fixture_bytes(), "lib/arm64-v8a/libflutter.so": engine})

    def run_cli(self, apk_path: str) -> tuple[int, dict]:
        out = os.path.join(self.dir, "result.json")
        code = main([apk_path, "--dart-version", "3.6.2", "--flutter-version", "3.27.4",
                     "--release-date", "2025-02-05", "--out", out])
        with open(out, encoding="utf-8") as f:
            return code, json.load(f)

    def test_read_apk_hash_from_zip(self):
        self.assertEqual(HASH_3_27, read_apk_hash(self.flutter_apk()))

    def test_apk_without_libapp_raises(self):
        with self.assertRaisesRegex(SnapshotError, "no lib/arm64-v8a/libapp.so in APK"):
            read_apk_hash(self.apk({"classes.dex": b"dex"}))

    def test_apk_with_libapp_but_no_header_raises(self):
        with self.assertRaisesRegex(SnapshotError, "no Dart snapshot header in libapp.so"):
            read_apk_hash(self.apk({"lib/arm64-v8a/libapp.so": b"\x7fELF\x02\x01" + bytes(200)}))

    def test_engine_has_hash(self):
        self.assertTrue(engine_has_hash(self.flutter_apk(), HASH_3_27))
        self.assertFalse(engine_has_hash(self.flutter_apk(engine=b"no hash here"), HASH_3_27))
        self.assertFalse(engine_has_hash(self.apk({"lib/arm64-v8a/libapp.so": fixture_bytes()}), HASH_3_27))

    def test_cli_writes_ok_result(self):
        code, result = self.run_cli(self.flutter_apk())
        self.assertEqual(0, code)
        self.assertEqual({"dart_version": "3.6.2", "flutter_version": "3.27.4", "release_date": "2025-02-05",
                          "status": "ok", "hash": HASH_3_27}, result)

    def test_cli_writes_failed_result(self):
        code, result = self.run_cli(self.apk({"classes.dex": b"dex"}))
        self.assertEqual(1, code)
        self.assertEqual("failed", result["status"])
        self.assertIn("no lib/arm64-v8a/libapp.so", result["error"])
        self.assertEqual("3.6.2", result["dart_version"])

    def test_cli_fails_when_engine_lacks_hash(self):
        code, result = self.run_cli(self.flutter_apk(engine=b"no hash here"))
        self.assertEqual(1, code)
        self.assertEqual("failed", result["status"])
        self.assertEqual(f"hash {HASH_3_27} not found in libflutter.so", result["error"])


if __name__ == "__main__":
    unittest.main()
