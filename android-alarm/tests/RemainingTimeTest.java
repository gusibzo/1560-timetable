package kr.palcheonjo.alarm1560;

public final class RemainingTimeTest {
  private static int checks;
  private static final long NOW = 1_794_097_440_000L;

  private static void check(long delta, String expected) {
    String actual = RemainingTime.format(NOW, NOW + delta);
    checks++;
    if (!expected.equals(actual)) throw new AssertionError(delta + ": " + actual + " != " + expected);
  }

  public static void main(String[] args) {
    check(-1000, "알람 시간입니다");
    check(0, "알람 시간입니다");
    check(1, "1초 남음");
    check(999, "1초 남음");
    check(1001, "2초 남음");
    check(59_000, "59초 남음");
    check(60_000, "1분 0초 남음");
    check(61_000, "1분 1초 남음");
    check(119_000, "1분 59초 남음");
    check(120_000, "2분 0초 남음");
    check(3_599_000, "59분 59초 남음");
    check(3_600_000, "1시간 0분 남음");
    check((3*3600+17*60)*1000L, "3시간 17분 남음");
    check(86_400_000, "1일 0시간 0분 남음");
    check((86400+2*3600+3*60+4)*1000L, "1일 2시간 3분 남음");
    check(30L*86_400_000, "30일 0시간 0분 남음");
    System.out.println("PASS: " + checks + " remaining-time checks");
  }
}
