#!/usr/bin/env bash
# Builds the rules database from src/schema.sql + src/rules.sql + the dart-snapshot rows generated from
# src/dart-snapshots.csv, and writes the publish set:
#   v1/rules-<version>.db       the db the app downloads; a published file never changes
#   v1/rules_latest.json        the manifest the app polls
# OUT_DIR=<dir> writes both somewhere else instead of v1/ (to check a build without touching the published set).
# Needs python3, the sqlite3 CLI, shasum, cmp and wc. Runs from any directory.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$here/src"
out="${OUT_DIR:-$here/v1}"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
db="$work/rules.db"

# Generated first and on its own: inside the { } pipeline below, a failing python3 would be masked by the group's
# exit status (the last echo's).
(cd "$here" && python3 -m tools.ledger sql src/dart-snapshots.csv) > "$work/dart-snapshot.sql"

# One session so page_size is set before the first table exists. journal_mode=DELETE keeps the header a rollback
# journal one: Android opens the file read-only and cannot do that for a WAL header without a -shm file.
{
  echo "PRAGMA page_size=1024;"
  echo "PRAGMA journal_mode=DELETE;"
  cat "$src/schema.sql" "$src/rules.sql" "$work/dart-snapshot.sql"
  echo "VACUUM;"
} | sqlite3 -bail "$db" > /dev/null

check="$(sqlite3 "$db" "PRAGMA quick_check;")"
if [ "$check" != "ok" ]; then
  echo "build.sh: quick_check failed: $check" >&2
  exit 1
fi
fk="$(sqlite3 "$db" "PRAGMA foreign_key_check;")"
if [ -n "$fk" ]; then
  echo "build.sh: foreign_key_check failed: $fk" >&2
  exit 1
fi

# RulesDbReader in the app accepts only the exact schema v1 objects: four tables and SQLite's own automatic indexes. Any
# other object (an index, sqlite_sequence from AUTOINCREMENT, sqlite_stat1 from ANALYZE, a view, a trigger) makes every
# installed app reject the file as invalid. Fail here instead, before the file reaches the publish set.
tables="$(sqlite3 "$db" "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name;" | tr '\n' ' ')"
if [ "$tables" != "matchers meta rules version_tables " ]; then
  echo "build.sh: sqlite_master must hold exactly the tables meta, rules, matchers and version_tables, found: $tables" >&2
  exit 1
fi
others="$(sqlite3 "$db" "SELECT type || ' ' || name FROM sqlite_master WHERE type <> 'table' AND NOT (type = 'index' AND name LIKE 'sqlite\_autoindex\_%' ESCAPE '\\' AND sql IS NULL);")"
if [ -n "$others" ]; then
  echo "build.sh: sqlite_master holds objects other than the four tables and their sqlite_autoindex_* indexes: $others" >&2
  echo "build.sh: RulesDbReader rejects them; a schema change needs a schema_version bump and publishing under v2/." >&2
  exit 1
fi

version="$(sqlite3 "$db" "SELECT value FROM meta WHERE key = 'version';")"
schema_version="$(sqlite3 "$db" "SELECT value FROM meta WHERE key = 'schema_version';")"
published_at="$(sqlite3 "$db" "SELECT value FROM meta WHERE key = 'published_at';")"

# meta must say what RulesDbReader and the manifest expect: schema 1, a positive integer version, an ISO-8601 UTC instant.
if [ "$schema_version" != "1" ]; then
  echo "build.sh: meta schema_version must be 1, found: '$schema_version'" >&2
  exit 1
fi
if ! [[ "$version" =~ ^[1-9][0-9]*$ ]]; then
  echo "build.sh: meta version must be a positive integer, found: '$version'" >&2
  exit 1
fi
if ! [[ "$published_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] \
  || [ "$(sqlite3 "$db" "SELECT datetime('$published_at') IS NULL;")" != "0" ]; then
  echo "build.sh: meta published_at must be an ISO-8601 UTC instant (YYYY-MM-DDTHH:MM:SSZ), found: '$published_at'" >&2
  exit 1
fi

# A published rules-<version>.db never changes: apps compare its sha256 with the manifest and never re-download a
# version they have. Rebuilding the same bytes is fine; other bytes under the same version need a version bump.
if [ -e "$out/rules-$version.db" ] && ! cmp -s "$db" "$out/rules-$version.db"; then
  echo "build.sh: $out/rules-$version.db is already published with other bytes; raise meta version in src/rules.sql" >&2
  exit 1
fi

mkdir -p "$out"
cp "$db" "$out/rules-$version.db"

size="$(wc -c < "$db" | tr -d '[:space:]')"
sha256="$(shasum -a 256 "$db" | cut -d ' ' -f 1)"
printf '{"schemaVersion":%s,"version":%s,"publishedAt":"%s","file":"rules-%s.db","size":%s,"sha256":"%s"}\n' \
  "$schema_version" "$version" "$published_at" "$version" "$size" "$sha256" > "$out/rules_latest.json"

echo "version: $version"
echo "size:    $size"
echo "sha256:  $sha256"
