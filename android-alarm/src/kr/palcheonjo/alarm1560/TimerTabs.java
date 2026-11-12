package kr.palcheonjo.alarm1560;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;

final class TimerTabs extends LinearLayout {
  private final SharedPreferences preferences;
  private final Button multiTab, stopwatchTab;
  private final MultiTimerPane multi;
  private final TripTimerPane stopwatch;

  TimerTabs(Context context, SharedPreferences preferences) {
    super(context);
    this.preferences = preferences;
    setOrientation(VERTICAL);
    LinearLayout tabs = Ui.row(context);
    int padding = Ui.dp(context, 5);
    tabs.setPadding(padding, padding, padding, 0);
    multiTab = tab(tabs, "멀티 타이머", "timer-tab-multi", true);
    stopwatchTab = tab(tabs, "스톱워치", "timer-tab-stopwatch", false);
    addView(tabs, new LinearLayout.LayoutParams(-1, -2));

    FrameLayout panels = new FrameLayout(context);
    multi = new MultiTimerPane(context);
    stopwatch = new TripTimerPane(context);
    panels.addView(multi, new FrameLayout.LayoutParams(-1, -1));
    panels.addView(stopwatch, new FrameLayout.LayoutParams(-1, -1));
    addView(panels, new LinearLayout.LayoutParams(-1, 0, 1));
    select(preferences.getBoolean("countdown-tab", false));
  }

  private Button tab(LinearLayout row, String title, String tag, boolean countdown) {
    Button tab = Ui.button(getContext(), title, false);
    tab.setTag(tag);
    tab.setTextSize(13);
    tab.setMinWidth(0);
    tab.setMinimumWidth(0);
    tab.setPadding(Ui.dp(getContext(), 2), 0, Ui.dp(getContext(), 2), 0);
    tab.setMinHeight(Ui.dp(getContext(), 48));
    row.addView(tab, new LinearLayout.LayoutParams(0, -2, 1));
    tab.setOnClickListener(v -> {
      select(countdown);
      preferences.edit().putBoolean("countdown-tab", countdown).apply();
    });
    return tab;
  }

  private void select(boolean countdown) {
    multi.setVisibility(countdown ? VISIBLE : GONE);
    stopwatch.setVisibility(countdown ? GONE : VISIBLE);
    style(multiTab, countdown);
    style(stopwatchTab, !countdown);
  }

  private void style(Button tab, boolean selected) {
    tab.setSelected(selected);
    tab.setTextColor(selected ? Color.BLACK : Ui.WHITE);
    tab.setBackgroundTintList(ColorStateList.valueOf(selected ? Ui.GOLD : 0xff303034));
  }

  void restore() {
    multi.restore();
    stopwatch.restore();
  }

  void refresh() {
    multi.refresh();
    stopwatch.refresh();
  }

  void countdownsChanged() {
    multi.render();
  }
}
