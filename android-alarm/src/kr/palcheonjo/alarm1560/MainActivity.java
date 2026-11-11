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
  private LinearLayout body, alarmTab, moreTab;
  private ScrollView scroll;
  private FrameLayout floating;
  private TextView back;
  private View sortButton, deleteButton;
  private AlarmArt alarmTabArt, moreTabArt, floatingArt;
  private TextView alarmTabLabel, moreTabLabel;
  private SharedPreferences appearance;
  private boolean morePage, selecting, registered;
  private final Set<String> selected = new HashSet<>();
  private final List<RemainingLabel> remainingLabels = new ArrayList<>();
  private final Handler handler = new Handler(Looper.getMainLooper());
  private static final int NAV_HEIGHT = 98;

  private static final class RemainingLabel {
    final TextView view;
    final long at;

    RemainingLabel(TextView view, long at) {
      this.view = view;
      this.at = at;
    }
  }

  private TextView remainingLabel(long at, int size, int color) {
    TextView view =
        Ui.bold(this, RemainingTime.format(System.currentTimeMillis(), at), size, color);
    remainingLabels.add(new RemainingLabel(view, at));
    return view;
  }

  private final BroadcastReceiver changes =
      new BroadcastReceiver() {
        @Override
        public void onReceive(Context c, Intent intent) {
          render();
        }
      };
  private final Runnable refresh =
      new Runnable() {
        @Override
        public void run() {
          long now = System.currentTimeMillis();
          for (RemainingLabel label : remainingLabels) {
            String text = RemainingTime.format(now, label.at);
            if (!text.contentEquals(label.view.getText())) label.view.setText(text);
          }
          handler.postDelayed(this, 1000 - System.currentTimeMillis() % 1000);
        }
      };

  @Override
  public void onCreate(Bundle state) {
    super.onCreate(state);
    setVolumeControlStream(AudioManager.STREAM_ALARM);
    appearance =
        createDeviceProtectedStorageContext()
            .getSharedPreferences("photo-appearance-v1", MODE_PRIVATE);
    ReferenceAlarms.ensure(this);
    FrameLayout root = new FrameLayout(this);
    Ui.screen(this, root, 0);
    LinearLayout column = Ui.column(this);
    root.addView(column, new FrameLayout.LayoutParams(-1, -1));
    LinearLayout toolbar = Ui.row(this);
    toolbar.setPadding(Ui.dp(this, 18), 0, Ui.dp(this, 10), 0);
    back = Ui.text(this, "‹ 1560", 18, Ui.GRAY);
    back.setGravity(Gravity.CENTER_VERTICAL);
    back.setContentDescription("1560 시간표 열기");
    toolbar.addView(back, new LinearLayout.LayoutParams(0, -1, 1));
    back.setOnClickListener(
        v -> {
          if (selecting) {
            selecting = false;
            selected.clear();
            render();
          } else if (morePage) {
            morePage = false;
            render();
          } else openTimetable();
        });
    sortButton = iconButton("sort", Ui.GOLD, "알람 정렬", v -> sortMenu(v));
    deleteButton = iconButton("trash", Ui.GOLD, "알람 삭제", v -> beginSelection());
    toolbar.addView(sortButton, new LinearLayout.LayoutParams(Ui.dp(this, 48), Ui.dp(this, 48)));
    toolbar.addView(deleteButton, new LinearLayout.LayoutParams(Ui.dp(this, 48), Ui.dp(this, 48)));
    toolbar.addView(
        iconButton("more", Ui.GOLD, "알람 메뉴", this::menu),
        new LinearLayout.LayoutParams(Ui.dp(this, 48), Ui.dp(this, 48)));
    column.addView(toolbar, new LinearLayout.LayoutParams(-1, Ui.dp(this, 64)));
    scroll = new ScrollView(this);
    scroll.setFillViewport(true);
    scroll.setClipToPadding(false);
    body = Ui.column(this);
    body.setPadding(Ui.dp(this, 13), Ui.dp(this, 10), Ui.dp(this, 13), Ui.dp(this, 100));
    scroll.addView(body);
    column.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
    LinearLayout navigation = Ui.row(this);
    navigation.setGravity(Gravity.CENTER);
    android.graphics.drawable.GradientDrawable navShape = Ui.shape(0xff202022, 0);
    float radius = Ui.dp(this, 28);
    navShape.setCornerRadii(new float[] {radius, radius, radius, radius, 0, 0, 0, 0});
    navigation.setBackground(navShape);
    alarmTab = Ui.column(this);
    alarmTab.setGravity(Gravity.CENTER);
    alarmTab.setTag("main-tab-alarms");
    alarmTab.setContentDescription("알람 목록");
    alarmTabArt = new AlarmArt(this, "alarm-filled", Ui.GOLD);
    alarmTab.addView(alarmTabArt, new LinearLayout.LayoutParams(Ui.dp(this, 34), Ui.dp(this, 34)));
    alarmTabLabel = Ui.bold(this, "알람", 18, Ui.GOLD);
    alarmTabLabel.setGravity(Gravity.CENTER);
    alarmTab.addView(alarmTabLabel);
    moreTab = Ui.column(this);
    moreTab.setGravity(Gravity.CENTER);
    moreTab.setTag("main-tab-more");
    moreTab.setContentDescription("더보기");
    moreTabArt = new AlarmArt(this, "more-horizontal", Ui.GRAY);
    moreTab.addView(moreTabArt, new LinearLayout.LayoutParams(Ui.dp(this, 34), Ui.dp(this, 34)));
    moreTabLabel = Ui.bold(this, "더보기", 18, Ui.GRAY);
    moreTabLabel.setGravity(Gravity.CENTER);
    moreTab.addView(moreTabLabel);
    navigation.addView(alarmTab, new LinearLayout.LayoutParams(0, -1, 1));
    navigation.addView(moreTab, new LinearLayout.LayoutParams(0, -1, 1));
    column.addView(navigation, new LinearLayout.LayoutParams(-1, Ui.dp(this, NAV_HEIGHT)));
    alarmTab.setOnClickListener(
        v -> {
          morePage = false;
          selecting = false;
          selected.clear();
          render();
          scroll.smoothScrollTo(0, 0);
        });
    moreTab.setOnClickListener(
        v -> {
          morePage = true;
          selecting = false;
          selected.clear();
          render();
          scroll.smoothScrollTo(0, 0);
        });
    floating = new FrameLayout(this);
    floating.setBackground(Ui.shape(Ui.GOLD, Ui.dp(this, 100)));
    floating.setElevation(Ui.dp(this, 7));
    floating.setTag("main-add");
    floating.setContentDescription("알람 추가");
    floating.setFocusable(true);
    floatingArt = new AlarmArt(this, "clock-plus", android.graphics.Color.BLACK);
    FrameLayout.LayoutParams art =
        new FrameLayout.LayoutParams(Ui.dp(this, 42), Ui.dp(this, 42), Gravity.CENTER);
    floating.addView(floatingArt, art);
    FrameLayout.LayoutParams add =
        new FrameLayout.LayoutParams(
            Ui.dp(this, 76), Ui.dp(this, 76), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
    add.bottomMargin = Ui.dp(this, NAV_HEIGHT + 16);
    root.addView(floating, add);
    floating.setOnClickListener(
        v -> {
          if (selecting) confirmSelection();
          else startActivity(new Intent(this, EditActivity.class));
        });
    AlarmService.channel(this);
  }

  private View iconButton(
      String kind, int color, String description, View.OnClickListener listener) {
    AlarmArt icon = new AlarmArt(this, kind, color);
    icon.setPadding(Ui.dp(this, 8), Ui.dp(this, 8), Ui.dp(this, 8), Ui.dp(this, 8));
    icon.setContentDescription(description);
    icon.setFocusable(true);
    icon.setOnClickListener(listener);
    return icon;
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
    render();
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

  @Override
  public void onBackPressed() {
    if (selecting) {
      selecting = false;
      selected.clear();
      render();
    } else if (morePage) {
      morePage = false;
      render();
    } else super.onBackPressed();
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
    remainingLabels.clear();
    body.removeAllViews();
    alarmTabArt.tint(morePage ? Ui.GRAY : Ui.GOLD);
    alarmTabLabel.setTextColor(morePage ? Ui.GRAY : Ui.GOLD);
    moreTabArt.tint(morePage ? Ui.GOLD : Ui.GRAY);
    moreTabLabel.setTextColor(morePage ? Ui.GOLD : Ui.GRAY);
    back.setText(selecting ? "‹ 취소" : morePage ? "‹ 알람" : "‹ 1560");
    back.setContentDescription(selecting ? "선택 취소" : morePage ? "알람 목록으로" : "1560 시간표 열기");
    sortButton.setVisibility(morePage || selecting ? View.GONE : View.VISIBLE);
    deleteButton.setVisibility(morePage ? View.GONE : View.VISIBLE);
    floating.setVisibility(morePage ? View.GONE : View.VISIBLE);
    floating.setAlpha(selecting && selected.isEmpty() ? 0.5f : 1f);
    floating.removeAllViews();
    floatingArt =
        new AlarmArt(this, selecting ? "trash" : "clock-plus", android.graphics.Color.BLACK);
    floating.addView(
        floatingArt,
        new FrameLayout.LayoutParams(Ui.dp(this, 42), Ui.dp(this, 42), Gravity.CENTER));
    floating.setContentDescription(selecting ? "선택한 알람 삭제" : "알람 추가");
    if (morePage) {
      renderMore();
      return;
    }
    List<Alarm> alarms = Engine.alarms(this);
    long now = System.currentTimeMillis(), next = 0;
    for (Alarm a : alarms) {
      long at = Engine.scheduled(this, a.id);
      if (at > now && (next == 0 || at < next)) next = at;
    }
    LinearLayout summary = Ui.row(this);
    summary.setPadding(Ui.dp(this, 8), Ui.dp(this, 26), Ui.dp(this, 8), Ui.dp(this, 18));
    summary.addView(
        new AlarmArt(this, selecting ? "trash" : "clock", Ui.GRAY),
        new LinearLayout.LayoutParams(Ui.dp(this, 38), Ui.dp(this, 38)));
    LinearLayout heading = Ui.column(this);
    heading.setPadding(Ui.dp(this, 12), 0, 0, 0);
    TextView title =
        selecting
            ? Ui.bold(this, selected.size() + "개 선택", 28, Ui.WHITE)
            : next == 0 ? Ui.bold(this, "알람 꺼짐", 28, Ui.WHITE) : remainingLabel(next, 28, Ui.WHITE);
    title.setTag("summary-countdown");
    heading.addView(title);
    heading.addView(
        Ui.text(
            this,
            selecting ? "삭제할 알람을 선택해 주세요" : next == 0 ? "켜진 알람이 없습니다" : "다음 알람 · " + Ui.date(next),
            15,
            Ui.GRAY));
    summary.addView(heading, new LinearLayout.LayoutParams(0, -2, 1));
    body.addView(summary);
    statusCard();
    sortAlarms(alarms, now);
    for (Alarm a : alarms) alarmCard(a, now);
    if (alarms.isEmpty()) body.addView(Ui.text(this, "아래 ＋ 버튼을 눌러 알람을 추가해 주세요.", 18, Ui.GRAY));
  }

  private void statusCard() {
    boolean ready = Engine.exactAllowed(this) && notifications() && fullScreen();
    String detail = "화면이 꺼져도 예약 · 별도 알람 음량";
    if (!Engine.exactAllowed(this)) detail = "정확한 알람 권한을 허용해 주세요.";
    else if (!notifications()) detail = "알림을 허용해 주세요.";
    else if (!fullScreen()) detail = "잠금 화면 전체 표시를 허용해 주세요.";
    else if (getSystemService(AudioManager.class).getStreamVolume(AudioManager.STREAM_ALARM) == 0) {
      ready = false;
      detail = "휴대폰 알람 음량이 0입니다. 눌러서 조절하세요.";
    }
    LinearLayout card = Ui.row(this);
    card.setPadding(Ui.dp(this, 14), Ui.dp(this, 10), Ui.dp(this, 8), Ui.dp(this, 10));
    card.setBackground(cardShape());
    card.addView(
        new AlarmArt(this, "phone", Ui.GRAY),
        new LinearLayout.LayoutParams(Ui.dp(this, 18), Ui.dp(this, 26)));
    LinearLayout text = Ui.column(this);
    text.setPadding(Ui.dp(this, 10), 0, 0, 0);
    TextView statusTitle =
        Ui.bold(
            this, ready ? "휴대폰 알람으로 예약합니다" : "알람 권한 · 음량을 확인해 주세요", 16, ready ? Ui.WHITE : Ui.GOLD);
    statusTitle.setPadding(0, Ui.dp(this, 1), 0, Ui.dp(this, 1));
    TextView statusDetail = Ui.text(this, detail, 14, Ui.GRAY);
    statusDetail.setPadding(0, Ui.dp(this, 1), 0, Ui.dp(this, 1));
    text.addView(statusTitle);
    text.addView(statusDetail);
    card.addView(text, new LinearLayout.LayoutParams(0, -2, 1));
    card.addView(
        new AlarmArt(this, "chevron", Ui.GRAY),
        new LinearLayout.LayoutParams(Ui.dp(this, 22), Ui.dp(this, 26)));
    card.setContentDescription("알람 음량 및 권한 설정");
    card.setFocusable(true);
    card.setOnClickListener(v -> setup());
    Ui.addCard(body, card);
  }

  private android.graphics.drawable.GradientDrawable cardShape() {
    android.graphics.drawable.GradientDrawable shape = Ui.shape(Ui.CARD, Ui.dp(this, 24));
    shape.setStroke(Ui.dp(this, 1), 0xff303033);
    return shape;
  }

  private void alarmCard(Alarm a, long now) {
    boolean on = a.enabled || a.snoozeUntil > now;
    long at = Engine.scheduled(this, a.id);
    FrameLayout frame = new FrameLayout(this);
    frame.setBackground(cardShape());
    frame.setMinimumHeight(Ui.dp(this, 184));
    frame.setTag("alarm-card-" + a.id);
    LinearLayout content = Ui.column(this);
    content.setPadding(Ui.dp(this, 22), Ui.dp(this, 20), Ui.dp(this, 22), Ui.dp(this, 17));
    if (!a.label.isEmpty()) {
      LinearLayout label = Ui.row(this);
      label.setPadding(0, 0, Ui.dp(this, 75), 0);
      label.addView(
          new AlarmArt(this, "tag", on ? Ui.WHITE : Ui.GRAY),
          new LinearLayout.LayoutParams(Ui.dp(this, 17), Ui.dp(this, 20)));
      TextView name = Ui.bold(this, a.label, 17, on ? Ui.WHITE : Ui.GRAY);
      name.setPadding(Ui.dp(this, 6), 0, 0, 0);
      name.setSingleLine(true);
      name.setEllipsize(android.text.TextUtils.TruncateAt.END);
      label.addView(name, new LinearLayout.LayoutParams(0, -2, 1));
      content.addView(label);
    } else {
      Space spacer = new Space(this);
      content.addView(spacer, new LinearLayout.LayoutParams(1, Ui.dp(this, 15)));
    }
    TextView time = Ui.bold(this, Ui.time(a), 56, on ? Ui.WHITE : 0xff89898e);
    time.setPadding(0, Ui.dp(this, 4), 0, Ui.dp(this, 4));
    time.setIncludeFontPadding(false);
    time.setTag("alarm-time-" + a.id);
    content.addView(time);
    content.addView(Ui.bold(this, dayLabel(a), 18, Ui.GRAY));
    TextView status;
    if (on && at > 0) status = remainingLabel(at, 18, Ui.GOLD);
    else
      status =
          Ui.bold(
              this,
              on ? "예약 권한을 확인해 주세요" : a.missedAt > 0 ? "예약 시간 경과 · 다시 켜 주세요" : "알람 꺼짐",
              16,
              on || a.missedAt > 0 ? Ui.GOLD : Ui.GRAY);
    status.setPadding(0, Ui.dp(this, 3), Ui.dp(this, 38), Ui.dp(this, 3));
    content.addView(status);
    frame.addView(content, new FrameLayout.LayoutParams(-1, -2));
    if (selecting) {
      CheckBox check = new CheckBox(this);
      check.setChecked(selected.contains(a.id));
      check.setContentDescription(Engine.title(a) + " 선택");
      check.setOnCheckedChangeListener(
          (b, value) -> {
            if (value) selected.add(a.id);
            else selected.remove(a.id);
            render();
          });
      FrameLayout.LayoutParams p =
          new FrameLayout.LayoutParams(
              Ui.dp(this, 52), Ui.dp(this, 44), Gravity.TOP | Gravity.RIGHT);
      p.setMargins(0, Ui.dp(this, 18), Ui.dp(this, 15), 0);
      frame.addView(check, p);
    } else {
      AlarmToggle toggle = new AlarmToggle(this, on);
      toggle.setTag("alarm-toggle-" + a.id);
      toggle.setContentDescription(Engine.title(a) + (on ? " 알람 끄기" : " 알람 켜기"));
      toggle.setOnClickListener(v -> toggle(a.id));
      FrameLayout.LayoutParams p =
          new FrameLayout.LayoutParams(
              Ui.dp(this, 70), Ui.dp(this, 42), Gravity.TOP | Gravity.RIGHT);
      p.setMargins(0, Ui.dp(this, 22), Ui.dp(this, 22), 0);
      frame.addView(toggle, p);
      View menu = iconButton("more", Ui.GRAY, Engine.title(a) + " 알람 메뉴", v -> alarmMenu(v, a));
      FrameLayout.LayoutParams m =
          new FrameLayout.LayoutParams(
              Ui.dp(this, 46), Ui.dp(this, 46), Gravity.BOTTOM | Gravity.RIGHT);
      m.setMargins(0, 0, Ui.dp(this, 10), Ui.dp(this, 8));
      frame.addView(menu, m);
    }
    frame.setContentDescription(Engine.title(a) + (selecting ? " 선택" : " 수정"));
    frame.setFocusable(true);
    frame.setOnClickListener(
        v -> {
          if (selecting) {
            if (!selected.add(a.id)) selected.remove(a.id);
            render();
          } else edit(a.id);
        });
    Ui.addCard(body, frame);
  }

  private String dayLabel(Alarm a) {
    if (a.days != 0) return Ui.dayDescription(a);
    String today = iso(System.currentTimeMillis());
    if (a.date.isEmpty() || a.date.equals(today)) return "오늘";
    Calendar tomorrow = Calendar.getInstance();
    tomorrow.add(Calendar.DATE, 1);
    if (a.date.equals(iso(tomorrow.getTimeInMillis()))) return "내일";
    return a.date;
  }

  private void toggle(String id) {
    try {
      Alarm a = Engine.find(this, id);
      if (a == null) return;
      boolean on = a.enabled || a.snoozeUntil > System.currentTimeMillis();
      a.enabled = !on;
      a.snoozeUntil = 0;
      if (a.enabled) {
        a.arm(System.currentTimeMillis());
        if (a.days == 0 && a.oneTimeAt == 0) {
          a.date = "";
          a.arm(System.currentTimeMillis());
        }
        if (a.days == 0) a.date = iso(a.oneTimeAt);
      }
      Engine.save(this, a);
      render();
    } catch (RuntimeException error) {
      Toast.makeText(this, "알람을 저장하지 못했습니다", Toast.LENGTH_LONG).show();
      render();
    }
  }

  private long displayTarget(Alarm a, long now) {
    long scheduled = Engine.scheduled(this, a.id);
    if (scheduled > now) return scheduled;
    long next =
        AlarmTime.next(
            now, a.hour, a.minute, a.days, a.days == 0 ? a.date : "", TimeZone.getDefault());
    return next == 0 ? Long.MAX_VALUE : next;
  }

  private void sortAlarms(List<Alarm> list, long now) {
    int mode = appearance.getInt("sort", 0);
    if (mode == 3) return;
    Map<String, Long> targets = new HashMap<>();
    if (mode == 0) for (Alarm a : list) targets.put(a.id, displayTarget(a, now));
    Collections.sort(
        list,
        (a, b) -> {
          if (mode == 0) {
            int order = Long.compare(targets.get(a.id), targets.get(b.id));
            if (order != 0) return order;
          }
          int order = Integer.compare(a.hour * 60 + a.minute, b.hour * 60 + b.minute);
          return mode == 2 ? -order : order;
        });
  }

  private void sortMenu(View anchor) {
    PopupMenu menu = new PopupMenu(this, anchor);
    String[] names = {"가까운 알람 순", "이른 시간 순", "늦은 시간 순", "추가한 순"};
    for (int i = 0; i < names.length; i++)
      menu.getMenu()
          .add(0, i, i, names[i])
          .setCheckable(true)
          .setChecked(appearance.getInt("sort", 0) == i);
    menu.getMenu().setGroupCheckable(0, true, true);
    menu.setOnMenuItemClickListener(
        item -> {
          appearance.edit().putInt("sort", item.getItemId()).apply();
          render();
          return true;
        });
    menu.show();
  }

  private void alarmMenu(View anchor, Alarm a) {
    PopupMenu menu = new PopupMenu(this, anchor);
    menu.getMenu().add(0, 0, 0, "알람 수정");
    menu.getMenu().add(0, 1, 1, "삭제");
    menu.setOnMenuItemClickListener(
        item -> {
          if (item.getItemId() == 0) edit(a.id);
          else confirmDelete(Collections.singleton(a.id));
          return true;
        });
    menu.show();
  }

  private void beginSelection() {
    if (Engine.alarms(this).isEmpty()) {
      Toast.makeText(this, "삭제할 알람이 없습니다", Toast.LENGTH_SHORT).show();
      return;
    }
    selecting = !selecting;
    selected.clear();
    render();
  }

  private void confirmSelection() {
    if (selected.isEmpty()) {
      Toast.makeText(this, "삭제할 알람을 선택해 주세요", Toast.LENGTH_SHORT).show();
      return;
    }
    confirmDelete(new HashSet<>(selected));
  }

  private void confirmDelete(Set<String> ids) {
    new AlertDialog.Builder(this)
        .setTitle("알람 " + ids.size() + "개를 삭제할까요?")
        .setMessage("선택한 알람과 해당 예약을 삭제합니다.")
        .setNegativeButton("취소", null)
        .setPositiveButton(
            "삭제",
            (dialog, which) -> {
              for (String id : ids) Engine.remove(this, id);
              selected.clear();
              selecting = false;
              render();
            })
        .show();
  }

  private void renderMore() {
    TextView title = Ui.bold(this, "더보기", 28, Ui.WHITE);
    title.setPadding(Ui.dp(this, 8), Ui.dp(this, 24), 0, Ui.dp(this, 20));
    body.addView(title);
    String[] names = {"알람 음량 · 권한 확인", "백업 저장", "백업 불러오기", "최근 알람 기록", "동물 소리 출처", "앱 정보"};
    for (int n = 0; n < names.length; n++) {
      final int id = n;
      LinearLayout row = Ui.row(this);
      row.setPadding(Ui.dp(this, 18), Ui.dp(this, 14), Ui.dp(this, 12), Ui.dp(this, 14));
      row.setBackground(cardShape());
      row.addView(Ui.bold(this, names[n], 18, Ui.WHITE), new LinearLayout.LayoutParams(0, -2, 1));
      row.addView(
          new AlarmArt(this, "chevron", Ui.GRAY),
          new LinearLayout.LayoutParams(Ui.dp(this, 24), Ui.dp(this, 28)));
      row.setFocusable(true);
      row.setContentDescription(names[n]);
      row.setOnClickListener(v -> moreAction(id));
      Ui.addCard(body, row);
    }
  }

  private void openTimetable() {
    try {
      startActivity(
          new Intent(Intent.ACTION_VIEW, Uri.parse("https://gusibzo.github.io/1560-timetable/")));
    } catch (ActivityNotFoundException error) {
      Toast.makeText(this, "시간표를 열 수 없습니다", Toast.LENGTH_SHORT).show();
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
    PopupMenu menu = new PopupMenu(this, anchor);
    String[] names = {"알람 음량 · 권한", "백업 저장", "백업 불러오기", "최근 알람 기록", "동물 소리 출처", "앱 정보"};
    for (int n = 0; n < names.length; n++) menu.getMenu().add(0, n, n, names[n]);
    menu.setOnMenuItemClickListener(
        item -> {
          moreAction(item.getItemId());
          return true;
        });
    menu.show();
  }

  private void moreAction(int id) {
    switch (id) {
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
            .setTitle("1560 알람 M · 1.0.3")
            .setMessage(
                "팔천조 형님을 위한 휴대폰 알람\n\n"
                    + "인터넷 · 계정 없이 휴대폰 안에서 작동합니다.\n"
                    + "알람 시간은 안드로이드 시스템에 예약합니다.\n"
                    + "처음 설치한 뒤 2분 후 알람을 만들어 화면을 잠그고 시험해 주세요.\n\n"
                    + "개인용 앱입니다. 실제 휴대폰에서 알람 시험이 필요합니다.")
            .setPositiveButton("확인", null)
            .show();
        break;
    }
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
