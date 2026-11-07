package kr.palcheonjo.alarm1560;

import android.app.*;
import android.content.*;
import android.media.AudioManager;
import android.os.*;
import android.view.*;
import android.widget.*;
import org.json.JSONObject;

public final class RingActivity extends Activity {
  private final Handler handler = new Handler(Looper.getMainLooper());
  private String token = "";
  private TextView clock;
  private final Runnable refresh =
      new Runnable() {
        public void run() {
          render();
          handler.postDelayed(this, 1000);
        }
      };

  @Override
  public void onCreate(Bundle b) {
    super.onCreate(b);
    if (Build.VERSION.SDK_INT >= 27) {
      setShowWhenLocked(true);
      setTurnScreenOn(true);
    } else {
      getWindow()
          .addFlags(
              WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED
                  | WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON);
    }
    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    setVolumeControlStream(AudioManager.STREAM_ALARM);
  }

  @Override
  protected void onResume() {
    super.onResume();
    refresh.run();
  }

  @Override
  protected void onPause() {
    handler.removeCallbacksAndMessages(null);
    super.onPause();
  }

  private void render() {
    JSONObject active = Engine.active(this);
    if (active == null) {
      finish();
      return;
    }
    Alarm a = Alarm.from(active.optJSONObject("alarm"));
    String next = a.id + ":" + active.optLong("at");
    if (next.equals(token)) {
      if (clock != null)
        clock.setText(android.text.format.DateFormat.format("HH:mm", System.currentTimeMillis()));
      return;
    }
    token = next;
    LinearLayout root = Ui.column(this);
    root.setGravity(Gravity.CENTER);
    Ui.screen(this, root);
    root.addView(Ui.bold(this, "1560 알람 M", 22, Ui.GOLD));
    clock =
        Ui.bold(
            this,
            android.text.format.DateFormat.format("HH:mm", System.currentTimeMillis()).toString(),
            72,
            Ui.WHITE);
    root.addView(clock);
    root.addView(Ui.bold(this, Engine.title(a), 28, Ui.WHITE));
    root.addView(Ui.text(this, Sounds.NAMES[Sounds.index(a.sound)], 17, Ui.GRAY));
    Button stop = Ui.button(this, "알람 해제", true);
    LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, Ui.dp(this, 76));
    p.topMargin = Ui.dp(this, 34);
    root.addView(stop, p);
    stop.setOnClickListener(v -> act(AlarmService.STOP));
    if (a.snooze && a.snoozeLeft > 0) {
      Button snooze =
          Ui.button(this, a.snoozeMinutes + "분 뒤 다시 알림 (" + a.snoozeLeft + "회 남음)", false);
      root.addView(snooze, new LinearLayout.LayoutParams(-1, Ui.dp(this, 68)));
      snooze.setOnClickListener(v -> act(AlarmService.SNOOZE));
    }
    root.addView(Ui.text(this, "옆면 음량 버튼으로 알람 소리를 조절할 수 있어요.", 15, Ui.GRAY));
  }

  private void act(String name) {
    startService(new Intent(this, AlarmService.class).setAction(name).putExtra("token", token));
    token = "";
    handler.postDelayed(this::render, 200);
  }
}
