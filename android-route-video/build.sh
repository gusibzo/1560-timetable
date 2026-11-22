#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ANDROID_PLATFORM_JAR:?Set Android API 35 platform jar}"
: "${ANDROID_BUILD_TOOLS:?Set Android 35 build tools directory}"
: "${ECJ_JAR:?Set Eclipse Java compiler jar}"
: "${ROUTE_VIDEO_SIGNING_KEY:?Set signing keystore}"
: "${ROUTE_VIDEO_SIGNING_PASSWORD_FILE:?Set private signing password file}"
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT
mkdir -p "$out"/{classes,dex,res/drawable-xxxhdpi}
cp ../icons/icon-192.png "$out/res/drawable-xxxhdpi/route_video_icon.png"
"$ANDROID_BUILD_TOOLS/aapt2" compile --dir "$out/res" -o "$out/resources.zip"
"$ANDROID_BUILD_TOOLS/aapt2" link -o "$out/unsigned.apk" -I "$ANDROID_PLATFORM_JAR" \
  --manifest AndroidManifest.xml -A assets "$out/resources.zip"
find src -name '*.java' > "$out/sources.txt"
java -jar "$ECJ_JAR" -1.8 -classpath "$ANDROID_PLATFORM_JAR" -d "$out/classes" @"$out/sources.txt"
find "$out/classes" -name '*.class' > "$out/classes.txt"
java -cp "$ANDROID_BUILD_TOOLS/lib/d8.jar" com.android.tools.r8.D8 \
  --min-api 29 --lib "$ANDROID_PLATFORM_JAR" --output "$out/dex" @"$out/classes.txt"
(cd "$out/dex" && zip -q -j ../unsigned.apk classes.dex)
"$ANDROID_BUILD_TOOLS/zipalign" -f 4 "$out/unsigned.apk" "$out/aligned.apk"
mkdir -p ../downloads
apk=../downloads/1560-route-video-1.2.apk
"$ANDROID_BUILD_TOOLS/apksigner" sign --ks "$ROUTE_VIDEO_SIGNING_KEY" \
  --ks-pass "file:$ROUTE_VIDEO_SIGNING_PASSWORD_FILE" --v1-signing-enabled true \
  --v2-signing-enabled true --v3-signing-enabled true --v4-signing-enabled false \
  --out "$apk" "$out/aligned.apk"
"$ANDROID_BUILD_TOOLS/zipalign" -c 4 "$apk"
"$ANDROID_BUILD_TOOLS/apksigner" verify --verbose "$apk"
