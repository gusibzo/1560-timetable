package kr.palcheonjo.alarm1560;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.Build;
import java.util.*;
import org.json.*;

/** Single-process, synchronously committed device-protected alarm state. */
public final class Engine {
  public static final String CHANGED = "kr.palcheonjo.alarm1560.CHANGED";

  private static SharedPreferences prefs(Context c) {
    return c.createDeviceProtectedStorageContext()
        .getSharedPreferences("alarms-v1", Context.MODE_PRIVATE);
  }

  private static JSONObject data(Context c) {
    try {
      return new JSONObject(prefs(c).getString("state", "{}"));
    } catch (JSONException e) {
      return new JSONObject();
    }
  }

  private static void put(JSONObject j, String k, Object v) {
    try {
      j.put(k, v);
    } catch (JSONException e) {
      throw new IllegalStateException(e);
    }
  }

  private static void write(Context c, JSONObject d) {
    if (!prefs(c).edit().putString("state", d.toString()).commit())
      throw new IllegalStateException("알람을 저장하지 못했습니다");
    c.sendBroadcast(new Intent(CHANGED).setPackage(c.getPackageName()));
  }

  private static JSONArray array(JSONObject d, String key) {
    JSONArray a = d.optJSONArray(key);
    if (a == null) {
      a = new JSONArray();
      put(d, key, a);
    }
    return a;
  }

  private static JSONObject object(JSONObject d, String key) {
    JSONObject a = d.optJSONObject(key);
    if (a == null) {
      a = new JSONObject();
      put(d, key, a);
    }
    return a;
  }

  public static synchronized List<Alarm> alarms(Context c) {
    JSONArray aa = array(data(c), "alarms");
    List<Alarm> list = new ArrayList<>();
    for (int i = 0; i < aa.length(); i++) {
      JSONObject j = aa.optJSONObject(i);
      if (j != null) list.add(Alarm.from(j));
    }
    return list;
  }

  public static synchronized Alarm find(Context c, String id) {
    for (Alarm a : alarms(c)) if (a.id.equals(id)) return a;
    return null;
  }

  public static synchronized void save(Context c, Alarm a) {
    JSONObject d = data(c);
    JSONArray old = array(d, "alarms"), out = new JSONArray();
    boolean found = false;
    for (int i = 0; i < old.length(); i++) {
      JSONObject j = old.optJSONObject(i);
      if (j == null) continue;
      if (a.id.equals(j.optString("id"))) {
        out.put(a.json());
        found = true;
      } else out.put(j);
    }
    if (!found) out.put(a.json());
    put(d, "alarms", out);
    write(c, d);
    reconcile(c, false);
  }

  public static synchronized void remove(Context c, String id) {
    JSONObject d = data(c);
    JSONArray old = array(d, "alarms"), out = new JSONArray();
    for (int i = 0; i < old.length(); i++) {
      JSONObject j = old.optJSONObject(i);
      if (j != null && !id.equals(j.optString("id"))) out.put(j);
    }
    put(d, "alarms", out);
    write(c, d);
    reconcile(c, false);
  }

  public static boolean exactAllowed(Context c) {
    return Build.VERSION.SDK_INT < 31
        || c.getSystemService(AlarmManager.class).canScheduleExactAlarms();
  }

