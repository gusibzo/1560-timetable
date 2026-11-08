package kr.palcheonjo.alarm1560;

import android.app.Activity;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.view.*;
import android.widget.*;
import java.text.SimpleDateFormat;
import java.util.*;

final class Ui {
  static final int GOLD = 0xffffbc00, WHITE = 0xfff4f4f5, GRAY = 0xffa2a2a7, CARD = 0xff1c1c1e;

  static int dp(Context c, int n) {
    return Math.round(n * c.getResources().getDisplayMetrics().density);
  }

  static GradientDrawable shape(int color, int radius) {
    GradientDrawable g = new GradientDrawable();
    g.setColor(color);
    g.setCornerRadius(radius);
    return g;
  }

  static TextView text(Context c, String t, int size, int color) {
    TextView v = new TextView(c);
    v.setText(t);
    v.setTextSize(size);
    v.setTextColor(color);
    v.setPadding(0, dp(c, 5), 0, dp(c, 5));
    return v;
  }

  static TextView bold(Context c, String t, int size, int color) {
    TextView v = text(c, t, size, color);
    v.setTypeface(null, Typeface.BOLD);
    return v;
  }

  static LinearLayout column(Context c) {
    LinearLayout l = new LinearLayout(c);
    l.setOrientation(LinearLayout.VERTICAL);
    return l;
  }

  static LinearLayout row(Context c) {
    LinearLayout l = new LinearLayout(c);
    l.setGravity(Gravity.CENTER_VERTICAL);
    return l;
  }

  static LinearLayout card(Context c) {
    LinearLayout l = column(c);
    int p = dp(c, 20);
    l.setPadding(p, p, p, p);
    l.setBackground(shape(CARD, dp(c, 24)));
    return l;
  }

  static void addCard(LinearLayout parent, View child) {
    LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2);
    p.bottomMargin = dp(parent.getContext(), 14);
    parent.addView(child, p);
  }

  static Button button(Context c, String title, boolean gold) {
    Button b = new Button(c);
    b.setText(title);
    b.setTextSize(17);
    b.setAllCaps(false);
    b.setTextColor(gold ? Color.BLACK : WHITE);
    b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(gold ? GOLD : 0xff303034));
    b.setMinHeight(dp(c, 54));
    return b;
  }

  static void screen(Activity a, View content) {
    screen(a, content, 18);
  }

  static void screen(Activity a, View content, int sidePadding) {
    a.getWindow().setStatusBarColor(Color.BLACK);
    a.getWindow().setNavigationBarColor(Color.BLACK);
    content.setBackgroundColor(Color.BLACK);
    a.setContentView(content);
    content.setOnApplyWindowInsetsListener(
        (v, insets) -> {
          if (Build.VERSION.SDK_INT >= 30) {
            android.graphics.Insets i =
                insets.getInsets(
                    WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
            v.setPadding(
                dp(a, sidePadding) + i.left, i.top, dp(a, sidePadding) + i.right, i.bottom);
          } else
            v.setPadding(
                dp(a, sidePadding) + insets.getSystemWindowInsetLeft(),
                insets.getSystemWindowInsetTop(),
                dp(a, sidePadding) + insets.getSystemWindowInsetRight(),
                insets.getSystemWindowInsetBottom());
          return insets;
        });
    content.requestApplyInsets();
  }

  static String time(Alarm a) {
    return String.format(Locale.KOREA, "%02d:%02d", a.hour, a.minute);
  }

  static String date(long at) {
    return new SimpleDateFormat("M/d (E) HH:mm", Locale.KOREA).format(new Date(at));
  }

  static String dayDescription(Alarm a) {
    if (a.days == 127) return "매일";
    if (a.days == 62) return "평일";
    if (a.days == 65) return "주말";
    if (a.days == 0) return a.date.isEmpty() ? "한 번" : a.date + " · 한 번";
    String[] names = {"일", "월", "화", "수", "목", "금", "토"};
    StringBuilder s = new StringBuilder();
    for (int n = 0; n < 7; n++) if ((a.days & (1 << n)) != 0) s.append(names[n]).append(" ");
    return s.toString();
  }
}
