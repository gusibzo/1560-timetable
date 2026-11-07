package kr.palcheonjo.alarm1560;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.media.AudioManager;
import android.net.Uri;
import android.os.*;
import android.provider.Settings;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.json.*;

public final class MainActivity extends Activity {
  private LinearLayout body;
  private final Handler handler = new Handler(Looper.getMainLooper());
  private final BroadcastReceiver changes =
      new BroadcastReceiver() {
        public void onReceive(Context c, Intent i) {
          render();
        }
      };
  private final Runnable refresh =
      new Runnable() {
        public void run() {
          render();
          handler.postDelayed(this, 30_000);
        }
      };
  private boolean registered;

  @Override
  public void onCreate(Bundle b) {
    super.onCreate(b);
    setVolumeControlStream(AudioManager.STREAM_ALARM);
    LinearLayout root = Ui.column(this);
    Ui.screen(this, root);
    LinearLayout top = Ui.row(this);
    top.addView(Ui.bold(this, "1560 알람 M", 24, Ui.GOLD), new LinearLayout.LayoutParams(0, -2, 1));
    Button more = Ui.button(this, "더보기", false);
    top.addView(more);
    more.setOnClickListener(this::menu);
    root.addView(top);
    ScrollView scroll = new ScrollView(this);
    scroll.setFillViewport(true);
    body = Ui.column(this);
    scroll.addView(body);
    root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
    Button add = Ui.button(this, "＋ 알람 추가", true);
    root.addView(add, new LinearLayout.LayoutParams(-1, Ui.dp(this, 64)));
    add.setOnClickListener(v -> startActivity(new Intent(this, EditActivity.class)));
    AlarmService.channel(this);
  }

  @Override
  protected void onResume() {
    super.onResume();
    if (!registered) {
      if (Build.VERSION.SDK_INT >= 33)
        registerReceiver(changes, new IntentFilter(Engine.CHANGED), Context.RECEIVER_NOT_EXPORTED);
      else registerReceiver(changes, new IntentFilter(Engine.CHANGED));
      registered = true;
    }
    Engine.reconcile(this, false);
    refresh.run();
    if (Engine.active(this) != null) {
      startForegroundService(new Intent(this, AlarmService.class));
      startActivity(new Intent(this, RingActivity.class));
    }
  }

  @Override
  protected void onPause() {
    handler.removeCallbacksAndMessages(null);
    if (registered) {
      unregisterReceiver(changes);
      registered = false;
    }
    super.onPause();
  }

  private boolean notifications() {
    return getSystemService(NotificationManager.class).areNotificationsEnabled();
  }

  private boolean fullScreen() {
    return Build.VERSION.SDK_INT < 34
        || getSystemService(NotificationManager.class).canUseFullScreenIntent();
  }

