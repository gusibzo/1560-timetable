package kr.palcheonjo.alarm1560;

import android.content.*;
import java.util.List;

/** Add the user's two reference times once, disabled, without replacing saved alarms. */
final class ReferenceAlarms {
  private ReferenceAlarms() {}

  static void ensure(Context context) {
    SharedPreferences prefs =
        context
            .createDeviceProtectedStorageContext()
            .getSharedPreferences("photo-appearance-v1", Context.MODE_PRIVATE);
    if (prefs.getBoolean("reference-times-added", false)) return;
    int[] minutes = {11 * 60 + 20, 14 * 60 + 11};
    for (int value : minutes) {
      List<Alarm> existing = Engine.alarms(context);
      boolean present = false;
      for (Alarm a : existing)
        if (a.hour * 60 + a.minute == value) {
          present = true;
          break;
        }
      if (!present) {
        Alarm a = new Alarm();
        a.hour = value / 60;
        a.minute = value % 60;
        a.enabled = false;
        a.date = MainActivity.iso(System.currentTimeMillis());
        Engine.save(context, a);
      }
    }
    if (!prefs.edit().putBoolean("reference-times-added", true).commit())
      throw new IllegalStateException("화면 설정을 저장하지 못했습니다");
  }
}
