package kr.palcheonjo.alarm1560;

import android.content.*;
import android.util.Log;

public final class RestoreReceiver extends BroadcastReceiver {
  @Override
  public void onReceive(Context c, Intent i) {
    String a = i.getAction();
    if (a == null) return;
    boolean boot =
        Intent.ACTION_BOOT_COMPLETED.equals(a) || Intent.ACTION_LOCKED_BOOT_COMPLETED.equals(a);
    boolean supported =
        boot
            || Intent.ACTION_MY_PACKAGE_REPLACED.equals(a)
            || Intent.ACTION_TIME_CHANGED.equals(a)
            || Intent.ACTION_TIMEZONE_CHANGED.equals(a)
            || "android.app.action.SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED".equals(a);
    // Boot receivers only re-arm OS alarms: Android 15+ forbids boot-launched playback FGS.
    if (supported) Engine.restore(c, boot);
    if (Intent.ACTION_MY_PACKAGE_REPLACED.equals(a)
        || "android.app.action.SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED".equals(a)) {
      try {
        new CountdownTimers(c).restoreScheduling();
      } catch (RuntimeException error) {
        Log.w("Alarm1560", "Could not restore timers", error);
      }
    }
  }
}