  private void render() {
    if (body == null) return;
    body.removeAllViews();
    List<Alarm> list = Engine.alarms(this);
    long now = System.currentTimeMillis(), next = 0;
    int count = 0;
    for (Alarm a : list) {
      long at = Engine.scheduled(this, a.id);
      if (at > now) {
        count++;
        if (next == 0 || at < next) next = at;
      }
    }
    body.addView(Ui.bold(this, next == 0 ? "켜진 알람이 없습니다" : Ui.date(next), 30, Ui.WHITE));
    body.addView(
        Ui.text(
            this, next == 0 ? "아래에서 알람을 추가하거나 켜 주세요." : "다음 알람 · " + count + "개 예약됨", 17, Ui.GRAY));
    boolean ready = Engine.exactAllowed(this) && notifications() && fullScreen();
    LinearLayout status = Ui.card(this);
    status.addView(
        Ui.bold(this, ready ? "휴대폰 알람으로 예약합니다" : "알람 권한을 확인해 주세요", 18, ready ? Ui.WHITE : Ui.GOLD));
    String statusText = "화면이 꺼져도 예약 · 미디어와 별도 알람 음량";
    if (!Engine.exactAllowed(this)) statusText = "정확한 알람 권한이 없어 예약할 수 없습니다.";
    else if (!notifications()) statusText = "알림을 허용해야 잠금 화면과 해제 버튼을 볼 수 있어요.";
    else if (!fullScreen()) statusText = "잠금 화면 전체 표시 권한을 허용해 주세요.";
    status.addView(Ui.text(this, statusText, 15, Ui.GRAY));
    AudioManager am = getSystemService(AudioManager.class);
    if (am.getStreamVolume(AudioManager.STREAM_ALARM) == 0)
      status.addView(Ui.bold(this, "현재 휴대폰 알람 음량이 0입니다.", 16, Ui.GOLD));
    Button setup = Ui.button(this, "알람 음량 · 권한 확인", false);
    status.addView(setup);
    setup.setOnClickListener(v -> setup());
    Ui.addCard(body, status);
    for (Alarm a : list) {
      LinearLayout card = Ui.card(this), line = Ui.row(this);
      boolean on = a.enabled || a.snoozeUntil > now;
      TextView label =
          Ui.bold(this, a.label.isEmpty() ? "알람" : a.label, 18, on ? Ui.WHITE : Ui.GRAY);
      line.addView(label, new LinearLayout.LayoutParams(0, -2, 1));
      Switch sw = new Switch(this);
      sw.setContentDescription(Engine.title(a) + " 알람 켜기");
      sw.setChecked(on);
      line.addView(sw);
      card.addView(line);
      TextView time = Ui.bold(this, Ui.time(a), 50, on ? Ui.WHITE : Ui.GRAY);
      card.addView(time);
      card.addView(Ui.text(this, Ui.dayDescription(a), 17, Ui.GRAY));
      long at = Engine.scheduled(this, a.id);
      String detail =
          on
              ? (at > 0
                  ? (a.snoozeUntil > 0 ? "다시 알림 · " : "다음 · ") + Ui.date(at)
                  : "예약 권한을 확인해 주세요")
              : "알람 꺼짐";
      if (a.missedAt > 0) detail = "예약 시간 경과 · " + Ui.date(a.missedAt) + " · 다시 켜 주세요";
      card.addView(Ui.text(this, detail, 16, on || a.missedAt > 0 ? Ui.GOLD : Ui.GRAY));
      Button edit = Ui.button(this, "알람 수정", false);
      card.addView(edit);
      edit.setOnClickListener(v -> edit(a.id));
      time.setOnClickListener(v -> edit(a.id));
      sw.setOnCheckedChangeListener(
          (button, checked) -> {
            try {
              Alarm current = Engine.find(this, a.id);
              if (current == null) return;
              current.enabled = checked;
              current.snoozeUntil = 0;
              if (checked) {
                current.arm(System.currentTimeMillis());
                if (current.days == 0 && current.oneTimeAt == 0) {
                  current.date = "";
                  current.arm(System.currentTimeMillis());
                }
                if (current.days == 0) current.date = iso(current.oneTimeAt);
              }
              Engine.save(this, current);
              render();
            } catch (RuntimeException e) {
              Toast.makeText(this, e.getMessage(), Toast.LENGTH_LONG).show();
            }
          });
      Ui.addCard(body, card);
    }
    if (list.isEmpty()) {
      LinearLayout empty = Ui.card(this);
      empty.addView(Ui.bold(this, "새 알람을 만들어 주세요", 22, Ui.WHITE));
      empty.addView(
          Ui.text(
              this, "시간 · 반복 요일 · 동물 소리를 고를 수 있어요.\n이전 웹 알람 백업은 더보기에서 불러올 수 있습니다.", 17, Ui.GRAY));
      Ui.addCard(body, empty);
    }
  }

