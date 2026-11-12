package kr.palcheonjo.alarm1560;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.SystemClock;
import android.provider.Settings;
import android.util.TypedValue;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.Locale;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

final class TripTimerPane extends ScrollView {
  private static final int MAX_RECORDS = 30;
  private final SharedPreferences state;
  private final TextView clock, departure;
  private final Button action;
  private final LinearLayout history;
  private JSONArray records = new JSONArray();
  private long startedAt;
  private long startTick;

  TripTimerPane(Context context) {
    super(context);
    setTag("trip-timer");
    setFillViewport(true);
    state = context.createDeviceProtectedStorageContext()
        .getSharedPreferences("trip-timer-v1", Context.MODE_PRIVATE);

    LinearLayout content = Ui.column(context);
    int padding = Ui.dp(context, 9);
    content.setPadding(padding, Ui.dp(context, 8), padding, padding);
    addView(content);
    LinearLayout card = Ui.column(context);
    card.setPadding(padding, padding, padding, padding);
    card.setBackground(Ui.shape(Ui.CARD, Ui.dp(context, 20)));
    clock = Ui.bold(context, "00:00:00", 32, Ui.WHITE);
    clock.setTag("trip-elapsed");
    clock.setGravity(Gravity.CENTER);
    clock.setSingleLine(true);
    clock.setAutoSizeTextTypeUniformWithConfiguration(13, 32, 1, TypedValue.COMPLEX_UNIT_SP);
    card.addView(clock, new LinearLayout.LayoutParams(-1, Ui.dp(context, 58)));
    departure = Ui.text(context, "", 13, Ui.GRAY);
    departure.setGravity(Gravity.CENTER);
    card.addView(departure);
    action = Ui.button(context, "출발", true);
    action.setTag("trip-action");
    action.setOnClickListener(v -> markTrip());
    card.addView(action, new LinearLayout.LayoutParams(-1, -2));
    Ui.addCard(content, card);

    TextView historyTitle = Ui.bold(context, "운행 기록", 16, Ui.WHITE);
    if (Build.VERSION.SDK_INT >= 28) historyTitle.setAccessibilityHeading(true);
    content.addView(historyTitle);
    history = Ui.column(context);
    history.setTag("trip-history");
    content.addView(history);
  }

  void restore() {
    startedAt = state.getLong("started-at", 0);
    startTick = state.getLong("start-tick", 0);
    if (startedAt != 0
        && (state.getInt("boot", -1) != bootCount() || startTick > SystemClock.elapsedRealtime())) {
      startedAt = 0;
      state.edit().remove("started-at").remove("start-tick").remove("boot").apply();
    }
    try {
      records = new JSONArray(state.getString("records", "[]"));
    } catch (JSONException error) {
      records = new JSONArray();
    }
    render();
  }

  private int bootCount() {
    return Settings.Global.getInt(getContext().getContentResolver(), Settings.Global.BOOT_COUNT, -1);
  }

  private long elapsed() {
    if (startedAt != 0) return Math.max(0, SystemClock.elapsedRealtime() - startTick);
    JSONObject latest = records.optJSONObject(0);
    return latest == null ? 0 : latest.optLong("elapsed");
  }

  private void markTrip() {
    // Re-read saved state in case another instance of the screen was opened.
    restore();
    try {
      SharedPreferences.Editor change = state.edit();
      if (startedAt == 0) {
        change.putLong("started-at", System.currentTimeMillis())
            .putLong("start-tick", SystemClock.elapsedRealtime()).putInt("boot", bootCount());
      } else {
        JSONObject trip = new JSONObject()
            .put("departure", startedAt)
            .put("arrival", System.currentTimeMillis())
            .put("elapsed", elapsed());
        JSONArray updated = new JSONArray().put(trip);
        for (int i = 0; i < Math.min(records.length(), MAX_RECORDS - 1); i++) {
          updated.put(records.get(i));
        }
        change.putString("records", updated.toString())
            .remove("started-at").remove("start-tick").remove("boot");
      }
      if (!change.commit()) showSaveError();
    } catch (JSONException error) {
      showSaveError();
    }
    restore();
  }

  private void showSaveError() {
    Toast.makeText(getContext(), "타이머 기록을 저장할 수 없습니다.", Toast.LENGTH_SHORT).show();
  }

  void refresh() {
    String text = formatElapsed(elapsed());
    if (!text.contentEquals(clock.getText())) clock.setText(text);
  }

  private void render() {
    action.setText(startedAt == 0 ? "출발" : "도착");
    JSONObject latest = records.optJSONObject(0);
    departure.setText(startedAt != 0 ? "출발 " + Ui.date(startedAt)
        : latest == null ? "출발을 눌러 시간을 재세요" : "도착 " + Ui.date(latest.optLong("arrival")));
    refresh();
    history.removeAllViews();
    Context context = getContext();
    if (records.length() == 0) history.addView(Ui.text(context, "아직 기록이 없습니다", 13, Ui.GRAY));
    for (int i = 0; i < records.length(); i++) {
      JSONObject trip = records.optJSONObject(i);
      if (trip == null) continue;
      LinearLayout row = Ui.column(context);
      int padding = Ui.dp(context, 10);
      row.setPadding(padding, Ui.dp(context, 4), padding, Ui.dp(context, 4));
      row.setBackground(Ui.shape(Ui.CARD, Ui.dp(context, 15)));
      row.addView(Ui.bold(context, formatElapsed(trip.optLong("elapsed")), 20, Ui.WHITE));
      row.addView(Ui.text(context, "출발 " + Ui.date(trip.optLong("departure"))
          + "\n도착 " + Ui.date(trip.optLong("arrival")), 12, Ui.GRAY));
      Ui.addCard(history, row);
    }
  }

  private static String formatElapsed(long millis) {
    long seconds = millis / 1000;
    return String.format(Locale.KOREA, "%02d:%02d:%02d", seconds / 3600, seconds / 60 % 60, seconds % 60);
  }
}
