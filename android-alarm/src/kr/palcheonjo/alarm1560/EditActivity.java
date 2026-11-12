package kr.palcheonjo.alarm1560;

import android.app.*;
import android.media.AudioManager;
import android.os.Bundle;
import android.widget.*;
import java.util.*;
import org.json.JSONObject;

public final class EditActivity extends Activity {
  private Alarm alarm;
  private EditText name;
  private ToggleButton[] dayButtons = new ToggleButton[7];
  private Spinner sounds, snoozeMinutes;
  private SeekBar gain;
  private CheckBox ramp, vibrate, snooze;
  private TextView dateLabel, time;
  private AlarmAudio preview;
  private Button previewButton;
  private boolean previewing;

  @Override
  public void onCreate(Bundle saved) {
    super.onCreate(saved);
    setVolumeControlStream(AudioManager.STREAM_ALARM);
    preview = new AlarmAudio(this);
    String id = getIntent().getStringExtra("id");
    alarm = id == null ? new Alarm() : Engine.find(this, id);
    if (alarm == null) alarm = new Alarm();
    if (id == null) {
      Calendar c = Calendar.getInstance();
      c.add(Calendar.MINUTE, 2);
      alarm.hour = c.get(Calendar.HOUR_OF_DAY);
      alarm.minute = c.get(Calendar.MINUTE);
    }
    if (saved != null) {
      try {
        alarm = Alarm.from(new JSONObject(saved.getString("draft")));
      } catch (Exception ignored) {
      }
    }
    if (saved == null && !alarm.enabled && alarm.days == 0 && !alarm.date.isEmpty()
        && AlarmTime.next(System.currentTimeMillis(), alarm.hour, alarm.minute, 0, alarm.date,
            TimeZone.getDefault()) == 0) {
      // An elapsed one-time reservation can be set again using its next occurrence.
      alarm.date = "";
    }
    LinearLayout root = Ui.column(this);
    Ui.screen(this, root);
    root.addView(Ui.bold(this, id == null ? "알람 추가" : "알람 수정", 25, Ui.WHITE));
    ScrollView scroll = new ScrollView(this);
    LinearLayout form = Ui.column(this);
    scroll.addView(form);
    root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
    LinearLayout first = Ui.card(this);
    time = Ui.bold(this, Ui.time(alarm), 60, Ui.WHITE);
    first.addView(time);
    Button choose = Ui.button(this, "시간 선택", true);
    first.addView(choose);
    choose.setOnClickListener(
        v -> {
          stopPreview();
          new TimePickerDialog(
                  this,
                  (view, h, m) -> {
                    alarm.hour = h;
                    alarm.minute = m;
                    time.setText(Ui.time(alarm));
                  },
                  alarm.hour,
                  alarm.minute,
                  true)
              .show();
        });
    Ui.addCard(form, first);
    LinearLayout repeat = Ui.card(this);
    repeat.addView(Ui.bold(this, "반복 요일", 20, Ui.WHITE));
    LinearLayout days = Ui.row(this);
    String[] labels = {"일", "월", "화", "수", "목", "금", "토"};
    for (int n = 0; n < 7; n++) {
      ToggleButton b = new ToggleButton(this);
      b.setTextOn(labels[n]);
      b.setTextOff(labels[n]);
      b.setText(labels[n]);
      b.setTextSize(15);
      b.setMinWidth(0);
      b.setPadding(0, 0, 0, 0);
      b.setChecked((alarm.days & (1 << n)) != 0);
      days.addView(b, new LinearLayout.LayoutParams(0, Ui.dp(this, 50), 1));
      dayButtons[n] = b;
      b.setOnCheckedChangeListener(
          (button, checked) -> {
            alarm.days = mask();
            if (alarm.days != 0) alarm.date = "";
            updateDate();
          });
    }
    repeat.addView(days);
    LinearLayout presets = Ui.row(this);
    String[] presetsText = {"평일", "주말", "매일", "한 번"};
    int[] masks = {62, 65, 127, 0};
    for (int n = 0; n < 4; n++) {
      final int mask = masks[n];
      Button b = Ui.button(this, presetsText[n], false);
      b.setTextSize(14);
      b.setMinWidth(0);
      b.setPadding(0, 0, 0, 0);
      presets.addView(b, new LinearLayout.LayoutParams(0, -2, 1));
      b.setOnClickListener(
          v -> {
            for (int k = 0; k < 7; k++) dayButtons[k].setChecked((mask & (1 << k)) != 0);
            alarm.date = "";
            updateDate();
          });
    }
    repeat.addView(presets);
    dateLabel = Ui.text(this, "", 16, Ui.GRAY);
    repeat.addView(dateLabel);
    Button date = Ui.button(this, "특정 날짜 선택", false);
    repeat.addView(date);
    date.setOnClickListener(
        v -> {
          stopPreview();
          Calendar c = Calendar.getInstance();
          new DatePickerDialog(
                  this,
                  (view, y, m, d) -> {
                    for (ToggleButton b : dayButtons) b.setChecked(false);
                    alarm.date = String.format(Locale.US, "%04d-%02d-%02d", y, m + 1, d);
                    updateDate();
                  },
                  c.get(Calendar.YEAR),
                  c.get(Calendar.MONTH),
                  c.get(Calendar.DATE))
              .show();
        });
    updateDate();
    Ui.addCard(form, repeat);
    LinearLayout naming = Ui.card(this);
    naming.addView(Ui.bold(this, "알람 이름", 20, Ui.WHITE));
    name = new EditText(this);
    name.setSingleLine(true);
    name.setText(alarm.label);
    name.setHint("예: 평일 8번, 집 출발");
    name.setTextSize(19);
    name.setFilters(new android.text.InputFilter[] {new android.text.InputFilter.LengthFilter(80)});
    naming.addView(name);
    Ui.addCard(form, naming);
    LinearLayout sound = Ui.card(this);
    sound.addView(Ui.bold(this, "알람 소리", 20, Ui.WHITE));
    sounds = new Spinner(this);
    sounds.setAdapter(
        new ArrayAdapter<String>(
            this, android.R.layout.simple_spinner_dropdown_item, Sounds.NAMES));
    sounds.setSelection(Sounds.index(alarm.sound));
    sound.addView(sounds, new LinearLayout.LayoutParams(-1, Ui.dp(this, 58)));
    previewButton = Ui.button(this, "▶ 소리 미리듣기", false);
    sound.addView(previewButton);
    previewButton.setOnClickListener(
        v -> {
          if (previewing) stopPreview();
          else {
            readForm();
            preview.start(alarm, false);
            previewing = true;
            previewButton.setText("■ 미리듣기 중지");
          }
        });
    TextView volume = Ui.bold(this, "이 알람의 소리 크기 " + alarm.volume + "%", 18, Ui.WHITE);
    sound.addView(volume);
    gain = new SeekBar(this);
    gain.setMax(90);
    gain.setProgress(alarm.volume - 10);
    sound.addView(gain);
    gain.setOnSeekBarChangeListener(
        new SeekBar.OnSeekBarChangeListener() {
          public void onProgressChanged(SeekBar s, int p, boolean user) {
            volume.setText("이 알람의 소리 크기 " + (p + 10) + "%");
            if (user) stopPreview();
          }

          public void onStartTrackingTouch(SeekBar s) {}

          public void onStopTrackingTouch(SeekBar s) {}
        });
    sound.addView(
        Ui.text(this, "전체 크기는 휴대폰의 ‘알람 음량’으로 정해집니다.\n이어폰 미디어 음량과 별도로 조절합니다.", 15, Ui.GRAY));
    ramp = check("30초 동안 점점 크게", alarm.ramp);
    vibrate = check("진동 함께 울리기", alarm.vibrate);
    snooze = check("다시 알림 사용 (최대 3회)", alarm.snooze);
    sound.addView(ramp);
    sound.addView(vibrate);
    sound.addView(snooze);
    snoozeMinutes = new Spinner(this);
    String[] intervals = {"1분 뒤 다시", "3분 뒤 다시", "5분 뒤 다시", "10분 뒤 다시", "15분 뒤 다시"};
    snoozeMinutes.setAdapter(
        new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, intervals));
    int[] values = {1, 3, 5, 10, 15};
    int selected = 2;
    for (int k = 0; k < values.length; k++) if (values[k] == alarm.snoozeMinutes) selected = k;
    snoozeMinutes.setSelection(selected);
    sound.addView(snoozeMinutes, new LinearLayout.LayoutParams(-1, Ui.dp(this, 52)));
    Ui.addCard(form, sound);
    if (id != null) {
      Button delete = Ui.button(this, "이 알람 삭제", false);
      form.addView(delete);
      delete.setOnClickListener(
          v ->
              new AlertDialog.Builder(this)
                  .setTitle("이 알람을 삭제할까요?")
                  .setMessage(Engine.title(alarm))
                  .setNegativeButton("취소", null)
                  .setPositiveButton(
                      "삭제",
                      (dialog, w) -> {
                        stopPreview();
                        Engine.remove(this, alarm.id);
                        finish();
                      })
                  .show());
    }
    LinearLayout actions = Ui.row(this);
    Button cancel = Ui.button(this, "취소", false), save = Ui.button(this, "저장", true);
    actions.addView(cancel, new LinearLayout.LayoutParams(0, Ui.dp(this, 64), 1));
    actions.addView(save, new LinearLayout.LayoutParams(0, Ui.dp(this, 64), 1));
    root.addView(actions);
    cancel.setOnClickListener(v -> finish());
    save.setTag("alarm-editor-save");
    save.setOnClickListener(v -> save());
  }

  private CheckBox check(String label, boolean selected) {
    CheckBox b = new CheckBox(this);
    b.setText(label);
    b.setTextSize(17);
    b.setChecked(selected);
    return b;
  }

  private int mask() {
    int value = 0;
    for (int n = 0; n < dayButtons.length; n++)
      if (dayButtons[n] != null && dayButtons[n].isChecked()) value |= 1 << n;
    return value;
  }

  private void updateDate() {
    if (dateLabel != null)
      dateLabel.setText(
          alarm.days != 0
              ? Ui.dayDescription(alarm)
              : alarm.date.isEmpty() ? "한 번 · 다음에 돌아오는 선택 시간에 울림" : alarm.date + " · 한 번만 울림");
  }

  private void readForm() {
    if (name == null) return;
    alarm.label = name.getText().toString().trim();
    alarm.days = mask();
    alarm.sound = Sounds.IDS[sounds.getSelectedItemPosition()];
    alarm.volume = gain.getProgress() + 10;
    alarm.ramp = ramp.isChecked();
    alarm.vibrate = vibrate.isChecked();
    alarm.snooze = snooze.isChecked();
    alarm.snoozeMinutes = new int[] {1, 3, 5, 10, 15}[snoozeMinutes.getSelectedItemPosition()];
  }

  private void save() {
    stopPreview();
    readForm();
    alarm.arm(System.currentTimeMillis());
    if (alarm.days == 0 && alarm.oneTimeAt == 0) {
      Toast.makeText(this, "이미 지난 날짜입니다. 날짜나 시간을 바꿔 주세요.", Toast.LENGTH_LONG).show();
      return;
    }
    if (alarm.days == 0) alarm.date = MainActivity.iso(alarm.oneTimeAt);
    alarm.enabled = true;
    try {
      Engine.save(this, alarm);
      String message = Engine.scheduled(this, alarm.id) > 0
          ? "알람을 켜고 저장했습니다"
          : "알람을 저장했습니다. 예약 권한을 확인해 주세요.";
      Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
      finish();
    } catch (RuntimeException e) {
      Toast.makeText(this, "저장하지 못했습니다. 다시 시도해 주세요.", Toast.LENGTH_LONG).show();
    }
  }

  private void stopPreview() {
    if (preview != null) preview.stop();
    previewing = false;
    if (previewButton != null) previewButton.setText("▶ 소리 미리듣기");
  }

  @Override
  protected void onPause() {
    stopPreview();
    super.onPause();
  }

  @Override
  protected void onSaveInstanceState(Bundle b) {
    readForm();
    b.putString("draft", alarm.json().toString());
    super.onSaveInstanceState(b);
  }

  @Override
  protected void onDestroy() {
    stopPreview();
    super.onDestroy();
  }
}
