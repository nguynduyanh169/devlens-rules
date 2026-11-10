-- Detection rules shipped in the app and published as rules_latest.db.
-- Edit this file, raise meta.version, then run build.sh. Rule order is priority order (frameworks first).
-- dart-snapshot rows are not here: build.sh generates them from src/dart-snapshots.csv.
BEGIN;

INSERT INTO meta (key, value) VALUES
  ('schema_version', '1'),
  ('version', '5'),
  ('published_at', '2026-11-10T07:36:54Z');

INSERT INTO rules (id, position, label, kind, category, vendor, description, url, show_as_filter) VALUES
  ('flutter', 1, 'Flutter', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('react-native', 2, 'React Native', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('expo', 3, 'Expo', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('unity', 4, 'Unity', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('unreal', 5, 'Unreal Engine', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('godot', 6, 'Godot', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('cocos', 7, 'Cocos', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('dotnet', 8, '.NET MAUI / Xamarin', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('compose-multiplatform', 9, 'Compose Multiplatform', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('cordova', 10, 'Cordova', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('capacitor', 11, 'Capacitor', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('nativescript', 12, 'NativeScript', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('lynx', 13, 'Lynx', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('qt', 14, 'Qt', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('libgdx', 15, 'libGDX', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('gamemaker', 16, 'GameMaker', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('defold', 17, 'Defold', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('solar2d', 18, 'Solar2D', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('python', 19, 'Python', 'LANGUAGE', NULL, NULL, NULL, NULL, 1),
  ('twa', 20, 'TWA (PWA)', 'FRAMEWORK', NULL, NULL, NULL, NULL, 1),
  ('jetpack-compose', 21, 'Jetpack Compose', 'UI_TOOLKIT', NULL, NULL, NULL, NULL, 0),
  ('kotlin', 22, 'Kotlin', 'LANGUAGE', NULL, NULL, NULL, NULL, 0),
  ('hermes', 23, 'Hermes', 'FRAMEWORK', NULL, NULL, NULL, NULL, 0);

-- Every ARCHIVE_PATH pattern is relative to the APK root. Matchers marked "unverified" were not checked against a real app.
INSERT INTO matchers (rule_id, position, target, mode, pattern) VALUES
  ('flutter', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libflutter.so'),
  ('flutter', 2, 'ARCHIVE_PATH', 'PREFIX', 'assets/flutter_assets/'),
  ('react-native', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libreactnativejni.so'),
  ('react-native', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libreactnative.so'),
  ('react-native', 3, 'ARCHIVE_PATH', 'EXACT', 'assets/index.android.bundle'),
  ('expo', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libexpo-modules-core.so'),
  ('expo', 2, 'ARCHIVE_PATH', 'EXACT', 'assets/app.config'),
  ('unity', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libunity.so'),
  ('unity', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libil2cpp.so'),
  ('unreal', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libUE4.so'), -- unverified
  ('unreal', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libUnreal.so'), -- unverified
  ('godot', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libgodot_android.so'),
  ('cocos', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libcocos2dcpp.so'),
  ('cocos', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libcocos2djs.so'),
  ('cocos', 3, 'NATIVE_LIB_NAME', 'EXACT', 'libcocos.so'),
  ('dotnet', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libmonodroid.so'),
  ('dotnet', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libmonosgen-2.0.so'),
  ('dotnet', 3, 'ARCHIVE_PATH', 'PREFIX', 'assemblies/'),
  ('compose-multiplatform', 1, 'ARCHIVE_PATH', 'PREFIX', 'composeResources/'),
  ('cordova', 1, 'ARCHIVE_PATH', 'EXACT', 'assets/www/cordova.js'),
  ('capacitor', 1, 'ARCHIVE_PATH', 'EXACT', 'assets/capacitor.config.json'),
  ('capacitor', 2, 'ARCHIVE_PATH', 'EXACT', 'assets/native-bridge.js'),
  ('nativescript', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libNativeScript.so'),
  ('lynx', 1, 'NATIVE_LIB_NAME', 'EXACT', 'liblynx.so'),
  ('qt', 1, 'NATIVE_LIB_NAME', 'REGEX', 'libQt[56]Core(_[A-Za-z0-9_-]+)?\.so'),
  ('libgdx', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libgdx.so'), -- unverified
  ('gamemaker', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libyoyo.so'), -- unverified
  ('defold', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libdmengine.so'), -- unverified
  ('solar2d', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libcorona.so'), -- unverified
  ('python', 1, 'NATIVE_LIB_NAME', 'REGEX', 'libpython3\.[0-9]{1,2}m?\.so'),
  ('python', 2, 'ARCHIVE_PATH', 'PREFIX', 'assets/chaquopy/'), -- unverified
  ('twa', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.androidbrowserhelper.trusted.LauncherActivity'), -- unverified
  ('jetpack-compose', 1, 'ARCHIVE_PATH', 'EXACT', 'META-INF/androidx.compose.ui_ui.version'),
  ('kotlin', 1, 'ARCHIVE_PATH', 'PREFIX', 'kotlin/'),
  ('kotlin', 2, 'ARCHIVE_PATH', 'REGEX', 'META-INF/.+\.kotlin_module'),
  ('hermes', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libhermes.so'),
  ('hermes', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libhermesvm.so');

-- hermes-version maps a Hermes release string to the React Native release(s) that ship it. Source:
-- packages/react-native/sdks/hermes-engine/version.properties of the React Native repo, read on 2026-11-05.
-- A value with an en dash (U+2013) is a range: the same Hermes build shipped in both React Native minors.
INSERT INTO version_tables (table_name, key, value) VALUES
  ('hermes-version', '250829098.0.1', '0.82'),
  ('hermes-version', '250829098.0.4', '0.83'),
  ('hermes-version', '250829098.0.7', '0.84'),
  ('hermes-version', '250829098.0.9', '0.84'),
  ('hermes-version', '250829098.0.10', '0.85'),
  ('hermes-version', '250829098.0.14', '0.86'),
  ('hermes-version', '250829098.0.16', '0.86–0.87'),
  ('hermes-version', '250829098.0.17', '0.86–0.87'),
  ('hermes-version', '260318099.0.4', '0.88'),
  ('hermes-version', '260318099.0.5', '0.88'),
  ('hermes-version', '0.14.0', '0.83'),
  ('hermes-version', '0.14.1', '0.83–0.84'),
  ('hermes-version', '0.15.1', '0.84'),
  ('hermes-version', '0.16.0', '0.85'),
  ('hermes-version', '0.17.0', '0.86');

COMMIT;
