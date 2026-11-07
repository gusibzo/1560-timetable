package kr.palcheonjo.alarm1560;

import java.util.TimeZone;
import java.util.UUID;
import org.json.JSONObject;

public final class Alarm {
  public String id = UUID.randomUUID().toString(), label = "", date = "", sound = "bell";
  public int hour = 9, minute = 0, days = 0, volume = 100, snoozeMinutes = 5, snoozeLeft = 3;
  public boolean enabled = true, ramp = false, vibrate = true, snooze = true;
  public long oneTimeAt = 0, snoozeUntil = 0, lastFired = 0, missedAt = 0;

  public static Alarm from(JSONObject j) {
    Alarm a = new Alarm();
    a.id = j.optString("id", a.id);
    a.label = j.optString("label", "");
    a.hour = Math.max(0, Math.min(23, j.optInt("hour", 9)));
    a.minute = Math.max(0, Math.min(59, j.optInt("minute", 0)));
    a.days = j.optInt("days", 0) & 127;
    a.date = j.optString("date", "");
    a.sound = Sounds.valid(j.optString("sound", "bell"));
    a.enabled = j.optBoolean("enabled", false);
    a.ramp = j.optBoolean("ramp", false);
    a.vibrate = j.optBoolean("vibrate", true);
    a.snooze = j.optBoolean("snooze", true);
    a.volume = Math.max(10, Math.min(100, j.optInt("volume", 100)));
    a.snoozeMinutes = Math.max(1, Math.min(60, j.optInt("snoozeMinutes", 5)));
    a.snoozeLeft = Math.max(0, Math.min(3, j.optInt("snoozeLeft", 3)));
    a.oneTimeAt = j.optLong("oneTimeAt", 0);
    a.snoozeUntil = j.optLong("snoozeUntil", 0);
    a.lastFired = j.optLong("lastFired", 0);
    a.missedAt = j.optLong("missedAt", 0);
    return a;
  }

  public JSONObject json() {
    JSONObject j = new JSONObject();
    try {
      j.put("id", id)
          .put("label", label)
          .put("hour", hour)
          .put("minute", minute)
          .put("days", days)
          .put("date", date)
          .put("sound", sound)
          .put("enabled", enabled)
          .put("ramp", ramp)
          .put("vibrate", vibrate)
          .put("snooze", snooze)
          .put("volume", volume)
          .put("snoozeMinutes", snoozeMinutes)
          .put("snoozeLeft", snoozeLeft)
          .put("oneTimeAt", oneTimeAt)
          .put("snoozeUntil", snoozeUntil)
          .put("lastFired", lastFired)
          .put("missedAt", missedAt);
    } catch (Exception e) {
      throw new IllegalStateException(e);
    }
    return j;
  }

  public long next(long now) {
    if (snoozeUntil > now) return snoozeUntil;
    if (!enabled) return 0;
    if (days == 0) return oneTimeAt > now ? oneTimeAt : 0;
    return AlarmTime.next(now, hour, minute, days, "", TimeZone.getDefault());
  }

  public void arm(long now) {
    snoozeUntil = 0;
    snoozeLeft = 3;
    missedAt = 0;
    oneTimeAt = days == 0 ? AlarmTime.next(now, hour, minute, 0, date, TimeZone.getDefault()) : 0;
  }
}
