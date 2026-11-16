package kr.palcheonjo.trip1560;

import android.Manifest;
import android.app.Activity;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public final class TripActivity extends Activity {
  private static final ZoneId SEOUL = ZoneId.of("Asia/Seoul");
  private static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("M/d HH:mm");
  private long proposed;
  private int bus;
  private boolean leftArea;

  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    readLink(getIntent());
    if (state != null) {
      proposed = state.getLong("proposed");
      bus = state.getInt("bus");
      leftArea = state.getBoolean("left");
    }
  }

  @Override protected void onResume() {
    super.onResume();
    render();
  }

  @Override protected void onNewIntent(Intent intent) {
    super.onNewIntent(intent);
    setIntent(intent);
    readLink(intent);
    render();
  }

  @Override protected void onSaveInstanceState(Bundle state) {
    state.putLong("proposed", proposed);
    state.putInt("bus", bus);
    state.putBoolean("left", leftArea);
    super.onSaveInstanceState(state);
  }

  private void readLink(Intent intent) {
    Uri data = intent.getData();
    if (data == null || !"alarm1560trip".equals(data.getScheme()) || !"trip".equals(data.getHost())) return;
    try {
      long at = Long.parseLong(data.getQueryParameter("at"));
      long delta = at - System.currentTimeMillis();
      if (at <= 0 || delta < -8 * 3600000L || delta > 14 * 86400000L) return;
      proposed = at;
      String value = data.getQueryParameter("bus");
      bus = value != null && value.matches("([1-9]|1[0-3])") ? Integer.parseInt(value) : 0;
      leftArea = "1".equals(data.getQueryParameter("left"));
    } catch (IllegalArgumentException ignored) {}
  }

  private int dp(int size) { return Math.round(size * getResources().getDisplayMetrics().density); }

  private void button(LinearLayout group, String label, Runnable click) {
    Button button = new Button(this);
    button.setText(label);
    button.setMinHeight(dp(52));
    button.setOnClickListener(view -> click.run());
    group.addView(button, new LinearLayout.LayoutParams(-1, -2));
  }

  private void render() {
    SharedPreferences prefs = TripService.state(this);
    long active = prefs.getLong("at", 0);
    LinearLayout view = new LinearLayout(this);
    view.setOrientation(LinearLayout.VERTICAL);
    view.setPadding(dp(18), dp(36), dp(18), dp(20));
    TextView title = new TextView(this);
    title.setText("1560 운행 알림");
    title.setTextSize(26);
    view.addView(title);
    TextView detail = new TextView(this);
    detail.setTextSize(17);
    detail.setPadding(0, dp(12), 0, dp(12));
    long at = proposed != 0 ? proposed : active;
    String clock = at == 0 ? "출발 시간을 선택하세요." : "출발 " + DATE.format(Instant.ofEpochMilli(at).atZone(SEOUL));
    detail.setText((bus > 0 && proposed != 0 ? bus + "번 · " : "") + clock
        + (active != 0 ? "\n운행 알림이 켜져 있습니다." : "\n정확한 위치를 허용하면 경희대 사거리·정문 도착을 감지합니다."));
    view.addView(detail);
    button(view, "출발 시각 선택", this::pickTime);
    if (proposed != 0) button(view, active == 0 ? "운행 알림 시작" : "이 시간으로 변경", this::activate);
    if (active != 0) {
      if (active <= System.currentTimeMillis()) button(view, "도착 알림", () -> service(TripService.ARRIVE));
      button(view, "운행 알림 끄기", () -> service(TripService.STOP));
    }
    setContentView(view);
  }

  private void pickTime() {
    ZonedDateTime now = ZonedDateTime.now(SEOUL);
    new TimePickerDialog(this, (picker, hour, minute) -> {
      ZonedDateTime selected = now.withHour(hour).withMinute(minute).withSecond(0).withNano(0);
      proposed = (selected.isAfter(ZonedDateTime.now(SEOUL)) ? selected : selected.plusDays(1)).toInstant().toEpochMilli();
      bus = 0;
      leftArea = false;
      render();
    }, now.getHour(), now.getMinute(), true).show();
  }

  private void activate() {
    if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
      requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 1);
      return;
    }
    if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        && !getPreferences(MODE_PRIVATE).getBoolean("asked", false)) {
      getPreferences(MODE_PRIVATE).edit().putBoolean("asked", true).apply();
      requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 2);
      return;
    }
    try {
      TripService.reserve(this, proposed, leftArea);
      proposed = 0;
      render();
    } catch (RuntimeException error) {
      Toast.makeText(this, "운행 알림을 시작할 수 없습니다. 위치와 정확한 알람 권한을 확인해 주세요.", Toast.LENGTH_LONG).show();
    }
  }

  @Override public void onRequestPermissionsResult(int request, String[] permissions, int[] grants) {
    super.onRequestPermissionsResult(request, permissions, grants);
    if (request == 2 || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) activate();
    else Toast.makeText(this, "자동 도착에 정확한 위치 권한이 필요합니다.", Toast.LENGTH_LONG).show();
  }

  private void service(String action) {
    if (TripService.STOP.equals(action)) {
      TripService.cancelDeparture(this);
      TripService.state(this).edit().clear().commit();
      stopService(new Intent(this, TripService.class));
      render();
    } else startForegroundService(new Intent(this, TripService.class).setAction(action));
  }
}
