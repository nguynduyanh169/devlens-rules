"""Reads and bumps the two meta values of src/rules.sql that a rules PR changes: version and published_at."""
import re

_VERSION = re.compile(r"\('version', '(\d+)'\)")
_PUBLISHED_AT = re.compile(r"\('published_at', '[^']*'\)")
_INSTANT = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


class MetaError(ValueError):
    pass


def _only_match(pattern: re.Pattern, sql: str, what: str) -> re.Match:
    matches = list(pattern.finditer(sql))
    if len(matches) != 1:
        raise MetaError(f"rules.sql must hold exactly one {what} meta row, found {len(matches)}")
    return matches[0]


def read_version(sql: str) -> int:
    return int(_only_match(_VERSION, sql, "version").group(1))


def bump_meta(sql: str, version: int, published_at: str) -> str:
    if not _INSTANT.fullmatch(published_at):
        raise MetaError(f"published_at must be YYYY-MM-DDTHH:MM:SSZ, found '{published_at}'")
    _only_match(_VERSION, sql, "version")
    _only_match(_PUBLISHED_AT, sql, "published_at")
    sql = _VERSION.sub(f"('version', '{version}')", sql)
    return _PUBLISHED_AT.sub(f"('published_at', '{published_at}')", sql)
