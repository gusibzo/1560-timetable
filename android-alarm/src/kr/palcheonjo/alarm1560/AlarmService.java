package kr.palcheonjo.alarm1560;

import android.app.*;
import android.content.*;
import android.content.pm.ServiceInfo;
import android.net.Uri;
import android.os.*;
import org.json.JSONObject;

public final class AlarmService extends Service {
  public static final String STOP = "STOP", SNOOZE = "SNOOZE", CHANNEL = "alarm-ring-v1";
  private final Handler handler = new Handler(Looper.getMainLooper());
  private AlarmAudio audio;
  private PowerManager.WakeLock wake;
  private String token = "";
  private int lastStartId;
  private final Runnable timeout =
      () -> {
        Engine.log(this, "10분 경과로 알람을 종료했습니다");
        Engine.finish(this, false);
        playActive();
      };

  @Override
  public void onCreate() {
    super.onCreate();
    channel(this);
    ensureForeground();
    audio = new AlarmAudio(this);
  }

  /** A stop action can arrive before the original foreground start is delivered. */
  private void ensureForeground() {
    Notification preparing =
        new Notification.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_alarm)
            .setContentTitle("1560 알람 M")
            .setContentText("알람을 준비하고 있습니다")
            .setCategory(Notification.CATEGORY_ALARM)
            .setOngoing(true)
            .build();
    if (Build.VERSION.SDK_INT >= 29)
      startForeground(1560, preparing, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK);
    else startForeground(1560, preparing);
  }

  public static void channel(Context c) {
    NotificationChannel channel =
        new NotificationChannel(CHANNEL, "울리는 알람", NotificationManager.IMPORTANCE_HIGH);
    channel.setDescription("설정한 시간의 알람과 해제·다시 알림 버튼");
    channel.setSound(null, null);
    channel.enableVibration(false);
    channel.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
    c.getSystemService(NotificationManager.class).createNotificationChannel(channel);
  }

  private PendingIntent action(String name, Alarm a) {
    JSONObject active = Engine.active(this);
    long at = active == null ? 0 : active.optLong("at");
    Intent intent =
        new Intent(this, AlarmService.class)
            .setAction(name)
            .setData(Uri.parse("alarm1560://action/" + name + "/" + a.id + "/" + at))
            .putExtra("token", a.id + ":" + at);
    return PendingIntent.getService(
        this, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
  }

  private Notification notification(Alarm a) {
    PendingIntent show =
        PendingIntent.getActivity(
            this,
            101,
            new Intent(this, RingActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    Notification.Builder b =
        new Notification.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_alarm)
            .setContentTitle(Engine.title(a))
            .setContentText("1560 알람 M · 눌러서 알람 해제")
            .setCategory(Notification.CATEGORY_ALARM)
            .setVisibility(Notification.VISIBILITY_PUBLIC)
            .setOngoing(true)
            .setAutoCancel(false)
            .setContentIntent(show)
            .setFullScreenIntent(show, true)
            .addAction(new Notification.Action.Builder(null, "해제", action(STOP, a)).build());
    if (a.snooze && a.snoozeLeft > 0)
      b.addAction(
          new Notification.Action.Builder(null, a.snoozeMinutes + "분 뒤 다시", action(SNOOZE, a))
              .build());
    return b.build();
  }

  @Override
  public int onStartCommand(Intent i, int flags, int startId) {
    lastStartId = startId;
    // Honor every foreground-service start, including a stale/dismissed occurrence.
    ensureForeground();
    String action = i == null ? null : i.getAction();
    if (STOP.equals(action) || SNOOZE.equals(action)) {
      JSONObject active = Engine.active(this);
      String current =
          active == null
              ? ""
              : Alarm.from(active.optJSONObject("alarm")).id + ":" + active.optLong("at");
      if (current.equals(i.getStringExtra("token"))) {
        Engine.finish(this, SNOOZE.equals(action));
        token = "";
      }
    }
    playActive();
    return Engine.active(this) == null ? START_NOT_STICKY : START_STICKY;
  }

  private void playActive() {
    JSONObject record = Engine.active(this);
    if (record == null) {
      shutdown();
      return;
    }
    Alarm a = Alarm.from(record.optJSONObject("alarm"));
    String next = a.id + ":" + record.optLong("at");
    // Become an eligible foreground app before audio focus or sound on Android 15–17.
    if (Build.VERSION.SDK_INT >= 29)
      startForeground(1560, notification(a), ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK);
    else startForeground(1560, notification(a));
    if (next.equals(token)) return;
    token = next;
    audio.stop();
    handler.removeCallbacks(timeout);
    long remaining =
        600_000
            - (System.currentTimeMillis() - record.optLong("started", System.currentTimeMillis()));
    if (remaining <= 0) {
      timeout.run();
      return;
    }
    if (wake != null && wake.isHeld()) wake.release();
    wake =
        getSystemService(PowerManager.class)
            .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "1560Alarm:ring");
    wake.acquire(remaining + 15_000);
    audio.start(a, true);
    handler.postDelayed(timeout, remaining);
    sendBroadcast(new Intent(Engine.CHANGED).setPackage(getPackageName()));
  }

  private void shutdown() {
    audio.stop();
    handler.removeCallbacksAndMessages(null);
    if (wake != null && wake.isHeld()) wake.release();
    wake = null;
    // A newer start may already be queued in system_server.
    if (stopSelfResult(lastStartId)) stopForeground(STOP_FOREGROUND_REMOVE);
  }

  @Override
  public void onDestroy() {
    audio.stop();
    handler.removeCallbacksAndMessages(null);
    if (wake != null && wake.isHeld()) wake.release();
    super.onDestroy();
  }

  @Override
  public IBinder onBind(Intent i) {
    return null;
  }
}
