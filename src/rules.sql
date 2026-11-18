-- Detection rules shipped in the app and published as rules_latest.db.
-- Edit this file, raise meta.version, then run build.sh. Rule order is priority order (frameworks first).
-- dart-snapshot rows are not here: build.sh generates them from src/dart-snapshots.csv.
BEGIN;

INSERT INTO meta (key, value) VALUES
  ('schema_version', '1'),
  ('version', '6'),
  ('published_at', '2026-11-18T09:13:58Z');

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

-- Third-party SDKs (kind THIRD_PARTY_SDK, since v6). Older apps drop rules with an unknown kind, so they never see these.
-- Matchers use names R8 does not rename: manifest component classes the SDK's AAR merges, its .so names, and Java
-- resources at the APK root (Google Play services / Firebase / Play Billing AARs ship `<artifact>.properties` there,
-- holding `version=`). Never a DEX class name. Third-party SDKs ship no `META-INF/<group>_<artifact>.version` file, so
-- none of these rules yields a version yet.
INSERT INTO rules (id, position, label, kind, category, vendor, description, url, show_as_filter) VALUES
  ('firebase', 24, 'Firebase', 'THIRD_PARTY_SDK', 'BACKEND', 'Google', 'Firebase core (firebase-common), pulled in by every Firebase product.', 'https://firebase.google.com/docs/android/setup', 0),
  ('firebase-analytics', 25, 'Google Analytics for Firebase', 'THIRD_PARTY_SDK', 'ANALYTICS', 'Google', 'App measurement and event analytics.', 'https://firebase.google.com/docs/analytics', 0),
  ('firebase-crashlytics-ndk', 26, 'Firebase Crashlytics (NDK)', 'THIRD_PARTY_SDK', 'CRASH_REPORTING', 'Google', 'Native crash reporting. The JVM-only Crashlytics leaves no trace these matchers can see.', 'https://firebase.google.com/docs/crashlytics', 0),
  ('firebase-messaging', 27, 'Firebase Cloud Messaging', 'THIRD_PARTY_SDK', 'PUSH', 'Google', 'Push notifications through FCM.', 'https://firebase.google.com/docs/cloud-messaging', 0),
  ('firebase-auth', 28, 'Firebase Authentication', 'THIRD_PARTY_SDK', 'BACKEND', 'Google', 'User sign-in backed by Firebase.', 'https://firebase.google.com/docs/auth', 0),
  ('google-sign-in', 29, 'Google Sign-In', 'THIRD_PARTY_SDK', 'BACKEND', 'Google', 'Sign in with a Google account (play-services-auth).', 'https://developers.google.com/identity', 0),
  ('admob', 30, 'Google Mobile Ads (AdMob)', 'THIRD_PARTY_SDK', 'ADS', 'Google', 'AdMob and Ad Manager ads.', 'https://developers.google.com/admob/android', 0),
  ('meta-audience-network', 31, 'Meta Audience Network', 'THIRD_PARTY_SDK', 'ADS', 'Meta', 'Meta ads in third-party apps.', 'https://developers.facebook.com/docs/audience-network', 0),
  ('applovin', 32, 'AppLovin', 'THIRD_PARTY_SDK', 'ADS', 'AppLovin', 'AppLovin ads and MAX mediation.', 'https://developers.applovin.com', 0),
  ('unity-ads', 33, 'Unity Ads', 'THIRD_PARTY_SDK', 'ADS', 'Unity', 'Unity ads, also used outside Unity games.', 'https://docs.unity.com/ads', 0),
  ('ironsource', 34, 'ironSource (LevelPlay)', 'THIRD_PARTY_SDK', 'ADS', 'Unity', 'ironSource ads and LevelPlay mediation.', 'https://developers.is.com', 0),
  ('pangle', 35, 'Pangle', 'THIRD_PARTY_SDK', 'ADS', 'ByteDance', 'ByteDance ads network.', 'https://www.pangleglobal.com', 0),
  ('liftoff-vungle', 36, 'Liftoff Monetize (Vungle)', 'THIRD_PARTY_SDK', 'ADS', 'Liftoff', 'Vungle ads, now Liftoff Monetize.', 'https://liftoff.io', 0),
  ('appsflyer', 37, 'AppsFlyer', 'THIRD_PARTY_SDK', 'ANALYTICS', 'AppsFlyer', 'Install attribution and marketing analytics.', 'https://dev.appsflyer.com', 0),
  ('adjust', 38, 'Adjust', 'THIRD_PARTY_SDK', 'ANALYTICS', 'Adjust', 'Install attribution and marketing analytics.', 'https://dev.adjust.com', 0),
  ('facebook-sdk', 39, 'Facebook SDK', 'THIRD_PARTY_SDK', 'ANALYTICS', 'Meta', 'Facebook Login, Share and App Events.', 'https://developers.facebook.com/docs/android', 0),
  ('sentry', 40, 'Sentry', 'THIRD_PARTY_SDK', 'CRASH_REPORTING', 'Sentry', 'Error and crash reporting, performance monitoring.', 'https://docs.sentry.io/platforms/android', 0),
  ('bugsnag', 41, 'Bugsnag', 'THIRD_PARTY_SDK', 'CRASH_REPORTING', 'SmartBear', 'Native crash and ANR reporting (bugsnag-plugin-android-ndk / -anr).', 'https://docs.bugsnag.com/platforms/android', 0),
  ('okhttp', 42, 'OkHttp', 'THIRD_PARTY_SDK', 'NETWORK', 'Square', 'HTTP client; Retrofit, Coil and many SDKs bring it in.', 'https://square.github.io/okhttp', 0),
  ('cronet', 43, 'Cronet', 'THIRD_PARTY_SDK', 'NETWORK', 'Google', 'Chromium network stack, embedded build.', 'https://developer.android.com/develop/connectivity/cronet', 0),
  ('webrtc', 44, 'WebRTC', 'THIRD_PARTY_SDK', 'NETWORK', 'Google', 'Real-time audio, video and data channels.', 'https://webrtc.org', 0),
  ('conscrypt', 45, 'Conscrypt', 'THIRD_PARTY_SDK', 'NETWORK', 'Google', 'Bundled BoringSSL-based TLS provider.', 'https://github.com/google/conscrypt', 0),
  ('chucker', 46, 'Chucker', 'THIRD_PARTY_SDK', 'NETWORK', 'Chucker Team', 'In-app HTTP inspector, meant for debug builds.', 'https://github.com/ChuckerTeam/chucker', 0),
  ('realm', 47, 'Realm', 'THIRD_PARTY_SDK', 'DATABASE', 'MongoDB', 'Realm Java and Realm Kotlin object database.', 'https://github.com/realm/realm-kotlin', 0),
  ('sqlcipher', 48, 'SQLCipher', 'THIRD_PARTY_SDK', 'DATABASE', 'Zetetic', 'Encrypted SQLite.', 'https://www.zetetic.net/sqlcipher', 0),
  ('mmkv', 49, 'MMKV', 'THIRD_PARTY_SDK', 'DATABASE', 'Tencent', 'Memory-mapped key-value storage.', 'https://github.com/Tencent/MMKV', 0),
  ('objectbox', 50, 'ObjectBox', 'THIRD_PARTY_SDK', 'DATABASE', 'ObjectBox', 'On-device object database.', 'https://objectbox.io', 0),
  ('play-billing', 51, 'Google Play Billing', 'THIRD_PARTY_SDK', 'PAYMENT', 'Google', 'In-app purchases and subscriptions on Google Play.', 'https://developer.android.com/google/play/billing', 0),
  ('stripe', 52, 'Stripe', 'THIRD_PARTY_SDK', 'PAYMENT', 'Stripe', 'Card and wallet payments.', 'https://docs.stripe.com/sdks/android', 0),
  ('revenuecat-paywalls', 53, 'RevenueCat Paywalls', 'THIRD_PARTY_SDK', 'PAYMENT', 'RevenueCat', 'RevenueCat paywall UI (purchases-ui); the core purchases SDK merges no component.', 'https://www.revenuecat.com/docs', 0),
  ('onesignal', 54, 'OneSignal', 'THIRD_PARTY_SDK', 'PUSH', 'OneSignal', 'Push notifications and in-app messaging.', 'https://documentation.onesignal.com', 0),
  ('braze', 55, 'Braze', 'THIRD_PARTY_SDK', 'PUSH', 'Braze', 'Customer engagement: push, in-app messages, content cards.', 'https://www.braze.com/docs', 0),
  ('clevertap', 56, 'CleverTap', 'THIRD_PARTY_SDK', 'PUSH', 'CleverTap', 'Customer engagement: push, in-app messages, app inbox.', 'https://developer.clevertap.com', 0),
  ('play-core', 57, 'Google Play Core', 'THIRD_PARTY_SDK', 'OTHER', 'Google', 'In-app updates, reviews, feature delivery and Play Integrity.', 'https://developer.android.com/guide/playcore', 0),
  ('ml-kit', 58, 'ML Kit', 'THIRD_PARTY_SDK', 'OTHER', 'Google', 'On-device machine learning (barcode, face, text, ...).', 'https://developers.google.com/ml-kit', 0),
  ('google-maps', 59, 'Google Maps SDK', 'THIRD_PARTY_SDK', 'OTHER', 'Google', 'Maps SDK for Android (play-services-maps).', 'https://developers.google.com/maps/documentation/android-sdk', 0),
  ('tensorflow-lite', 60, 'TensorFlow Lite (LiteRT)', 'THIRD_PARTY_SDK', 'OTHER', 'Google', 'On-device ML inference runtime.', 'https://ai.google.dev/edge/litert', 0),
  ('zxing-embedded', 61, 'ZXing Android Embedded', 'THIRD_PARTY_SDK', 'OTHER', 'JourneyApps', 'Barcode scanning UI on top of ZXing.', 'https://github.com/journeyapps/zxing-android-embedded', 0),
  ('mupdf', 62, 'MuPDF', 'THIRD_PARTY_SDK', 'OTHER', 'Artifex', 'PDF rendering library (AGPL or commercial licence).', 'https://mupdf.com', 0);

