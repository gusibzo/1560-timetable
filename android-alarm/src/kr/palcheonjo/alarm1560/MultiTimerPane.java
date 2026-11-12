package kr.palcheonjo.alarm1560;

import android.app.AlertDialog;
import android.content.Context;
import android.os.SystemClock;
import android.text.InputFilter;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.PopupMenu;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

final class MultiTimerPane extends ScrollView {
  private final CountdownTimers timers;
  private final LinearLayout list;
  private final Map<CountdownTimers.Timer, TextView> clocks = new LinkedHashMap<>();

  MultiTimerPane(Context context) {
    super(context);
    setTag("multi-timer");
    setFillViewport(true);
    timers = new CountdownTimers(context);
    LinearLayout content = Ui.column(context);
    int padding = Ui.dp(context, 9);
    content.setPadding(padding, Ui.dp(context, 8), padding, padding);
    addView(content);
    Button add = button("＋ 타이머 추가", true);
    add.setTag("multi-timer-add");
    add.setOnClickListener(v -> edit(null));
    Ui.addCard(content, add);
    list = Ui.column(context);
    list.setTag("multi-timer-list");
    content.addView(list);
  }

  void restore() {
    try {
      timers.restoreScheduling();
    } catch (RuntimeException error) {
      storageError();
    }
    render();
  }

  void refresh() {
    long now = SystemClock.elapsedRealtime();
    for (Map.Entry<CountdownTimers.Timer, TextView> entry : clocks.entrySet()) {
      CountdownTimers.Timer timer = entry.getKey();
      if (timer.deadline <= 0) continue;
      long left = timer.left(now);
      if (left == 0) {
        try {
          timers.finishDue();
        } catch (RuntimeException error) {
          storageError();
        }
        render();
        return;
      }
      entry.getValue().setText(CountdownTimers.format(left));
    }
  }

  void render() {
    Context context = getContext();
    List<CountdownTimers.Timer> saved = timers.read();
    clocks.clear();
    list.removeAllViews();
    if (saved.isEmpty()) list.addView(Ui.text(context, "시간을 정해 타이머를 추가하세요", 13, Ui.GRAY));
    for (CountdownTimers.Timer timer : saved) addCard(timer);
  }

  private void addCard(CountdownTimers.Timer timer) {
    Context context = getContext();
    LinearLayout card = Ui.column(context);
    int padding = Ui.dp(context, 8);
    card.setPadding(padding, Ui.dp(context, 4), padding, padding);
    card.setBackground(Ui.shape(Ui.CARD, Ui.dp(context, 16)));
    LinearLayout titleRow = Ui.row(context);
    titleRow.addView(Ui.bold(context, timer.title, 14, Ui.WHITE),
        new LinearLayout.LayoutParams(0, -2, 1));
    Button options = button("⋮", false);
    options.setTextSize(19);
    options.setContentDescription(timer.title + " 메뉴");
    titleRow.addView(options, new LinearLayout.LayoutParams(Ui.dp(context, 42), -2));
    options.setOnClickListener(v -> {
      PopupMenu menu = new PopupMenu(context, options);
      menu.getMenu().add(0, 1, 0, "시간 수정");
      menu.getMenu().add(0, 2, 1, "삭제");
      menu.setOnMenuItemClickListener(item -> {
        if (item.getItemId() == 1) edit(timer);
        else new AlertDialog.Builder(context).setTitle(timer.title + " 삭제")
            .setNegativeButton("취소", null)
            .setPositiveButton("삭제", (dialog, which) -> update(() -> timers.remove(timer)))
            .show();
        return true;
      });
      menu.show();
    });
    card.addView(titleRow);

    TextView clock = Ui.bold(context, CountdownTimers.format(timer.left(SystemClock.elapsedRealtime())),
        30, timer.deadline > 0 ? Ui.GOLD : Ui.WHITE);
    clock.setTag("countdown-clock");
    clock.setSingleLine(true);
    clock.setGravity(Gravity.CENTER);
    clock.setAutoSizeTextTypeUniformWithConfiguration(14, 30, 1, TypedValue.COMPLEX_UNIT_SP);
    card.addView(clock, new LinearLayout.LayoutParams(-1, Ui.dp(context, 54)));
    clocks.put(timer, clock);

    String status = "준비", action = "시작";
    if (timer.deadline > 0) {
      status = "진행 중";
      action = "일시정지";
    } else if (timer.remaining == 0) {
      status = "종료";
      action = "다시 시작";
    } else if (timer.remaining < timer.duration) {
      status = "일시정지";
      action = "계속";
    }
    TextView state = Ui.text(context, status, 12, Ui.GRAY);
    state.setGravity(Gravity.CENTER);
    card.addView(state);
    Button run = button(action, true);
    run.setTag("countdown-action");
    run.setContentDescription(timer.title + " " + action);
    run.setOnClickListener(v -> update(() -> timers.toggle(timer)));
    card.addView(run, new LinearLayout.LayoutParams(-1, -2));
    Button reset = button("초기화", false);
    reset.setTag("countdown-reset");
    reset.setContentDescription(timer.title + " 초기화");
    reset.setOnClickListener(v -> update(() -> timers.reset(timer)));
    card.addView(reset, new LinearLayout.LayoutParams(-1, -2));
    Ui.addCard(list, card);
  }

