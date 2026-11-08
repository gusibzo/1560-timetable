package kr.palcheonjo.alarm1560;

/** Display-only countdown; alarm delivery remains owned by Android AlarmManager. */
public final class RemainingTime {
  private RemainingTime() {}

  public static String format(long now, long at) {
    if (at <= now) return "알람 시간입니다";
    long delta = at - now;
    long seconds = delta / 1000 + (delta % 1000 == 0 ? 0 : 1);
    long days = seconds / 86400;
    long hours = seconds / 3600 % 24;
    long minutes = seconds / 60 % 60;
    long rest = seconds % 60;
    if (days > 0) return days + "일 " + hours + "시간 " + minutes + "분 남음";
    if (hours > 0) return hours + "시간 " + minutes + "분 남음";
    if (minutes > 0) return minutes + "분 " + rest + "초 남음";
    return rest + "초 남음";
  }
}
