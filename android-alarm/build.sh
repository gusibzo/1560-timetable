#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ANDROID_PLATFORM_JAR:?Set ANDROID_PLATFORM_JAR to API 35 android.jar}"
: "${ANDROID_BUILD_TOOLS:?Set ANDROID_BUILD_TOOLS to Android build-tools 35 directory}"
: "${ECJ_JAR:?Set ECJ_JAR to Eclipse ECJ 3.39.0 jar}"
: "${SIGNING_STORE_FILE:?Set SIGNING_STORE_FILE to your private release keystore}"
: "${SIGNING_PASSWORD_FILE:?Set SIGNING_PASSWORD_FILE to a private password file}"
python3 prepare_assets.py
mkdir -p build/gen build/classes build/dex
rm -rf build/gen/* build/classes/* build/dex/*
"$ANDROID_BUILD_TOOLS/aapt2" compile --dir res -o build/resources.zip
"$ANDROID_BUILD_TOOLS/aapt2" link -o build/resources.apk -I "$ANDROID_PLATFORM_JAR" --manifest AndroidManifest.xml --java build/gen -A assets -0 wav -0 mp3 build/resources.zip
find src build/gen -name '*.java' -not -path '*/.*' > build/sources.txt
java -jar "$ECJ_JAR" -1.8 -warn:+unusedImport,-deprecation -classpath "$ANDROID_PLATFORM_JAR" -d build/classes @build/sources.txt
find build/classes -name '*.class' -not -path '*/.*' > build/classes.txt
java -cp "$ANDROID_BUILD_TOOLS/lib/d8.jar" com.android.tools.r8.D8 --min-api 26 --lib "$ANDROID_PLATFORM_JAR" --output build/dex @build/classes.txt
cp build/resources.apk build/unsigned.apk
(cd build/dex && zip -q -j ../unsigned.apk classes*.dex)
"$ANDROID_BUILD_TOOLS/zipalign" -f -p 4 build/unsigned.apk build/aligned.apk
apk=build/1560-alarm-M-1.0.5.apk
"$ANDROID_BUILD_TOOLS/apksigner" sign --ks "$SIGNING_STORE_FILE" --ks-key-alias alarm1560 --ks-pass "file:$SIGNING_PASSWORD_FILE" --out "$apk" build/aligned.apk
"$ANDROID_BUILD_TOOLS/apksigner" verify --verbose "$apk"
"$ANDROID_BUILD_TOOLS/aapt2" dump badging "$apk"
sha256sum "$apk"
