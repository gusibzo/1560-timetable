package kr.palcheonjo.alarm1560.tests;

import android.app.*;
import android.content.*;
import android.media.*;
import android.os.*;
import java.io.*;
import java.util.*;
import java.util.function.BooleanSupplier;
import kr.palcheonjo.alarm1560.*;
import org.json.*;

/** Destructive to the test emulator's app data. Never run against a user's phone. */
public final class DeviceTest extends Instrumentation {
  private Context context;
  private int checks;

  @Override
  public void onCreate(Bundle args) {
    super.onCreate(args);
    start();
  }

  private void check(boolean value, String label) {
    if (!value) throw new AssertionError(label);
    checks++;
  }

  private void capture(String name) throws IOException {
    android.graphics.Bitmap bitmap = getUiAutomation().takeScreenshot();
    if (bitmap == null) throw new IOException("Screenshot unavailable");
    try (FileOutputStream out =
        new FileOutputStream(new File(context.getExternalFilesDir(null), name))) {
      bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, out);
    }
    bitmap.recycle();
  }

  private void phase(String text) {
    Bundle b = new Bundle();
    b.putString("phase", text);
    sendStatus(0, b);
  }

  private void waitFor(BooleanSupplier test, long max, String label) throws Exception {
    long end = SystemClock.elapsedRealtime() + max;
    while (SystemClock.elapsedRealtime() < end) {
      if (test.getAsBoolean()) {
        checks++;
        return;
      }
      Thread.sleep(200);
    }
    throw new AssertionError(label);
  }

  private Alarm sample(String label, long delay) {
    Alarm a = new Alarm();
    Calendar c = Calendar.getInstance();
    a.hour = c.get(Calendar.HOUR_OF_DAY);
    a.minute = c.get(Calendar.MINUTE);
    a.label = label;
    a.oneTimeAt = System.currentTimeMillis() + delay;
    a.ramp = false;
    return a;
  }

  private String token(JSONObject active) {
    return Alarm.from(active.optJSONObject("alarm")).id + ":" + active.optLong("at");
  }

  private void stop(String action) throws Exception {
    JSONObject active = Engine.active(context);
    check(active != null, "active before action");
    context.startService(
        new Intent(context, AlarmService.class).setAction(action).putExtra("token", token(active)));
  }

  @Override
  public void onStart() {
    Bundle result = new Bundle();
    try {
      context = getTargetContext();
      phase("storage and OS scheduling");
      for (Alarm a : Engine.alarms(context)) Engine.remove(context, a.id);
      for (int clear = 0; clear < 200 && Engine.active(context) != null; clear++)
        Engine.finish(context, false);
      check(Engine.exactAllowed(context), "exact alarm permission");
      check(
          context.getSystemService(NotificationManager.class).areNotificationsEnabled(),
          "notifications allowed");
      Alarm a = sample("기기 시험", 120_000);
      Engine.save(context, a);
      check(Engine.find(context, a.id) != null, "persistent alarm");
      check(Engine.scheduled(context, a.id) == a.oneTimeAt, "scheduled timestamp");
      AlarmManager manager = context.getSystemService(AlarmManager.class);
      check(
          manager.getNextAlarmClock() != null
              && manager.getNextAlarmClock().getTriggerTime() == a.oneTimeAt,
          "OS AlarmClock registration");
      long old = a.oneTimeAt;
      a.oneTimeAt += 60_000;
      Engine.save(context, a);
      check(Engine.scheduled(context, a.id) == a.oneTimeAt, "edited alarm rescheduled");
      check(!Engine.claim(context, a.id, old), "stale delivery rejected");
      Engine.remove(context, a.id);
      check(Engine.scheduled(context, a.id) == 0, "deleted alarm canceled");
      check(manager.getNextAlarmClock() == null, "OS cancellation");
      phase("screen-off exact alarm and independent alarm audio");
      AudioManager am = context.getSystemService(AudioManager.class);
      am.setStreamVolume(AudioManager.STREAM_MUSIC, 0, 0);
      am.setStreamVolume(AudioManager.STREAM_ALARM, 4, 0);
      a = sample("잠금 화면 알람 시험", 30_000);
      a.sound = "tiger";
      Engine.save(context, a);
      final String id = a.id;
      final long fireAt = a.oneTimeAt;
      try (ParcelFileDescriptor fd =
          getUiAutomation().executeShellCommand("input keyevent KEYCODE_SLEEP")) {
        Thread.sleep(500);
      }
      waitFor(
          () -> !context.getSystemService(PowerManager.class).isInteractive(),
          20_000,
          "screen was not off before alarm");
      waitFor(() -> Engine.active(context) != null, 90_000, "alarm did not fire while screen off");
      check(Engine.find(context, id).lastFired == fireAt, "receiver consumed exact occurrence");
      check(!Engine.find(context, id).enabled, "one-shot disabled after firing");
      check(!Engine.claim(context, id, fireAt), "duplicate delivery rejected");
      waitFor(
          () -> {
            for (ActivityManager.RunningServiceInfo s :
                context.getSystemService(ActivityManager.class).getRunningServices(20))
              if (s.service.getClassName().equals(AlarmService.class.getName()) && s.foreground)
                return true;
            return false;
          },
          15_000,
          "playback foreground service");
      waitFor(
          () -> {
            for (AudioPlaybackConfiguration p : am.getActivePlaybackConfigurations())
              if (p.getAudioAttributes().getUsage() == AudioAttributes.USAGE_ALARM) return true;
            return false;
          },
          90_000,
          "ALARM audio usage");
      check(am.getStreamVolume(AudioManager.STREAM_MUSIC) == 0, "media volume remains zero");
      check(am.getStreamVolume(AudioManager.STREAM_ALARM) == 4, "alarm volume remains independent");
      phase("snooze and dismissal");
      stop(AlarmService.SNOOZE);
      waitFor(() -> Engine.active(context) == null, 10_000, "snooze stopped ringing");
      Alarm snoozed = Engine.find(context, id);
      check(snoozed.snoozeLeft == 2, "snooze count");
      check(snoozed.snoozeUntil > System.currentTimeMillis(), "snooze time persisted");
      check(Engine.scheduled(context, id) == snoozed.snoozeUntil, "snooze in AlarmManager");
      snoozed.snoozeUntil = System.currentTimeMillis() + 8_000;
      Engine.save(context, snoozed);
      waitFor(() -> Engine.active(context) != null, 55_000, "snoozed alarm did not ring");
      stop(AlarmService.STOP);
      waitFor(() -> Engine.active(context) == null, 10_000, "dismiss stopped ringing");
      check(Engine.scheduled(context, id) == 0, "dismiss leaves no one-shot reservation");
      Engine.remove(context, id);
      phase("simultaneous alarm queue");
      Alarm first = sample("동시 알람 1", 10_000), second = sample("동시 알람 2", 10_000);
      second.oneTimeAt = first.oneTimeAt;
      Engine.save(context, first);
      Engine.save(context, second);
      waitFor(
          () -> {
            try {
              return new JSONObject(Engine.exportData(context)).optJSONArray("queue").length() == 1;
            } catch (Exception e) {
              return false;
            }
          },
          65_000,
          "second simultaneous alarm queued");
      String firstToken = token(Engine.active(context));
      stop(AlarmService.STOP);
      waitFor(
          () -> {
            JSONObject active = Engine.active(context);
            return active != null && !firstToken.equals(token(active));
          },
          10_000,
          "queued alarm advanced");
      stop(AlarmService.STOP);
      waitFor(() -> Engine.active(context) == null, 10_000, "queue dismissed");
      Engine.remove(context, first.id);
      Engine.remove(context, second.id);
      phase("recently due reservation recovery");
      Alarm recovery = sample("예약 지연 복구 시험", 3000);
      Engine.save(context, recovery);
      Intent operation =
          new Intent(context, AlarmReceiver.class)
              .setAction("RING")
              .setData(
                  android.net.Uri.parse(
                      "alarm1560://ring/" + recovery.id + "/" + recovery.oneTimeAt));
      PendingIntent pending =
          PendingIntent.getBroadcast(
              context, 0, operation, PendingIntent.FLAG_NO_CREATE | PendingIntent.FLAG_IMMUTABLE);
      check(pending != null, "recovery pending intent");
      manager.cancel(pending);
      Thread.sleep(3500);
      Engine.reconcile(context, false);
      waitFor(() -> Engine.active(context) != null, 30_000, "recently due alarm recovery");
      stop(AlarmService.STOP);
      waitFor(() -> Engine.active(context) == null, 10_000, "recovered alarm dismissed");
      Engine.remove(context, recovery.id);

      phase("restore and missed one-shot");
      Alarm future = sample("예약 복구 시험", 120_000);
      Engine.save(context, future);
      Engine.restore(context, true);
      check(Engine.scheduled(context, future.id) == future.oneTimeAt, "boot re-arm retains target");
      Engine.remove(context, future.id);
      Alarm expired = sample("놓친 알람 시험", -1_000);
      Engine.save(context, expired);
      check(
          !Engine.find(context, expired.id).enabled
              && Engine.find(context, expired.id).missedAt > 0,
          "expired one-shot is visible as missed");
      Engine.remove(context, expired.id);
      check(
          Engine.importData(
                  context,
                  "{\"alarms\":[{\"h\":6,\"m\":15,\"label\":\"평.10번.2회.9번출\",\"days\":[1,2,3,4,5],\"sound\":\"tiger\",\"enabled\":true}]}")
              == 1,
          "web backup import");
      Alarm imported = Engine.alarms(context).get(0);
      check(!imported.enabled && imported.days == 62, "restored alarms require enabling");
      Alarm secondFixture = new Alarm();
      secondFixture.hour = 9;
      secondFixture.minute = 0;
      secondFixture.enabled = false;
      Engine.save(context, secondFixture);
      phase("native screens");
      Intent main = new Intent(context, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
      Activity activity = startActivitySync(main);
      waitForIdleSync();
      check(activity != null, "native list launch");
      Thread.sleep(1500);
      capture("qa-list.png");
      Intent edit =
          new Intent(context, EditActivity.class)
              .putExtra("id", imported.id)
              .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
      Activity editor = startActivitySync(edit);
      waitForIdleSync();
      check(editor != null, "native editor launch");
      Thread.sleep(1500);
      capture("qa-editor.png");
      runOnMainSync(editor::finish);
      waitForIdleSync();
      result.putString("result", "PASS: " + checks + " Android 35 device checks");
      finish(Activity.RESULT_OK, result);
    } catch (Throwable e) {
      StringWriter text = new StringWriter();
      e.printStackTrace(new PrintWriter(text));
      result.putString("failure", text.toString());
      if (context != null) result.putString("alarm_logs", Engine.logs(context).toString());
      finish(Activity.RESULT_CANCELED, result);
    }
  }
}
