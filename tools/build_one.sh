#!/usr/bin/env bash
# Builds a hello-world app with one Flutter release on a Linux runner and writes the build result JSON: status ok with
# the Dart snapshot hash of its lib/arm64-v8a/libapp.so, or status failed with the step that failed.
# Input (env): DART_VERSION FLUTTER_VERSION RELEASE_DATE ARCHIVE_URL SHA256 RESULT_FILE (relative to the repo root or
# absolute). Needs curl, sha256sum, tar with xz, jq, python3, a JDK and the Android SDK (all on ubuntu-24.04 runners).
# Exits 1 when the result is failed.
set -euo pipefail

: "${DART_VERSION:?}" "${FLUTTER_VERSION:?}" "${RELEASE_DATE:?}" "${ARCHIVE_URL:?}" "${SHA256:?}" "${RESULT_FILE:?}"

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
case "$RESULT_FILE" in
  /*) result="$RESULT_FILE" ;;
  *) result="$repo/$RESULT_FILE" ;;
esac
mkdir -p "$(dirname "$result")"
work="${RUNNER_TEMP:-$(mktemp -d)}/flutter-$FLUTTER_VERSION"

step="setup"
write_failure() {
  # The hash step writes its own result, failed or not; every earlier step leaves none, so write one here.
  [ -e "$result" ] || jq -n --arg d "$DART_VERSION" --arg f "$FLUTTER_VERSION" --arg r "$RELEASE_DATE" \
    --arg e "$step failed" \
    '{dart_version: $d, flutter_version: $f, release_date: $r, status: "failed", error: $e}' > "$result"
}
trap write_failure ERR

step="download"
mkdir -p "$work"
curl -fsSL --retry 3 -o "$work/flutter.tar.xz" "$ARCHIVE_URL"

step="sha256 check"
echo "$SHA256  $work/flutter.tar.xz" | sha256sum -c -

step="extract"
tar -xJf "$work/flutter.tar.xz" -C "$work"
export PATH="$work/flutter/bin:$PATH"

step="flutter setup"
flutter config --no-analytics > /dev/null
flutter --version

step="flutter create"
(cd "$work" && flutter create --platforms android --project-name probe probe)

step="flutter build apk"
(cd "$work/probe" && flutter build apk --release --target-platform android-arm64)

step="read hash"
cd "$repo"
python3 -m tools.dart_snapshot "$work/probe/build/app/outputs/flutter-apk/app-release.apk" \
  --dart-version "$DART_VERSION" --flutter-version "$FLUTTER_VERSION" --release-date "$RELEASE_DATE" \
  --out "$result"
cat "$result"
