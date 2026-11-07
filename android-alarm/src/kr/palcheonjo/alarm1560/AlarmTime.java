package kr.palcheonjo.alarm1560;

import java.util.Calendar;
import java.util.TimeZone;

/** Wall-clock scheduling without Android dependencies. Weekday bits: Sun=0..Sat=6. */
public final class AlarmTime {
  private AlarmTime() {}

  public static long next(long now, int hour, int minute, int days, String date, TimeZone zone) {
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59)
      throw new IllegalArgumentException("time");
    Calendar base = Calendar.getInstance(zone);
    base.setTimeInMillis(now);
    if (date != null && !date.isEmpty()) {
      try {
        String[] p = date.split("-");
        if (p.length != 3) return 0;
        Calendar c = Calendar.getInstance(zone);
        c.clear();
        c.setLenient(false);
        c.set(
            Integer.parseInt(p[0]),
            Integer.parseInt(p[1]) - 1,
            Integer.parseInt(p[2]),
            hour,
            minute,
            0);
        long at = c.getTimeInMillis();
        return at > now ? at : 0;
      } catch (RuntimeException e) {
        return 0;
      }
    }
    // Rebuild from a noon anchor each day: a DST-normalized nonexistent time must
    // not silently change all later recurring occurrences to that hour.
    base.set(Calendar.HOUR_OF_DAY, 12);
    base.set(Calendar.MINUTE, 0);
    base.set(Calendar.SECOND, 0);
    base.set(Calendar.MILLISECOND, 0);
    for (int i = 0; i < 9; i++) {
      Calendar c = (Calendar) base.clone();
      c.set(Calendar.HOUR_OF_DAY, hour);
      c.set(Calendar.MINUTE, minute);
      c.set(Calendar.SECOND, 0);
      c.set(Calendar.MILLISECOND, 0);
      int day = base.get(Calendar.DAY_OF_WEEK) - 1;
      if ((days == 0 || (days & (1 << day)) != 0) && c.getTimeInMillis() > now)
        return c.getTimeInMillis();
      base.add(Calendar.DATE, 1);
    }
    return 0;
  }

  public static long snooze(long now, int minutes) {
    if (minutes < 1 || minutes > 60) throw new IllegalArgumentException("snooze");
    return now + minutes * 60_000L;
  }
}
