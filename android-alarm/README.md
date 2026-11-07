# 1560 알람 M — Android

팔천조 형님의 삼성 휴대폰에서 쓰기 위한 **실제 Android 설치 앱**입니다. 기존 웹 알람의 검정·노랑 화면과 동물 소리는 유지하면서, JavaScript 타이머를 Android `AlarmManager.setAlarmClock()` 예약으로 교체했습니다. 웹페이지를 띄우는 앱이 아닙니다.

- 패키지: `kr.palcheonjo.alarm1560`
- 버전: 1.0.0 (1), Android 8.0/API 26 이상, target/compile API 35
- 인터넷, 계정, 광고, 위치, 마이크 권한 없음
- 별도 `USAGE_ALARM` 오디오: 이어폰 미디어 음량과 분리
- 요일 반복, 특정 날짜, 한 번 알람, 14종 소리, 30초 점증, 진동
- 잠금 화면 해제·다시 알림, 최대 3회 다시 알림, 동시 알람 순서 재생
- 재부팅·시각·시간대 변경 시 OS 예약 복구, 직접 부팅 저장소 사용
- 백업/복원 및 이전 1560 웹 알람 JSON 가져오기. 복원된 알람은 확인 후 직접 켜야 함
- 최근 2분 이내 지연 예약 재복구, 최근 40개 알람 기록, 지난 일회성 알람은 자동으로 다음 날로 바꾸지 않고 표시

## 처음 설치할 때

1. 개인용 APK를 설치하고 앱을 엽니다.
2. **알람 음량 · 권한 확인**에서 알림과 잠금 화면 전체 표시를 허용합니다. Android 12에서는 정확한 알람 권한도 허용합니다.
3. 2분 후 시험 알람을 저장하고 화면을 잠급니다. 소리, 해제, 다시 알림을 확인합니다. 이어폰을 연결한 상태에서도 한 번 더 시험합니다.

기존 웹앱의 알람은 자동으로 옮겨지지 않습니다. 백업 파일이 있다면 더보기 → 백업 불러오기로 옮길 수 있습니다.

전원이 꺼져 있거나 앱을 강제 종료한 상태에서는 예약이 작동하지 않습니다. 방해 금지에서 알람을 차단한 경우에도 소리가 제한될 수 있습니다. 이 개인용 첫 버전은 실제 삼성 S25 FE/Android 17에서 설치 시험이 필요합니다. 삼성 기본 시계에 중요한 출근 알람을 함께 두고 시험한 뒤 사용하세요.

## 예약과 재생

`Engine`은 알람 설정, 예약 시각, 현재 재생과 대기 목록을 하나의 device-protected SharedPreferences 문서에 동기 커밋합니다. 각 예약은 알람 ID와 발생 시각을 포함한 고유 PendingIntent를 사용합니다. 오래된 전달과 중복 전달은 저장된 예약 시각 대조로 거절합니다.

`AlarmReceiver`는 발생을 먼저 기록하고 다음 반복을 예약한 뒤 `AlarmService`를 시작합니다. 서비스는 mediaPlayback 전경 서비스로 올라간 **후** 오디오 포커스와 `USAGE_ALARM` 재생을 시작합니다. `RingActivity`는 잠금 화면 위에 표시할 수 있습니다. 해제/다시 알림 동작도 발생 ID를 확인하므로 이전 알림의 동작이 다음 알람을 해제하지 않습니다.

부팅 수신기는 예약만 복구하며 부팅으로 미디어 전경 서비스를 시작하지 않습니다. 재생 중에만 최대 10분의 wake lock과 재생 제한을 사용합니다. 선택한 음원 오류 시 기본 종소리, 이후 시스템 알람음으로 대체합니다. 소리 디코더 준비는 비동기로 실행해 화면과 해제 버튼을 막지 않습니다.

## 빌드

Java 17 런타임, Python 3, zip, Android Platform 35, Android Build Tools 35.0.0, Eclipse ECJ 3.39.0이 필요합니다. Gradle/외부 Android 라이브러리는 사용하지 않습니다. `build.sh`가 음원을 준비하고 aapt2 → ECJ(Java 8 bytecode) → D8 → zipalign → apksigner 순으로 빌드합니다.

```bash
export ANDROID_PLATFORM_JAR=/path/to/android-35/android.jar
export ANDROID_BUILD_TOOLS=/path/to/build-tools/35.0.0
export ECJ_JAR=/path/to/ecj-3.39.0.jar
export SIGNING_STORE_FILE=/private/path/alarm1560.p12
export SIGNING_PASSWORD_FILE=/private/path/password.txt
./build.sh
```

결과: `build/1560-alarm-M-1.0.0.apk`. 서명 별칭은 `alarm1560`입니다. 개인 배포용 릴리스 키로 서명합니다. **키/비밀번호를 이 저장소에 올리지 마세요.** 업데이트 APK는 같은 패키지와 같은 키를 사용하고 versionCode를 올려야 합니다. 개인 서명 백업은 APK와 별도로 보관합니다.

`prepare_assets.py`는 저장소의 `audio/alarms/`를 읽으므로 이 디렉터리를 포함한 전체 저장소에서 실행합니다. 원본·라이선스·변환 정보는 해당 디렉터리와 APK 내부 출처 화면에 있습니다. 생성된 음원과 빌드 파일은 Git에서 제외됩니다.

## 검증

호스트 시간 계산 검증:

```bash
java -jar "$ECJ_JAR" -17 -d build/host-tests src/kr/palcheonjo/alarm1560/AlarmTime.java tests/AlarmTimeTest.java
java -cp build/host-tests kr.palcheonjo.alarm1560.AlarmTimeTest
```

일회성/과거 날짜, 요일 비트, 자정·연도 변경, 다시 알림, DST 간격을 포함한 15개 검증입니다.

Android 기기 시험은 **테스트용 에뮬레이터에서만** 실행합니다. 해당 앱의 테스트 데이터가 바뀝니다.

```bash
./tests/build-device-test.sh
adb install -r build/1560-alarm-M-1.0.0.apk
adb install -r build/device-test.apk
adb shell pm grant kr.palcheonjo.alarm1560 android.permission.POST_NOTIFICATIONS
adb shell appops set kr.palcheonjo.alarm1560 USE_FULL_SCREEN_INTENT allow
adb shell am instrument -w kr.palcheonjo.alarm1560.tests/kr.palcheonjo.alarm1560.tests.DeviceTest
```

기기 시험은 OS 예약·편집·취소, 화면 끈 상태의 실제 수신, 미디어 0에서 ALARM 오디오, 전경 서비스, 다시 알림·해제, 동시 발생 대기, 예약 복구, 놓친 알람, 웹 백업과 네이티브 화면을 검사합니다. 서명 검증은 빌드 마지막 단계에서 실행합니다. 최종 결과와 실제 휴대폰에서 남은 확인은 [CHECKS.md](CHECKS.md)에 기록했습니다.

Android 공식 문서: [알람 예약](https://developer.android.com/develop/background-work/services/alarms), [Android 17 백그라운드 오디오](https://developer.android.com/about/versions/17/changes/bg-audio), [전경 서비스 시작 제한](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start), [전체 화면 알림 권한](https://source.android.com/docs/core/permissions/fsi-limits).
