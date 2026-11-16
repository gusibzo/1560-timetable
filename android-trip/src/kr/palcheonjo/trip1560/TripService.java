package kr.palcheonjo.trip1560;

import android.app.*;
import android.content.*;
import android.content.pm.ServiceInfo;
import android.location.*;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.os.*;
import java.util.ArrayDeque;

public final class TripService extends Service implements LocationListener {
  static final String START = "START", STOP = "STOP", DUE = "DUE", ARRIVE = "ARRIVE";
  private static final String CHANNEL = "1560-trip";
  private static final int NOTICE = 1560;
  private static final int FLAGS = PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT;
  // The main gate also includes the 1560 arrival stop on the west side.
  private static final double[][] DESTINATIONS = {{37.2476648,127.0791747}, {37.247333,127.078440}, {37.2474500,127.0778667}};
  private final ArrayDeque<Integer> sounds = new ArrayDeque<>();
  private final Handler handler = new Handler(Looper.getMainLooper());
  private MediaPlayer player;
  private LocationManager location;
  private boolean locationReady;
  private boolean tracking;
  private boolean ending;
  private int lastId;

  static SharedPreferences state(Context context) {
    return context.getSharedPreferences("trip", MODE_PRIVATE);
  }

  private static PendingIntent departureIntent(Context context, long at) {
    return PendingIntent.getBroadcast(context, 1,
        new Intent(context, DepartureReceiver.class).putExtra("at", at), FLAGS);
  }

  static void cancelDeparture(Context context) {
    context.getSystemService(AlarmManager.class).cancel(departureIntent(context, 0));
  }

  static void reserve(Context context, long at, boolean leftArea) {
    long now = System.currentTimeMillis();
    if (at <= now - 8 * 3600000L || at > now + 14 * 86400000L) throw new IllegalArgumentException("Departure time");
    AlarmManager alarms = context.getSystemService(AlarmManager.class);
    if (at > now && Build.VERSION.SDK_INT >= 31 && !alarms.canScheduleExactAlarms()) {
      throw new IllegalStateException("Exact alarm permission");
    }
    cancelDeparture(context);
    boolean saved = state(context).edit().clear().putLong("at", at).putBoolean("left", leftArea).commit();
    if (!saved) throw new IllegalStateException("Departure could not be saved");
    try {
      if (at > now) {
        PendingIntent show = PendingIntent.getActivity(context, 2, new Intent(context, TripActivity.class), FLAGS);
        alarms.setAlarmClock(new AlarmManager.AlarmClockInfo(at, show), departureIntent(context, at));
      }
      context.startForegroundService(new Intent(context, TripService.class).setAction(START));
    } catch (RuntimeException error) {
      cancelDeparture(context);
      state(context).edit().clear().commit();
      throw error;
    }
  }

  @Override public void onCreate() {
    super.onCreate();
    location = getSystemService(LocationManager.class);
    NotificationChannel channel = new NotificationChannel(CHANNEL, "1560 운행 추적", NotificationManager.IMPORTANCE_LOW);
    channel.setShowBadge(false);
    getSystemService(NotificationManager.class).createNotificationChannel(channel);
  }

  private void promote(boolean withLocation, String detail) {
    PendingIntent open = PendingIntent.getActivity(this, 2, new Intent(this, TripActivity.class), FLAGS);
    PendingIntent stop = PendingIntent.getService(this, 3, new Intent(this, TripService.class).setAction(STOP), FLAGS);
    Notification notification = new Notification.Builder(this, CHANNEL)
        .setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle("1560 운행 알림")
        .setContentText(detail).setContentIntent(open).setOngoing(true)
        .addAction(new Notification.Action.Builder(null, "끄기", stop).build()).build();
    if (Build.VERSION.SDK_INT >= 29) {
      int type = ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK;
      if (withLocation) type |= ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION;
      startForeground(NOTICE, notification, type);
    } else startForeground(NOTICE, notification);
  }