  private static PendingIntent operation(Context c, String id, long at) {
    Intent i =
        new Intent(c, AlarmReceiver.class)
            .setAction("RING")
            .setData(Uri.parse("alarm1560://ring/" + id + "/" + at))
            .putExtra("id", id)
            .putExtra("at", at);
    return PendingIntent.getBroadcast(
        c, 0, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
  }

  private static void cancel(Context c, String id, long at) {
    PendingIntent pi = operation(c, id, at);
    c.getSystemService(AlarmManager.class).cancel(pi);
    pi.cancel();
  }

  public static synchronized void reconcile(Context c, boolean force) {
    JSONObject d = data(c), old = object(d, "scheduled"), next = new JSONObject();
    JSONArray aa = array(d, "alarms");
    long now = System.currentTimeMillis();
    Set<String> retained = new HashSet<>();
    for (int n = 0; n < aa.length(); n++) {
      JSONObject j = aa.optJSONObject(n);
      if (j == null) continue;
      Alarm a = Alarm.from(j);
      if (force && a.enabled && a.days == 0 && !a.date.isEmpty() && a.snoozeUntil == 0)
        a.oneTimeAt = AlarmTime.next(now, a.hour, a.minute, 0, a.date, TimeZone.getDefault());
      long oldAt = old.optLong(a.id, 0), at = a.next(now);
      // The app may resume milliseconds before the OS receiver is delivered.
      // Re-arm a recently due reservation as an exact alarm instead of canceling it.
      boolean recentlyDue =
          oldAt > 0
              && oldAt <= now
              && now - oldAt <= 120_000
              && a.lastFired != oldAt
              && (a.enabled || a.snoozeUntil != 0);
      if (recentlyDue) at = oldAt;
      if (!recentlyDue && oldAt > 0 && oldAt <= now && a.lastFired != oldAt) {
        a.missedAt = oldAt;
        event(d, "놓친 알람 · " + title(a));
        try {
          aa.put(n, a.json());
        } catch (JSONException ignored) {
        }
      }
      // A past one-shot remains visibly missed, instead of silently becoming tomorrow.
      if (at == 0 && (a.enabled || a.snoozeUntil != 0)) {
        a.missedAt = oldAt > 0 ? oldAt : (a.snoozeUntil > 0 ? a.snoozeUntil : a.oneTimeAt);
        if (a.missedAt == 0) a.missedAt = now;
        a.enabled = false;
        a.snoozeUntil = 0;
        try {
          aa.put(n, a.json());
        } catch (JSONException ignored) {
        }
        event(d, "예약 시간 경과 · " + title(a));
      } else if (force) {
        try {
          aa.put(n, a.json());
        } catch (JSONException ignored) {
        }
      }
      if (at == 0) continue;
      if (!exactAllowed(c)) continue;
      try {
        if (force || oldAt != at || recentlyDue) {
          if (oldAt != 0) cancel(c, a.id, oldAt);
          PendingIntent show =
              PendingIntent.getActivity(
                  c,
                  0,
                  new Intent(c, MainActivity.class),
                  PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
          c.getSystemService(AlarmManager.class)
              .setAlarmClock(new AlarmManager.AlarmClockInfo(at, show), operation(c, a.id, at));
        }
        put(next, a.id, at);
        retained.add(a.id);
      } catch (SecurityException e) {
        event(d, "정확한 알람 권한을 확인해 주세요");
      }
    }
    Iterator<String> keys = old.keys();
    while (keys.hasNext()) {
      String id = keys.next();
      if (!retained.contains(id)) cancel(c, id, old.optLong(id));
    }
    put(d, "scheduled", next);
    write(c, d);
  }

  public static synchronized long scheduled(Context c, String id) {
    return object(data(c), "scheduled").optLong(id, 0);
  }

  public static synchronized boolean claim(Context c, String id, long at) {
    JSONObject d = data(c), scheduled = object(d, "scheduled");
    if (at <= 0 || scheduled.optLong(id, 0) != at) return false;
    JSONArray aa = array(d, "alarms");
    Alarm hit = null;
    for (int n = 0; n < aa.length(); n++) {
      JSONObject j = aa.optJSONObject(n);
      if (j == null || !id.equals(j.optString("id"))) continue;
      Alarm a = Alarm.from(j);
      if (!a.enabled && a.snoozeUntil == 0) return false;
      if (a.lastFired == at) return false;
      hit = Alarm.from(j);
      if (a.snoozeUntil != at) {
        a.snoozeLeft = 3;
        hit.snoozeLeft = 3;
      }
      a.lastFired = at;
      a.snoozeUntil = 0;
      a.missedAt = 0;
      if (a.days == 0) a.enabled = false;
      try {
        aa.put(n, a.json());
      } catch (JSONException ignored) {
      }
      break;
    }
    if (hit == null) return false;
    scheduled.remove(id);
    JSONObject ring = new JSONObject();
    put(ring, "alarm", hit.json());
    put(ring, "at", at);
    put(ring, "started", System.currentTimeMillis());
    if (d.optJSONObject("active") == null) put(d, "active", ring);
    else array(d, "queue").put(ring);
    event(d, "알람 시작 · " + title(hit));
    write(c, d);
    reconcile(c, false);
    return true;
  }

  public static synchronized JSONObject active(Context c) {
    return data(c).optJSONObject("active");
  }

  public static synchronized void finish(Context c, boolean snooze) {
    JSONObject d = data(c), active = d.optJSONObject("active");
    if (active == null) return;
    Alarm a = Alarm.from(active.optJSONObject("alarm"));
    if (snooze && a.snooze && a.snoozeLeft > 0) {
      JSONArray aa = array(d, "alarms");
      for (int i = 0; i < aa.length(); i++) {
        JSONObject j = aa.optJSONObject(i);
        if (j != null && a.id.equals(j.optString("id"))) {
          Alarm live = Alarm.from(j);
          live.snoozeUntil = AlarmTime.snooze(System.currentTimeMillis(), a.snoozeMinutes);
          live.snoozeLeft = a.snoozeLeft - 1;
          live.missedAt = 0;
          try {
            aa.put(i, live.json());
          } catch (JSONException ignored) {
          }
          break;
        }
      }
      event(d, a.snoozeMinutes + "분 다시 알림 · " + title(a));
    } else event(d, "알람 종료 · " + title(a));
    d.remove("active");
    JSONArray q = array(d, "queue");
    if (q.length() > 0) {
      JSONObject first = q.optJSONObject(0);
      q.remove(0);
      if (first != null) {
        put(first, "started", System.currentTimeMillis());
        put(d, "active", first);
      }
    }
    write(c, d);
    reconcile(c, false);
  }

  public static synchronized void restore(Context c, boolean boot) {
    if (boot) {
      JSONObject d = data(c);
      if (d.optJSONObject("active") != null) {
        event(d, "재부팅으로 재생이 중단되었습니다");
        d.remove("active");
        put(d, "queue", new JSONArray());
        write(c, d);
      }
    }
    reconcile(c, true);
  }

  private static void event(JSONObject d, String message) {
    JSONArray logs = array(d, "logs");
    JSONObject j = new JSONObject();
    put(j, "at", System.currentTimeMillis());
    put(j, "text", message);
    logs.put(j);
    while (logs.length() > 40) logs.remove(0);
  }

  public static synchronized void log(Context c, String message) {
    JSONObject d = data(c);
    event(d, message);
    write(c, d);
  }

  public static synchronized JSONArray logs(Context c) {
    return array(data(c), "logs");
  }

  public static String title(Alarm a) {
    return a.label.isEmpty() ? String.format(Locale.KOREA, "%02d:%02d", a.hour, a.minute) : a.label;
  }

  public static synchronized String exportData(Context c) {
    return data(c).toString();
  }

  public static synchronized int importData(Context c, String raw) throws JSONException {
    JSONObject src = new JSONObject(raw);
    JSONArray aa = src.optJSONArray("alarms");
    if (aa == null || aa.length() > 200) throw new JSONException("알람 백업 파일이 아닙니다");
    JSONObject d = data(c);
    JSONArray out = new JSONArray();
    for (int i = 0; i < aa.length(); i++) {
      JSONObject j = aa.getJSONObject(i);
      Alarm a;
      if (j.has("h")) { // Previous 1560 web alarm backup.
        a = new Alarm();
        a.hour = Math.max(0, Math.min(23, j.optInt("h", 9)));
        a.minute = Math.max(0, Math.min(59, j.optInt("m", 0)));
        a.label = j.optString("label", "");
        a.sound = Sounds.valid(j.optString("sound", "bell"));
        a.volume = 100;
        a.ramp = j.optBoolean("ramp", false);
        a.vibrate = j.optBoolean("vibrate", true);
        a.snooze = j.optBoolean("snooze", true);
        a.snoozeMinutes = Math.max(1, Math.min(60, j.optInt("snoozeMin", 5)));
        JSONArray days = j.optJSONArray("days");
        if (days != null)
          for (int k = 0; k < days.length(); k++) {
            int day = days.optInt(k, -1);
            if (day >= 0 && day < 7) a.days |= 1 << day;
          }
      } else a = Alarm.from(j);
      // Restored alarms require review; importing must never unexpectedly ring.
      a.id = UUID.randomUUID().toString();
      a.enabled = false;
      a.snoozeUntil = 0;
      a.oneTimeAt = 0;
      a.date = "";
      a.missedAt = 0;
      a.lastFired = 0;
      out.put(a.json());
    }
    put(d, "alarms", out);
    event(d, "백업 복원 · 알람 " + out.length() + "개 (꺼짐)");
    write(c, d);
    reconcile(c, false);
    return out.length();
  }
}
