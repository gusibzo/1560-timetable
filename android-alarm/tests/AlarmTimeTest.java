package kr.palcheonjo.alarm1560;

import java.time.*;
import java.util.TimeZone;

public final class AlarmTimeTest {
  static int checks;

  static long at(String text, String zone) {
    return LocalDateTime.parse(text).atZone(ZoneId.of(zone)).toInstant().toEpochMilli();
  }

  static void check(String name, long expected, long actual) {
    checks++;
    if (expected != actual)
      throw new AssertionError(
          name
              + " expected="
              + Instant.ofEpochMilli(expected)
              + " actual="
              + Instant.ofEpochMilli(actual));
  }

  static long next(String now, int hour, int minute, int days, String date, String zone) {
    return AlarmTime.next(at(now, zone), hour, minute, days, date, TimeZone.getTimeZone(zone));
  }

  public static void main(String[] args) {
    String k = "Asia/Seoul";
    check("today", at("2026-11-09T06:15:00", k), next("2026-11-09T05:44:00", 6, 15, 0, "", k));
    check(
        "past time => next day",
        at("2026-11-10T06:15:00", k),
        next("2026-11-09T06:16:00", 6, 15, 0, "", k));
    check(
        "strict equality => next day",
        at("2026-11-10T06:15:00", k),
        next("2026-11-09T06:15:00", 6, 15, 0, "", k));
    check(
        "Friday next weekday",
        at("2026-11-09T06:15:00", k),
        next("2026-11-06T21:00:00", 6, 15, 62, "", k));
    check("Sunday bit", at("2026-11-08T09:00:00", k), next("2026-11-07T21:00:00", 9, 0, 1, "", k));
    check(
        "Saturday bit", at("2026-11-14T09:00:00", k), next("2026-11-07T21:00:00", 9, 0, 64, "", k));
    check(
        "dated alarm",
        at("2026-12-01T04:55:00", k),
        next("2026-11-07T21:00:00", 4, 55, 0, "2026-12-01", k));
    check("past date stays expired", 0, next("2026-11-08T21:53:00", 21, 40, 0, "2026-11-08", k));
    check("invalid date rejected", 0, next("2026-11-08T21:53:00", 21, 40, 0, "2026-02-30", k));
    check(
        "year rollover", at("2027-01-01T00:00:00", k), next("2026-12-31T23:59:59", 0, 0, 0, "", k));
    check(
        "snooze crosses midnight",
        at("2026-11-09T00:04:00", k),
        AlarmTime.snooze(at("2026-11-08T23:59:00", k), 5));
    String ny = "America/New_York";
    check(
        "DST gap normalizes this occurrence",
        at("2026-03-08T03:30:00", ny),
        next("2026-03-08T01:00:00", 2, 30, 127, "", ny));
    check(
        "DST gap does not move tomorrow",
        at("2026-03-09T02:30:00", ny),
        next("2026-03-08T04:00:00", 2, 30, 127, "", ny));
    check(
        "weekly DST keeps wall clock",
        at("2026-03-15T02:30:00", ny),
        next("2026-03-08T04:00:00", 2, 30, 1, "", ny));
    boolean rejected = false;
    try {
      next("2026-11-08T12:00:00", 24, 0, 0, "", k);
    } catch (IllegalArgumentException e) {
      rejected = true;
    }
    if (!rejected) throw new AssertionError("invalid hour");
    checks++;
    System.out.println("PASS: " + checks + " alarm scheduling checks");
  }
}