  @Override public int onStartCommand(Intent intent, int flags, int id) {
    lastId = id;
    String action = intent == null ? START : intent.getAction();
    SharedPreferences prefs = state(this);
    long at = prefs.getLong("at", 0);
    long gateUntil = prefs.getLong("gate-until", 0);
    boolean awaitingGate = gateUntil > System.currentTimeMillis();
    boolean locate = (at != 0 || awaitingGate) && (locationReady || START.equals(action));
    try {
      String status = at > System.currentTimeMillis() ? "출발 예약 · 출발 후 도착 위치 확인"
          : "경희대 사거리·정문 도착 감지 중";
      promote(locate, locate ? status : "운행 알림 재생 중");
      locationReady = locate;
      if (locate && !tracking && (awaitingGate || at <= System.currentTimeMillis())) {
        location.requestLocationUpdates(LocationManager.GPS_PROVIDER, 2000, 4, this, Looper.getMainLooper());
        tracking = true;
      }
    } catch (SecurityException | IllegalArgumentException error) {
      locationReady = false;
      promote(false, "정확한 위치를 허용하면 도착을 감지할 수 있습니다.");
    }

    if (STOP.equals(action) || (at == 0 && !awaitingGate)) {
      cancelDeparture(this);
      prefs.edit().clear().commit();
      stopSelfResult(id);
      return START_NOT_STICKY;
    }
    ending = false;
    handler.removeCallbacksAndMessages(null);
    if (awaitingGate) waitForGate(gateUntil);
    else if (ARRIVE.equals(action) && at <= System.currentTimeMillis()) arrive(false, false);
    else announceDeparture();
    // A tracking service can be recreated after its process was reclaimed.
    if (!locationReady && !ARRIVE.equals(action)) {
      ending = true;
      if (player == null) stopSelfResult(id);
    }
    return locationReady ? START_STICKY : START_NOT_STICKY;
  }

  private void announceDeparture() {
    SharedPreferences prefs = state(this);
    long at = prefs.getLong("at", 0);
    long late = System.currentTimeMillis() - at;
    if (at > 0 && late >= 0 && late <= 60000 && !prefs.getBoolean("departed", false)
        && prefs.edit().putBoolean("departed", true).commit()) play(R.raw.trip_departure);
  }

  @Override public void onLocationChanged(Location fix) {
    long age = (SystemClock.elapsedRealtimeNanos() - fix.getElapsedRealtimeNanos()) / 1000000;
    if (!fix.hasAccuracy() || fix.getAccuracy() <= 0 || fix.getAccuracy() > 100 || age < 0 || age > 25000) return;
    SharedPreferences prefs = state(this);
    long at = prefs.getLong("at", 0);
    long now = System.currentTimeMillis();
    boolean waiting = prefs.getLong("gate-until", 0) > now;
    if (!waiting && (at <= 0 || at > now)) return;
    announceDeparture();
    float closest = Float.POSITIVE_INFINITY;
    int nearest = 0;
    float[] distance = new float[1];
    for (int i = 0; i < DESTINATIONS.length; i++) {
      Location.distanceBetween(fix.getLatitude(), fix.getLongitude(), DESTINATIONS[i][0], DESTINATIONS[i][1], distance);
      if (distance[0] < closest) {
        closest = distance[0];
        nearest = i;
      }
    }
    boolean inside = closest + Math.min(25, fix.getAccuracy() / 3) <= 120;
    if (waiting) {
      if (inside && nearest > 0) {
        endTracking();
        play(R.raw.trip_gate_voice);
      }
    } else if (!prefs.getBoolean("left", false)) {
      if (closest - fix.getAccuracy() >= 220) prefs.edit().putBoolean("left", true).commit();
    } else if (inside) arrive(nearest > 0, nearest == 0);
  }

  private void arrive(boolean gate, boolean checkGate) {
    cancelDeparture(this);
    if (checkGate) {
      long until = System.currentTimeMillis() + 5 * 60000;
      state(this).edit().clear().putLong("gate-until", until).commit();
      waitForGate(until);
    } else endTracking();
    play(gate ? R.raw.trip_gate : R.raw.trip_arrival);
  }

  private void waitForGate(long until) {
    handler.postDelayed(() -> {
      endTracking();
      if (player == null) stopSelfResult(lastId);
    }, Math.max(0, until - System.currentTimeMillis()));
  }

  private void endTracking() {
    handler.removeCallbacksAndMessages(null);
    state(this).edit().clear().commit();
    if (tracking) location.removeUpdates(this);
    tracking = false;
    ending = true;
  }

  private void play(int sound) {
    sounds.add(sound);
    if (player == null) playNext();
  }

  private void playNext() {
    Integer resource = sounds.poll();
    while (resource != null) {
      AudioAttributes attributes = new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM)
          .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build();
      player = MediaPlayer.create(this, resource, attributes, 0);
      if (player != null) {
        player.setWakeMode(this, PowerManager.PARTIAL_WAKE_LOCK);
        player.setOnCompletionListener(done -> { done.release(); player = null; playNext(); });
        player.setOnErrorListener((failed, what, extra) -> { failed.release(); player = null; playNext(); return true; });
        player.start();
        return;
      }
      resource = sounds.poll();
    }
    if (ending) stopSelfResult(lastId);
  }

  @Override public void onDestroy() {
    handler.removeCallbacksAndMessages(null);
    if (tracking) location.removeUpdates(this);
    if (player != null) player.release();
    super.onDestroy();
  }

  @Override public IBinder onBind(Intent intent) { return null; }
}
