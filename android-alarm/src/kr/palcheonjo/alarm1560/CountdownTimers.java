package kr.palcheonjo.alarm1560;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.SystemClock;
import android.provider.Settings;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** Countdown state and its Android wake-up alarms use elapsed time on the same boot. */
final class CountdownTimers {
  static final String CHANGED = "kr.palcheonjo.alarm1560.TIMERS_CHANGED";
  private static final String CHANNEL = "timer-end-v1";

  static final class Timer {
    final String id, title;
    final long duration, remaining, deadline;

    Timer(String id, String title, long duration, long remaining, long deadline) {
      this.id = id;
      this.title = title;
      this.duration = duration;
      this.remaining = remaining;
      this.deadline = deadline;
    }

    long left(long now) {
      return deadline > 0 ? Math.max(0, deadline - now) : remaining;
    }

    Timer withTime(long remaining, long deadline) {
      return new Timer(id, title, duration, remaining, deadline);
    }

    JSONObject json() throws JSONException {
      return new JSONObject().put("id", id).put("title", title).put("duration", duration)
          .put("remaining", remaining).put("deadline", deadline);
    }
  }

  private final Context context;
  private final SharedPreferences storage;
  private final AlarmManager scheduler;

  CountdownTimers(Context context) {
    this.context = context.getApplicationContext();
    storage = this.context.createDeviceProtectedStorageContext()
        .getSharedPreferences("multi-timers-v1", Context.MODE_PRIVATE);
    scheduler = this.context.getSystemService(AlarmManager.class);
  }

  private int boot() {
    return Settings.Global.getInt(context.getContentResolver(), Settings.Global.BOOT_COUNT, -1);
  }

  List<Timer> read() {
    List<Timer> timers = new ArrayList<>();
    boolean sameBoot = storage.getInt("boot", -1) == boot();
    try {
      JSONArray saved = new JSONArray(storage.getString("timers", "[]"));
      for (int i = 0; i < saved.length(); i++) {
        JSONObject entry = saved.optJSONObject(i);
        if (entry == null) continue;
        long duration = entry.optLong("duration");
        String id = entry.optString("id");
        if (id.isEmpty() || duration <= 0 || duration > 359_999_000L) continue;
        long remaining = Math.max(0, Math.min(duration, entry.optLong("remaining", duration)));
        long deadline = entry.optLong("deadline");
        if (deadline > 0 && !sameBoot) {
          remaining = duration;
          deadline = 0;
        }
        timers.add(new Timer(id, entry.optString("title"), duration, remaining, deadline));
      }
    } catch (JSONException ignored) {
      // Unreadable timer data does not affect alarm reservations or stopwatch records.
    }
    return timers;
  }

  private void write(List<Timer> timers) {
    JSONArray saved = new JSONArray();
    try {
      for (Timer timer : timers) saved.put(timer.json());
    } catch (JSONException error) {
      throw new IllegalStateException(error);
    }
    if (!storage.edit().putString("timers", saved.toString()).putInt("boot", boot()).commit())
      throw new IllegalStateException("타이머 저장 실패");
  }

  void configure(String id, String title, long duration) {
    replace(id, new Timer(id == null ? UUID.randomUUID().toString() : id, title, duration, duration, 0));
  }

  void toggle(Timer timer) {
    long now = SystemClock.elapsedRealtime();
    long remaining = timer.deadline > 0 ? timer.left(now) : timer.remaining;
    if (timer.deadline > 0 && remaining == 0) {
      finishDue();
      return;
    }
    if (timer.deadline > 0) replace(timer.id, timer.withTime(remaining, 0));
    else {
      if (remaining == 0) remaining = timer.duration;
      replace(timer.id, timer.withTime(remaining, now + remaining));
    }
  }

  void reset(Timer timer) {
    replace(timer.id, timer.withTime(timer.duration, 0));
  }

  void remove(Timer timer) {
    replace(timer.id, null);
  }

  private void replace(String id, Timer updated) {
    List<Timer> timers = read();
    Timer previous = null;
    for (int i = 0; i < timers.size(); i++) {
      if (!timers.get(i).id.equals(id)) continue;
      previous = timers.get(i);
      if (updated == null) timers.remove(i);
      else timers.set(i, updated);
      break;
    }
    if (id == null) timers.add(0, updated);
    else if (previous == null) return;

    boolean scheduled = updated != null && updated.deadline > 0;
    if (scheduled) schedule(updated);
    try {
      write(timers);
    } catch (RuntimeException error) {
      if (scheduled) scheduler.cancel(operation(updated));
      throw error;
    }
    if (previous != null && previous.deadline > 0) scheduler.cancel(operation(previous));
  }

  private PendingIntent operation(Timer timer) {
    Intent intent = new Intent(context, CountdownReceiver.class)
        .setAction("TIMER_DUE")
        .setData(Uri.parse("alarm1560://timer/" + timer.id + "/" + timer.deadline));
    return PendingIntent.getBroadcast(context, 0, intent, PendingIntent.FLAG_IMMUTABLE);
  }

  private void schedule(Timer timer) {
    PendingIntent intent = operation(timer);
    try {
      scheduler.setExactAndAllowWhileIdle(AlarmManager.ELAPSED_REALTIME_WAKEUP, timer.deadline, intent);
    } catch (SecurityException unavailable) {
      scheduler.setAndAllowWhileIdle(AlarmManager.ELAPSED_REALTIME_WAKEUP, timer.deadline, intent);
    }
  }

  void restoreScheduling() {
    finishDue();
    for (Timer timer : read()) if (timer.deadline > 0) schedule(timer);
  }

  boolean finishDue() {
    long now = SystemClock.elapsedRealtime();
    List<Timer> timers = read();
    List<Timer> finished = new ArrayList<>();
    for (int i = 0; i < timers.size(); i++) {
      Timer timer = timers.get(i);
      if (timer.deadline > 0 && timer.deadline <= now) {
        timers.set(i, timer.withTime(0, 0));
        finished.add(timer);
      }
    }
    if (finished.isEmpty()) return false;
    write(timers);
    for (Timer timer : finished) {
      scheduler.cancel(operation(timer));
      notifyFinished(timer);
    }
    context.sendBroadcast(new Intent(CHANGED).setPackage(context.getPackageName()));
    return true;
  }

  private void notifyFinished(Timer timer) {
    NotificationManager manager = context.getSystemService(NotificationManager.class);
    if (!manager.areNotificationsEnabled()) return;
    NotificationChannel channel =
        new NotificationChannel(CHANNEL, "타이머 종료", NotificationManager.IMPORTANCE_HIGH);
    channel.setSound(
        RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION),
        new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM).build());
    channel.enableVibration(true);
    manager.createNotificationChannel(channel);
    PendingIntent open = PendingIntent.getActivity(
        context, 0, new Intent(context, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
    Notification notice = new Notification.Builder(context, CHANNEL)
        .setSmallIcon(R.drawable.ic_alarm).setContentTitle(timer.title)
        .setContentText("타이머가 끝났습니다").setCategory(Notification.CATEGORY_ALARM)
        .setAutoCancel(true).setContentIntent(open).build();
    try {
      manager.notify(timer.id, 0, notice);
    } catch (SecurityException ignored) {
      // Notification permission may have changed while the timer was running.
    }
  }

  static String format(long millis) {
    long seconds = (millis + 999) / 1000;
    long hours = seconds / 3600;
    long minutes = seconds / 60 % 60;
    if (hours == 0) return String.format(Locale.US, "%02d:%02d", minutes, seconds % 60);
    return String.format(Locale.US, "%02d:%02d:%02d", hours, minutes, seconds % 60);
  }
}
