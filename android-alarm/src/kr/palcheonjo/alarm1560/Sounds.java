package kr.palcheonjo.alarm1560;

public final class Sounds {
  public static final String[] IDS = {
    "bell",
    "digital",
    "chime",
    "busbell",
    "siren",
    "rise",
    "lion",
    "tiger",
    "tigerGrowl",
    "rooster",
    "roosterFarm",
    "bird",
    "dog",
    "cat"
  };
  public static final String[] NAMES = {
    "기본 종소리",
    "전자 알람",
    "맑은 차임",
    "버스 벨",
    "사이렌",
    "점점 높아지는 소리",
    "사자 포효",
    "호랑이 포효",
    "호랑이 으르렁",
    "수탉",
    "농장 수탉",
    "새소리",
    "강아지",
    "고양이"
  };

  public static String valid(String id) {
    for (String s : IDS) if (s.equals(id)) return id;
    return "bell";
  }

  public static int index(String id) {
    for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return i;
    return 0;
  }

  public static String file(String id) {
    return "sounds/" + valid(id) + (index(id) < 6 ? ".wav" : ".mp3");
  }
}
