package kr.palcheonjo.alarm1560;

import android.content.*;

public final class AlarmReceiver extends BroadcastReceiver {
  @Override
  public void onReceive(Context c, Intent i) {
    if (!"RING".equals(i.getAction())) return;
    if (Engine.claim(c, i.getStringExtra("id"), i.getLongExtra("at", 0))) {
      try {
        c.startForegroundService(new Intent(c, AlarmService.class));
      } catch (RuntimeException e) {
        Engine.log(c, "재생 시작 실패 · 앱을 열어 권한을 확인해 주세요");
      }
    }
  }
}
