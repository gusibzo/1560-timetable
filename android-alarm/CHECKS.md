# 1.0.0 verification — 2026-11-08 KST

Installer: `1560-alarm-M-1.0.0.apk`

SHA-256: `a7254007a1422140ede28be6bcae5f4de0bff571892c226d23cf8b53e62bb2cc`

## Passed

- API 35 resources/manifest compilation, Java 8 bytecode, D8 conversion, zip alignment.
- APK v2 and v3 signature verification with the retained personal release key.
- APK ZIP CRC; 14 uncompressed audio assets; no INTERNET permission, instrumentation, keystore or password files in the production APK.
- 15 host checks for wall-clock scheduling: one-shot expiry, weekdays, dated alarms, midnight/year rollover, snooze and DST.
- **42 Android 35 instrumented checks**, using a software-emulated device:
  - persistent settings and actual OS AlarmClock registration;
  - edit, cancel, stale and duplicate occurrence rejection;
  - screen verified off before a scheduled occurrence;
  - active `USAGE_ALARM` playback with media volume zero and alarm volume unchanged;
  - playback service running in the foreground;
  - snooze scheduling/count, dismissal and simultaneous-alarm queue;
  - recently due occurrence recovery via a new OS exact delivery;
  - restore scheduling function, expired one-shot visibility and web backup import;
  - native main and editor activity creation.
- No AndroidRuntime crash in the final device run.
- Native main/editor window rendering and visual inspection passed. The slow software emulator's launcher/System UI produced ANR overlays; app windows were rendered directly for layout inspection rather than treating those overlays as app screenshots.

Foreground service promotion runs immediately on creation and on **every** start command, even if the occurrence has already been dismissed. Shutdown checks the latest start ID. This covers a delayed foreground-service start arriving after a rapid dismiss/new-alarm sequence. Media preparation and release do not block the main thread.

## Still requires the actual phone

Samsung S25 FE / Android 17 installation, full-screen appearance under the user's lock screen settings, physical speaker/headphone loudness/routing, and an actual reboot before a saved alarm. The restore function check above is not a physical reboot test.

Keep an important departure alarm in Samsung Clock until the phone's two-minute screen-lock test succeeds. The APK cannot ring while the phone is powered off or while the user has force-stopped it. DND can restrict alarm playback according to phone settings.

The private release keystore is stored separately from this repository. Updates must retain that key and package name and increase versionCode.
