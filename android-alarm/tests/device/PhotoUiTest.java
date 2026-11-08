package kr.palcheonjo.alarm1560.tests;

import android.app.*;
import android.content.*;
import android.graphics.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.util.*;
import kr.palcheonjo.alarm1560.*;

/** Uses only disposable emulator data. Includes upgrade preservation and real UI actions. */
public final class PhotoUiTest extends Instrumentation {
  private Context context;
  private Activity main;
  private int checks;

  @Override
  public void onCreate(Bundle args) {
    super.onCreate(args);
    start();
  }

  private void check(boolean condition, String message) {
    if (!condition) throw new AssertionError(message);
    checks++;
  }

  private View tagged(String tag) {
    return main.getWindow().getDecorView().findViewWithTag(tag);
  }

  private void click(String tag) {
    View view = tagged(tag);
    check(view != null, "View missing: " + tag);
    runOnMainSync(view::performClick);
    waitForIdleSync();
  }

  private Alarm time(int hour, int minute) {
    for (Alarm a : Engine.alarms(context)) if (a.hour == hour && a.minute == minute) return a;
    return null;
  }

  private String summary() {
    final String[] value = new String[1];
    runOnMainSync(() -> value[0] = ((TextView) tagged("summary-countdown")).getText().toString());
    return value[0];
  }

  private void launch() {
    main =
        startActivitySync(
            new Intent(context, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
    waitForIdleSync();
  }

  private void capture(String name) throws Exception {
    waitForIdleSync();
    Thread.sleep(700);
    final Throwable[] failure = new Throwable[1];
    runOnMainSync(
        () -> {
          try {
            View view = main.getWindow().getDecorView();
            if (view.getWidth() == 0) {
              android.util.DisplayMetrics m = main.getResources().getDisplayMetrics();
              view.measure(
                  View.MeasureSpec.makeMeasureSpec(m.widthPixels, View.MeasureSpec.EXACTLY),
                  View.MeasureSpec.makeMeasureSpec(m.heightPixels, View.MeasureSpec.EXACTLY));
              view.layout(0, 0, m.widthPixels, m.heightPixels);
            }
            Bitmap bitmap =
                Bitmap.createBitmap(view.getWidth(), view.getHeight(), Bitmap.Config.ARGB_8888);
            view.draw(new Canvas(bitmap));
            try (FileOutputStream out =
                new FileOutputStream(new File(context.getExternalFilesDir(null), name))) {
              bitmap.compress(Bitmap.CompressFormat.PNG, 100, out);
            }
            bitmap.recycle();
          } catch (Throwable error) {
            failure[0] = error;
          }
        });
    if (failure[0] != null) throw new Exception(failure[0]);
  }

  private View description(View view, String text) {
    if (text.contentEquals(
        view.getContentDescription() == null ? "" : view.getContentDescription())) return view;
    if (view instanceof android.view.ViewGroup) {
      android.view.ViewGroup group = (android.view.ViewGroup) view;
      for (int i = 0; i < group.getChildCount(); i++) {
        View found = description(group.getChildAt(i), text);
        if (found != null) return found;
      }
    }
    return null;
  }

  private void stage(String name) {
    Bundle b = new Bundle();
    b.putString("phase", name);
    sendStatus(0, b);
  }

  @Override
  public void onStart() {
    Bundle out = new Bundle();
    try {
      context = getTargetContext();
      for (Alarm a : Engine.alarms(context)) Engine.remove(context, a.id);
      for (int i = 0; i < 200 && Engine.active(context) != null; i++) Engine.finish(context, false);
      context
          .createDeviceProtectedStorageContext()
          .getSharedPreferences("photo-appearance-v1", Context.MODE_PRIVATE)
          .edit()
          .clear()
          .commit();
      Alarm existing = new Alarm();
      existing.hour = 6;
      existing.minute = 15;
      existing.label = "기존 알람";
      existing.enabled = false;
      Engine.save(context, existing);
      stage("photo defaults preserve existing alarms");
      launch();
      check(Engine.find(context, existing.id) != null, "Existing alarm lost");
      check(Engine.alarms(context).size() == 3, "Expected existing alarm plus two photo times");
      Alarm first = time(11, 20), second = time(14, 11);
      check(first != null && second != null, "Reference times missing");
      check(!first.enabled && !second.enabled, "Reference alarms must be off");
      check(summary().equals("알람 꺼짐"), "Off summary");
      Engine.remove(context, existing.id);
      waitForIdleSync();
      Thread.sleep(300);
      capture("qa-photo-main.png");
      stage("card opens editor and switch controls saved alarm");
      ActivityMonitor editor = addMonitor(EditActivity.class.getName(), null, false);
      click("alarm-card-" + first.id);
      Activity edit = waitForMonitorWithTimeout(editor, 15000);
      check(edit != null, "Card did not open editor");
      runOnMainSync(edit::finish);
      waitForIdleSync();
      removeMonitor(editor);
      click("alarm-toggle-" + first.id);
      check(Engine.find(context, first.id).enabled, "Switch did not enable alarm");
      click("alarm-toggle-" + first.id);
      check(!Engine.find(context, first.id).enabled, "Switch did not disable alarm");
      stage("live countdown and persistent reference marker");
      Calendar clock = Calendar.getInstance();
      clock.add(Calendar.MINUTE, 15);
      existing.hour = clock.get(Calendar.HOUR_OF_DAY);
      existing.minute = clock.get(Calendar.MINUTE);
      existing.date = "";
      existing.enabled = true;
      existing.arm(System.currentTimeMillis());
      Engine.save(context, existing);
      waitForIdleSync();
      Thread.sleep(500);
      String before = summary();
      Thread.sleep(2200);
      String after = summary();
      check(before.endsWith("남음") && !before.equals(after), "Countdown did not tick");
      int count = Engine.alarms(context).size();
      runOnMainSync(main::finish);
      waitForIdleSync();
      launch();
      check(Engine.alarms(context).size() == count, "Reference times duplicated after relaunch");
      stage("bottom tabs and floating add button");
      click("main-tab-more");
      check(tagged("main-add").getVisibility() == View.GONE, "Add button must hide on More");
      capture("qa-photo-more.png");
      click("main-tab-alarms");
      check(tagged("main-add").getVisibility() == View.VISIBLE, "Add button missing on alarms");
      editor = addMonitor(EditActivity.class.getName(), null, false);
      click("main-add");
      edit = waitForMonitorWithTimeout(editor, 15000);
      check(edit != null, "Floating add did not open editor");
      runOnMainSync(edit::finish);
      waitForIdleSync();
      removeMonitor(editor);
      stage("selection can be cancelled without deleting data");
      View delete = description(main.getWindow().getDecorView(), "알람 삭제");
      check(delete != null, "Delete tool missing");
      runOnMainSync(delete::performClick);
      waitForIdleSync();
      click("alarm-card-" + first.id);
      check(summary().equals("1개 선택"), "Selection count incorrect");
      click("main-add");
      sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);
      waitForIdleSync();
      sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);
      waitForIdleSync();
      check(Engine.alarms(context).size() == count, "Cancel deleted alarms");
      Engine.remove(context, existing.id);
      waitForIdleSync();
      Thread.sleep(500);
      capture("qa-photo-main-final.png");
      out.putString("result", "PASS: " + checks + " photo-style UI checks");
      finish(Activity.RESULT_OK, out);
    } catch (Throwable error) {
      StringWriter text = new StringWriter();
      error.printStackTrace(new PrintWriter(text));
      out.putString("failure", text.toString());
      finish(Activity.RESULT_CANCELED, out);
    }
  }
}
