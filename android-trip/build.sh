#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ANDROID_PLATFORM_JAR:?Set Android API 35 platform jar}"
: "${ANDROID_BUILD_TOOLS:?Set Android 35 build tools directory}"
: "${ECJ_JAR:?Set Eclipse Java compiler jar}"
: "${TRIP_SIGNING_KEY:?Set signing keystore}"
: "${TRIP_SIGNING_PASSWORD_FILE:?Set private signing password file}"
out=build
mkdir -p "$out"/{gen,classes,dex,res/raw}
python3 prepare_audio.py "$out/res/raw"
"$ANDROID_BUILD_TOOLS/aapt2" compile --dir "$out/res" -o "$out/res.zip"
"$ANDROID_BUILD_TOOLS/aapt2" link -o "$out/unsigned.apk" -I "$ANDROID_PLATFORM_JAR" --manifest AndroidManifest.xml --java "$out/gen" "$out/res.zip"
find src "$out/gen" -name '*.java' > "$out/sources.txt"
java -jar "$ECJ_JAR" -1.8 -classpath "$ANDROID_PLATFORM_JAR" -d "$out/classes" @"$out/sources.txt"
find "$out/classes" -name '*.class' > "$out/classes.txt"
java -cp "$ANDROID_BUILD_TOOLS/lib/d8.jar" com.android.tools.r8.D8 --min-api 26 --lib "$ANDROID_PLATFORM_JAR" --output "$out/dex" @"$out/classes.txt"
(cd "$out/dex" && zip -q -j ../unsigned.apk classes.dex)
"$ANDROID_BUILD_TOOLS/zipalign" -f 4 "$out/unsigned.apk" "$out/aligned.apk"
"$ANDROID_BUILD_TOOLS/apksigner" sign --ks "$TRIP_SIGNING_KEY" --ks-pass "file:$TRIP_SIGNING_PASSWORD_FILE" --out "$out/1560-trip-alert-test.apk" "$out/aligned.apk"
"$ANDROID_BUILD_TOOLS/apksigner" verify --verbose "$out/1560-trip-alert-test.apk"
