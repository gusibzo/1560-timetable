# 1.0.2 verification — 2026-11-08 KST

Installer: `1560-alarm-M-1.0.2.apk`, versionCode 3.

SHA-256: `49ec19ad1da3a6a08d2101555f8d34f08611fc6e2a90a0a2f0569104efed7aaa`

Main screen rebuilt to match the supplied reference: black rounded cards, large time text, large round switches, top sort/delete/menu controls, centered yellow clock-plus button and bottom Alarm/More tabs. Live countdown labels remain. Cards open the editor. More contains the existing settings and backup features.

The two reference times (11:20 and 14:11) are added once, disabled, only when the corresponding time is absent. Existing alarm IDs and settings remain intact; deleting a reference alarm later does not re-add it.

Validation:
- 15 scheduling and 16 countdown host checks passed.
- 24 Android 29 UI checks passed: existing alarm preservation, disabled reference times, no duplication after relaunch, card-to-editor navigation, real switch state changes, live countdown ticks, bottom tabs, floating add and cancellation of a selected deletion without data loss.
- Final label alignment and compact banner received a separate native-window render pass on the final signed APK. Main, More and editor windows rendered successfully and were visually inspected.
- No AndroidRuntime crash in the final window test.
- Full API 35 build and APK v2/v3 signature verification passed. Certificate matches 1.0.1; package unchanged and versionCode increased for in-place updating.
- APK archive/audio integrity checked. Engine, AlarmReceiver, AlarmService and AlarmAudio remain unchanged.

These are software-emulator checks, not a physical Samsung S25 FE / Android 17 test. The Android 35 alarm/audio integration checks below belong to 1.0.0. A phone check after updating is still appropriate.

---

# 1.0.1 verification — 2026-11-08 KST

Installer: `1560-alarm-M-1.0.1.apk`, versionCode 2.

SHA-256: `02b9e9a7e280220b38e74849f3d1837656ef6d8d7fda0bf4e730f98cd656794d`

The main screen now shows remaining time above the alarm list and under each enabled alarm. Display labels update once per second while the screen is visible. Hours/minutes are used for long waits and minutes/seconds for waits under one hour. Reaching the target displays “알람 시간입니다”.

The one-second refresh only changes TextView text, so switches and scrolling are not rebuilt each second. The UI timer stops onPause and resumes with current wall time onResume. Android alarm delivery, audio playback, permissions and stored alarm data are unchanged.

Passed for this update:
- Full API 35 compilation, D8 conversion, alignment and APK v2/v3 signature verification.
- Signing certificate matches the previously delivered 1.0.0 APK; package unchanged and versionCode increased from 1 to 2 for an in-place update.
- 15 existing wall-clock scheduling checks and 16 countdown checks, including millisecond rounding, expired targets and second/minute/hour/day boundaries.
- Archive CRC and 14 uncompressed audio assets.
- Source review confirms Engine, AlarmReceiver, AlarmService and AlarmAudio are unchanged.

The new countdown UI has not been run on a device in this update. The Android 35 integration and window-render checks below belong to 1.0.0 and were not repeated for this display-only change. A two-minute phone check after updating remains appropriate.

---

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