  static String iso(long at) {
    return new java.text.SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date(at));
  }

  private void edit(String id) {
    startActivity(new Intent(this, EditActivity.class).putExtra("id", id));
  }

  private void open(Intent i) {
    try {
      startActivity(i);
    } catch (ActivityNotFoundException e) {
      startActivity(
          new Intent(
              Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
              Uri.parse("package:" + getPackageName())));
    }
  }

  private void setup() {
    LinearLayout content = Ui.column(this);
    content.setPadding(Ui.dp(this, 20), Ui.dp(this, 10), Ui.dp(this, 20), Ui.dp(this, 10));
    content.addView(Ui.bold(this, "휴대폰 알람 음량", 19, Ui.WHITE));
    content.addView(Ui.text(this, "이어폰의 미디어 음량과 별개입니다.", 15, Ui.GRAY));
    AudioManager am = getSystemService(AudioManager.class);
    SeekBar volume = new SeekBar(this);
    volume.setMax(am.getStreamMaxVolume(AudioManager.STREAM_ALARM));
    volume.setProgress(am.getStreamVolume(AudioManager.STREAM_ALARM));
    content.addView(volume);
    volume.setOnSeekBarChangeListener(
        new SeekBar.OnSeekBarChangeListener() {
          public void onProgressChanged(SeekBar s, int p, boolean user) {
            if (user) am.setStreamVolume(AudioManager.STREAM_ALARM, p, 0);
          }

          public void onStartTrackingTouch(SeekBar s) {}

          public void onStopTrackingTouch(SeekBar s) {
            render();
          }
        });
    Button notice = Ui.button(this, notifications() ? "✓ 알림 허용됨" : "알림 허용하기", false);
    content.addView(notice);
    notice.setOnClickListener(
        v -> {
          if (Build.VERSION.SDK_INT >= 33
              && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                  != PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[] {Manifest.permission.POST_NOTIFICATIONS}, 10);
          else
            open(
                new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                    .putExtra(Settings.EXTRA_APP_PACKAGE, getPackageName()));
        });
    Button exact =
        Ui.button(this, Engine.exactAllowed(this) ? "✓ 정확한 알람 예약 가능" : "정확한 알람 허용하기", false);
    content.addView(exact);
    exact.setEnabled(!Engine.exactAllowed(this));
    exact.setOnClickListener(
        v -> {
          if (Build.VERSION.SDK_INT >= 31)
            open(
                new Intent(
                    Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,
                    Uri.parse("package:" + getPackageName())));
        });
    Button full = Ui.button(this, fullScreen() ? "✓ 잠금 화면 표시 가능" : "잠금 화면 표시 허용하기", false);
    content.addView(full);
    full.setOnClickListener(
        v -> {
          if (Build.VERSION.SDK_INT >= 34)
            open(
                new Intent(
                    Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT,
                    Uri.parse("package:" + getPackageName())));
        });
    content.addView(
        Ui.text(
            this,
            "방해 금지에서 알람을 차단하면 소리가 나지 않을 수 있어요. 휴대폰 전원이 꺼져 있거나 앱을 강제 종료한 상태에서는 울리지 않습니다.",
            14,
            Ui.GRAY));
    new AlertDialog.Builder(this)
        .setTitle("알람 준비")
        .setView(content)
        .setPositiveButton("닫기", (d, w) -> render())
        .show();
  }

  private void menu(View anchor) {
    PopupMenu p = new PopupMenu(this, anchor);
    String[] items = {"알람 음량 · 권한", "백업 저장", "백업 불러오기", "최근 알람 기록", "동물 소리 출처", "앱 정보"};
    for (int n = 0; n < items.length; n++) p.getMenu().add(0, n, n, items[n]);
    p.setOnMenuItemClickListener(
        item -> {
          switch (item.getItemId()) {
            case 0:
              setup();
              break;
            case 1:
              startActivityForResult(
                  new Intent(Intent.ACTION_CREATE_DOCUMENT)
                      .setType("application/json")
                      .addCategory(Intent.CATEGORY_OPENABLE)
                      .putExtra(Intent.EXTRA_TITLE, "1560-alarm-backup.json"),
                  41);
              break;
            case 2:
              Intent pick =
                  new Intent(Intent.ACTION_OPEN_DOCUMENT)
                      .setType("*/*")
                      .addCategory(Intent.CATEGORY_OPENABLE);
              startActivityForResult(pick, 42);
              break;
            case 3:
              logs();
              break;
            case 4:
              credits();
              break;
            case 5:
              new AlertDialog.Builder(this)
                  .setTitle("1560 알람 M · 1.0.0")
                  .setMessage(
                      "팔천조 형님을 위한 휴대폰 알람\n\n"
                          + "인터넷 · 계정 없이 휴대폰 안에서 작동합니다.\n"
                          + "알람 시간은 안드로이드 시스템에 예약합니다.\n"
                          + "처음 설치한 뒤 2분 후 알람을 만들어 화면을 잠그고 시험해 주세요.\n\n"
                          + "개인용 첫 설치 버전입니다. 실제 휴대폰 시험이 필요합니다.")
                  .setPositiveButton("확인", null)
                  .show();
              break;
          }
          return true;
        });
    p.show();
  }

  private void logs() {
    JSONArray logs = Engine.logs(this);
    StringBuilder s = new StringBuilder();
    for (int n = logs.length() - 1; n >= 0; n--) {
      JSONObject j = logs.optJSONObject(n);
      if (j != null)
        s.append(Ui.date(j.optLong("at"))).append("\n").append(j.optString("text")).append("\n\n");
    }
    new AlertDialog.Builder(this)
        .setTitle("최근 알람 기록")
        .setMessage(s.length() == 0 ? "아직 기록이 없습니다." : s.toString())
        .setPositiveButton("확인", null)
        .show();
  }

  private void credits() {
    try (InputStream in = getAssets().open("credits.txt")) {
      ByteArrayOutputStream out = new ByteArrayOutputStream();
      byte[] buf = new byte[4096];
      int n;
      while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
      TextView t = Ui.text(this, out.toString("UTF-8"), 15, Ui.WHITE);
      t.setPadding(24, 12, 24, 12);
      t.setTextIsSelectable(true);
      ScrollView scroll = new ScrollView(this);
      scroll.addView(t);
      new AlertDialog.Builder(this)
          .setTitle("동물 소리 출처")
          .setView(scroll)
          .setPositiveButton("확인", null)
          .show();
    } catch (IOException e) {
      Toast.makeText(this, "출처 파일을 열지 못했습니다", Toast.LENGTH_SHORT).show();
    }
  }

  @Override
  protected void onActivityResult(int request, int result, Intent i) {
    super.onActivityResult(request, result, i);
    if (result != RESULT_OK || i == null || i.getData() == null) return;
    Uri uri = i.getData();
    try {
      if (request == 41) {
        try (OutputStream out = getContentResolver().openOutputStream(uri)) {
          if (out == null) throw new IOException();
          out.write(Engine.exportData(this).getBytes(StandardCharsets.UTF_8));
        }
        Toast.makeText(this, "백업을 저장했습니다", Toast.LENGTH_SHORT).show();
      }
      if (request == 42) {
        String raw;
        try (InputStream in = getContentResolver().openInputStream(uri)) {
          if (in == null) throw new IOException();
          ByteArrayOutputStream out = new ByteArrayOutputStream();
          byte[] buf = new byte[4096];
          int n;
          while ((n = in.read(buf)) != -1) {
            out.write(buf, 0, n);
            if (out.size() > 1_000_000) throw new IOException("파일이 너무 큽니다");
          }
          raw = out.toString("UTF-8");
        }
        JSONObject j = new JSONObject(raw);
        JSONArray aa = j.optJSONArray("alarms");
        if (aa == null) throw new JSONException("알람 백업 파일이 아닙니다");
        new AlertDialog.Builder(this)
            .setTitle("알람 " + aa.length() + "개 불러오기")
            .setMessage("현재 알람 목록을 백업 내용으로 바꿉니다. 불러온 알람은 모두 꺼진 상태이므로 시간을 확인하고 켜 주세요.")
            .setNegativeButton("취소", null)
            .setPositiveButton(
                "불러오기",
                (d, w) -> {
                  try {
                    Engine.importData(this, raw);
                    render();
                  } catch (Exception e) {
                    Toast.makeText(this, "백업을 불러오지 못했습니다", Toast.LENGTH_LONG).show();
                  }
                })
            .show();
      }
    } catch (Exception e) {
      Toast.makeText(this, "파일을 처리하지 못했습니다: " + e.getMessage(), Toast.LENGTH_LONG).show();
    }
  }
}