  private Button button(String text, boolean gold) {
    Button button = Ui.button(getContext(), text, gold);
    button.setTextSize(13);
    button.setMinWidth(0);
    button.setMinimumWidth(0);
    button.setMinHeight(Ui.dp(getContext(), 48));
    button.setPadding(Ui.dp(getContext(), 4), 0, Ui.dp(getContext(), 4), 0);
    return button;
  }

  private void edit(CountdownTimers.Timer timer) {
    Context context = getContext();
    LinearLayout form = Ui.column(context);
    int padding = Ui.dp(context, 20);
    form.setPadding(padding, 0, padding, 0);
    EditText name = new EditText(context);
    name.setSingleLine(true);
    name.setHint("이름 (선택)");
    name.setFilters(new InputFilter[] {new InputFilter.LengthFilter(32)});
    name.setTag("countdown-name");
    form.addView(name);

    long seconds = timer == null ? 300 : timer.duration / 1000;
    LinearLayout row = Ui.row(context);
    EditText hour = number(row, "시간", (int) (seconds / 3600));
    EditText minute = number(row, "분", (int) (seconds / 60 % 60));
    EditText second = number(row, "초", (int) (seconds % 60));
    form.addView(row);
    AlertDialog dialog = new AlertDialog.Builder(context)
        .setTitle(timer == null ? "타이머 추가" : "타이머 수정")
        .setView(form).setNegativeButton("취소", null).setPositiveButton("저장", null).create();
    if (timer != null) name.setText(timer.title);
    dialog.show();
    dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
      int h = numberValue(hour), m = numberValue(minute), s = numberValue(second);
      if (m > 59) {
        minute.setError("0~59분");
        return;
      }
      if (s > 59) {
        second.setError("0~59초");
        return;
      }
      long duration = (h * 3600L + m * 60L + s) * 1000L;
      if (duration == 0) {
        second.setError("1초 이상 입력해 주세요");
        return;
      }
      String title = name.getText().toString().trim();
      String label = title.isEmpty() ? CountdownTimers.format(duration) + " 타이머" : title;
      if (update(() -> timers.configure(timer == null ? null : timer.id, label, duration))) dialog.dismiss();
    });
  }

  private EditText number(LinearLayout row, String unit, int value) {
    Context context = getContext();
    LinearLayout column = Ui.column(context);
    TextView label = Ui.text(context, unit, 14, Ui.GRAY);
    label.setGravity(Gravity.CENTER);
    column.addView(label);
    EditText input = new EditText(context);
    input.setSingleLine(true);
    input.setInputType(InputType.TYPE_CLASS_NUMBER);
    input.setGravity(Gravity.CENTER);
    input.setFilters(new InputFilter[] {new InputFilter.LengthFilter(2)});
    input.setSelectAllOnFocus(true);
    input.setText(Integer.toString(value));
    input.setTag("countdown-" + unit);
    input.setContentDescription(unit);
    column.addView(input, new LinearLayout.LayoutParams(-1, -2));
    row.addView(column, new LinearLayout.LayoutParams(0, -2, 1));
    return input;
  }

  private int numberValue(EditText input) {
    String text = input.getText().toString();
    return text.isEmpty() ? 0 : Integer.parseInt(text);
  }

  private boolean update(Runnable change) {
    try {
      change.run();
      render();
      return true;
    } catch (RuntimeException error) {
      storageError();
      return false;
    }
  }

  private void storageError() {
    Toast.makeText(getContext(), "타이머를 저장하지 못했습니다. 다시 시도해 주세요.", Toast.LENGTH_SHORT).show();
  }
}
