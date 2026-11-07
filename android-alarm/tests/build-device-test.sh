#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/device-classes build/device-dex
"$ANDROID_BUILD_TOOLS/aapt2" link -o build/device-resources.apk -I "$ANDROID_PLATFORM_JAR" --manifest tests/device/AndroidManifest.xml
java -jar "$ECJ_JAR" -1.8 -warn:-deprecation -classpath "$ANDROID_PLATFORM_JAR:build/classes" -d build/device-classes tests/device/*.java
find build/device-classes -name '*.class' -not -path '*/.*' > build/device-classes.txt
java -cp "$ANDROID_BUILD_TOOLS/lib/d8.jar" com.android.tools.r8.D8 --min-api 26 --lib "$ANDROID_PLATFORM_JAR" --classpath build/classes --output build/device-dex @build/device-classes.txt
cp build/device-resources.apk build/device-unsigned.apk
(cd build/device-dex && zip -q -j ../device-unsigned.apk classes.dex)
"$ANDROID_BUILD_TOOLS/zipalign" -f -p 4 build/device-unsigned.apk build/device-aligned.apk
"$ANDROID_BUILD_TOOLS/apksigner" sign --ks "$SIGNING_STORE_FILE" --ks-key-alias alarm1560 --ks-pass "file:$SIGNING_PASSWORD_FILE" --out build/device-test.apk build/device-aligned.apk