INSERT INTO matchers (rule_id, position, target, mode, pattern) VALUES
  ('firebase', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.firebase.provider.FirebaseInitProvider'),
  ('firebase', 2, 'COMPONENT_CLASS', 'EXACT', 'com.google.firebase.components.ComponentDiscoveryService'),
  ('firebase-analytics', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.android.gms.measurement.AppMeasurementService'),
  ('firebase-analytics', 2, 'COMPONENT_CLASS', 'EXACT', 'com.google.android.gms.measurement.AppMeasurementJobService'),
  ('firebase-analytics', 3, 'ARCHIVE_PATH', 'EXACT', 'firebase-analytics.properties'),
  ('firebase-crashlytics-ndk', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libcrashlytics.so'), -- unverified
  ('firebase-crashlytics-ndk', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libcrashlytics-common.so'), -- unverified
  ('firebase-crashlytics-ndk', 3, 'NATIVE_LIB_NAME', 'EXACT', 'libcrashlytics-handler.so'), -- unverified
  ('firebase-crashlytics-ndk', 4, 'NATIVE_LIB_NAME', 'EXACT', 'libcrashlytics-trampoline.so'), -- unverified
  ('firebase-messaging', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.firebase.messaging.FirebaseMessagingService'),
  ('firebase-messaging', 2, 'COMPONENT_CLASS', 'EXACT', 'com.google.firebase.iid.FirebaseInstanceIdReceiver'),
  ('firebase-auth', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.firebase.auth.internal.GenericIdpActivity'),
  ('firebase-auth', 2, 'COMPONENT_CLASS', 'EXACT', 'com.google.firebase.auth.internal.RecaptchaActivity'),
  ('firebase-auth', 3, 'ARCHIVE_PATH', 'EXACT', 'firebase-auth.properties'),
  ('google-sign-in', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.android.gms.auth.api.signin.internal.SignInHubActivity'),
  ('google-sign-in', 2, 'ARCHIVE_PATH', 'EXACT', 'play-services-auth.properties'),
  ('admob', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.android.gms.ads.AdActivity'),
  ('admob', 2, 'COMPONENT_CLASS', 'EXACT', 'com.google.android.gms.ads.MobileAdsInitProvider'),
  ('admob', 3, 'ARCHIVE_PATH', 'EXACT', 'play-services-ads.properties'),
  ('meta-audience-network', 1, 'COMPONENT_CLASS', 'EXACT', 'com.facebook.ads.AudienceNetworkActivity'), -- unverified
  ('meta-audience-network', 2, 'COMPONENT_CLASS', 'EXACT', 'com.facebook.ads.AudienceNetworkContentProvider'), -- unverified
  ('applovin', 1, 'COMPONENT_CLASS', 'EXACT', 'com.applovin.adview.AppLovinFullscreenActivity'), -- unverified
  ('applovin', 2, 'COMPONENT_CLASS', 'EXACT', 'com.applovin.sdk.AppLovinInitProvider'), -- unverified
  ('unity-ads', 1, 'COMPONENT_CLASS', 'EXACT', 'com.unity3d.services.ads.adunit.AdUnitActivity'), -- unverified
  ('unity-ads', 2, 'COMPONENT_CLASS', 'EXACT', 'com.unity3d.ads.adplayer.FullScreenWebViewDisplay'), -- unverified
  ('ironsource', 1, 'COMPONENT_CLASS', 'EXACT', 'com.ironsource.sdk.controller.ControllerActivity'), -- unverified
  ('ironsource', 2, 'COMPONENT_CLASS', 'EXACT', 'com.ironsource.lifecycle.IronsourceLifecycleProvider'), -- unverified
  ('pangle', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.bytedance.sdk.openadsdk.'),
  ('pangle', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libpglarmor.so'),
  ('liftoff-vungle', 1, 'COMPONENT_CLASS', 'EXACT', 'com.vungle.ads.internal.ui.VungleActivity'),
  ('liftoff-vungle', 2, 'COMPONENT_CLASS', 'EXACT', 'com.vungle.ads.VungleProvider'),
  ('liftoff-vungle', 3, 'COMPONENT_CLASS', 'EXACT', 'com.vungle.warren.ui.VungleActivity'), -- unverified (SDK 6.x)
  ('appsflyer', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.appsflyer.'),
  ('appsflyer', 2, 'ARCHIVE_PATH', 'PREFIX', 'assets/com/appsflyer/'),
  ('adjust', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.adjust.sdk.'),
  ('facebook-sdk', 1, 'COMPONENT_CLASS', 'EXACT', 'com.facebook.internal.FacebookInitProvider'),
  ('facebook-sdk', 2, 'COMPONENT_CLASS', 'EXACT', 'com.facebook.FacebookActivity'),
  ('facebook-sdk', 3, 'COMPONENT_CLASS', 'EXACT', 'com.facebook.CustomTabMainActivity'),
  ('sentry', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libsentry-android.so'),
  ('sentry', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libsentry.so'),
  ('sentry', 3, 'COMPONENT_CLASS', 'PREFIX', 'io.sentry.'),
  ('sentry', 4, 'ARCHIVE_PATH', 'EXACT', 'META-INF/native-image/io.sentry/sentry/native-image.properties'),
  ('bugsnag', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libbugsnag-ndk.so'), -- unverified
  ('bugsnag', 2, 'NATIVE_LIB_NAME', 'EXACT', 'libbugsnag-plugin-android-anr.so'), -- unverified
  ('bugsnag', 3, 'NATIVE_LIB_NAME', 'EXACT', 'libbugsnag-root-detection.so'), -- unverified
  ('okhttp', 1, 'ARCHIVE_PATH', 'PREFIX', 'okhttp3/internal/publicsuffix/'),
  ('okhttp', 2, 'ARCHIVE_PATH', 'EXACT', 'META-INF/native-image/okhttp/okhttp/native-image.properties'),
  ('cronet', 1, 'NATIVE_LIB_NAME', 'REGEX', 'libcronet\.[0-9]+(\.[0-9]+){1,3}\.so'), -- unverified
  ('webrtc', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libjingle_peerconnection_so.so'),
  ('conscrypt', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libconscrypt_jni.so'),
  ('chucker', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.chuckerteam.chucker.'),
  ('realm', 1, 'NATIVE_LIB_NAME', 'EXACT', 'librealm-jni.so'), -- unverified (Realm Java)
  ('realm', 2, 'NATIVE_LIB_NAME', 'EXACT', 'librealmc.so'), -- unverified (Realm Kotlin)
  ('sqlcipher', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libsqlcipher.so'), -- unverified
  ('mmkv', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libmmkv.so'),
  ('objectbox', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libobjectbox-jni.so'), -- unverified
  ('play-billing', 1, 'COMPONENT_CLASS', 'EXACT', 'com.android.billingclient.api.ProxyBillingActivity'),
  ('play-billing', 2, 'COMPONENT_CLASS', 'EXACT', 'com.android.billingclient.api.ProxyBillingActivityV2'),
  ('play-billing', 3, 'ARCHIVE_PATH', 'EXACT', 'billing.properties'),
  ('stripe', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.stripe.android.'), -- unverified
  ('revenuecat-paywalls', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.revenuecat.purchases.'), -- unverified
  ('onesignal', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.onesignal.'), -- unverified
  ('braze', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.braze.'), -- unverified
  ('braze', 2, 'COMPONENT_CLASS', 'PREFIX', 'com.appboy.'), -- unverified (Appboy, before SDK 14)
  ('clevertap', 1, 'COMPONENT_CLASS', 'PREFIX', 'com.clevertap.android.sdk.'),
  ('clevertap', 2, 'ARCHIVE_PATH', 'PREFIX', 'com/clevertap/android/sdk/'),
  ('play-core', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.android.play.core.common.PlayCoreDialogWrapperActivity'),
  ('ml-kit', 1, 'COMPONENT_CLASS', 'EXACT', 'com.google.mlkit.common.internal.MlKitComponentDiscoveryService'),
  ('ml-kit', 2, 'COMPONENT_CLASS', 'EXACT', 'com.google.mlkit.common.internal.MlKitInitProvider'),
  ('google-maps', 1, 'ARCHIVE_PATH', 'EXACT', 'play-services-maps.properties'),
  ('tensorflow-lite', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libtensorflowlite_jni.so'),
  ('zxing-embedded', 1, 'COMPONENT_CLASS', 'EXACT', 'com.journeyapps.barcodescanner.CaptureActivity'),
  ('mupdf', 1, 'NATIVE_LIB_NAME', 'EXACT', 'libmupdf_java.so'),
  ('mupdf', 2, 'COMPONENT_CLASS', 'PREFIX', 'com.artifex.mupdf.');

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
