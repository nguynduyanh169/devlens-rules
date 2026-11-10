"""Reads the Dart snapshot hash of a Flutter libapp.so: a port of DevLens's DartSnapshot (core/parser, Kotlin).

The Dart VM snapshot data (_kDartVmSnapshotData) sits at the start of .rodata, so near the front of the file. Its header
is a u32 magic (0xdcdcf5f5), an int64 length, an int64 kind, then 32 ASCII characters [0-9a-f] that name the Dart VM
build (at +20). Only the ELF identification is checked: the 4-byte magic and EI_DATA (byte 5: 1 = little-endian,
2 = big-endian, the byte order of the snapshot magic). Only offsets that are multiples of 8 are tried, each one
bounds-checked against both the prefix and the file size; malformed input gives None, never an exception.

Usage: python3 -m tools.dart_snapshot <apk> --dart-version D --flutter-version F --release-date R --out FILE
writes the build result JSON (status ok with the hash, or failed with an error) and exits 0 or 1.
"""
import argparse
import json
import sys
import zipfile

PREFIX_BYTES = 65_536

_ELF_MAGIC = b"\x7fELF"
_EI_DATA = 5
_ELFDATA2LSB = 1
_ELFDATA2MSB = 2
_SNAPSHOT_MAGIC = 0xDCDCF5F5
_MAGIC_SIZE = 4
_HASH_OFFSET = 20
_HASH_LENGTH = 32
_HEADER_SIZE = _HASH_OFFSET + _HASH_LENGTH
_STEP = 8
_HEX = frozenset(b"0123456789abcdef")

LIBAPP = "lib/arm64-v8a/libapp.so"
LIBFLUTTER = "lib/arm64-v8a/libflutter.so"


class SnapshotError(Exception):
    pass


def read_hash(prefix: bytes, file_size: int) -> str | None:
    """The hash of the first Dart snapshot header in `prefix` (the first bytes of a libapp.so of `file_size` bytes)."""
    if len(prefix) < _EI_DATA + 1 or prefix[:4] != _ELF_MAGIC:
        return None
    ei_data = prefix[_EI_DATA]
    if ei_data == _ELFDATA2LSB:
        byteorder = "little"
    elif ei_data == _ELFDATA2MSB:
        byteorder = "big"
    else:
        return None

    available = min(len(prefix), file_size)
    offset = 0
    while offset + _HEADER_SIZE <= available:
        magic = int.from_bytes(prefix[offset:offset + _MAGIC_SIZE], byteorder)
        if magic == _SNAPSHOT_MAGIC:
            candidate = prefix[offset + _HASH_OFFSET:offset + _HEADER_SIZE]
            if all(byte in _HEX for byte in candidate):
                return candidate.decode("ascii")
        offset += _STEP
    return None


def read_apk_hash(apk_path: str) -> str:
    with zipfile.ZipFile(apk_path) as apk:
        try:
            info = apk.getinfo(LIBAPP)
        except KeyError:
            raise SnapshotError(f"no {LIBAPP} in APK") from None
        with apk.open(info) as f:
            prefix = f.read(PREFIX_BYTES)
    snapshot_hash = read_hash(prefix, info.file_size)
    if snapshot_hash is None:
        raise SnapshotError("no Dart snapshot header in libapp.so")
    return snapshot_hash


def engine_has_hash(apk_path: str, snapshot_hash: str) -> bool:
    """Whether the engine of the same APK holds the hash as plain ASCII: the VM checks a snapshot against it."""
    with zipfile.ZipFile(apk_path) as apk:
        try:
            data = apk.read(LIBFLUTTER)
        except KeyError:
            return False
    return snapshot_hash.encode("ascii") in data


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m tools.dart_snapshot")
    parser.add_argument("apk")
    parser.add_argument("--dart-version", required=True)
    parser.add_argument("--flutter-version", required=True)
    parser.add_argument("--release-date", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    result = {"dart_version": args.dart_version, "flutter_version": args.flutter_version,
              "release_date": args.release_date}
    try:
        snapshot_hash = read_apk_hash(args.apk)
        if not engine_has_hash(args.apk, snapshot_hash):
            raise SnapshotError(f"hash {snapshot_hash} not found in libflutter.so")
        result.update(status="ok", hash=snapshot_hash)
    except (SnapshotError, OSError, zipfile.BadZipFile) as e:
        result.update(status="failed", error=str(e))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f)
        f.write("\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
