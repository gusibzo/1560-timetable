package kr.palcheonjo.alarm1560.tests;

import android.app.*;
import android.content.*;
import android.graphics.*;
import android.os.Bundle;
import android.view.View;
import java.io.*;
import kr.palcheonjo.alarm1560.*;

/** Render the app's own native window without launcher/ANR overlays from a slow emulator. */
public final class ScreenTest extends Instrumentation {
  @Override
  public void onCreate(Bundle args) {
    super.onCreate(args);
    start();
  }

  private void capture(Activity activity, String filename) throws Exception {
    waitForIdleSync();
    Thread.sleep(1500);
    final Throwable[] failure = new Throwable[1];
    runOnMainSync(
        () -> {
          try {
            View view = activity.getWindow().getDecorView();
            if (view.getWidth() == 0 || view.getHeight() == 0) {
              android.util.DisplayMetrics m = activity.getResources().getDisplayMetrics();
              view.measure(
                  View.MeasureSpec.makeMeasureSpec(m.widthPixels, View.MeasureSpec.EXACTLY),
                  View.MeasureSpec.makeMeasureSpec(m.heightPixels, View.MeasureSpec.EXACTLY));
              view.layout(0, 0, m.widthPixels, m.heightPixels);
            }
            Bitmap b =
                Bitmap.createBitmap(view.getWidth(), view.getHeight(), Bitmap.Config.ARGB_8888);
            view.draw(new Canvas(b));
            try (FileOutputStream out =
                new FileOutputStream(
                    new File(getTargetContext().getExternalFilesDir(null), filename))) {
              b.compress(Bitmap.CompressFormat.PNG, 100, out);
            }
            b.recycle();
          } catch (Throwable e) {
            failure[0] = e;
          }
        });
    if (failure[0] != null) throw new Exception(failure[0]);
  }

  @Override
  public void onStart() {
    Bundle out = new Bundle();
    try {
      Context c = getTargetContext();
      Activity main =
          startActivitySync(
              new Intent(c, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
      capture(main, "qa-native-list.png");
      Alarm first = Engine.alarms(c).get(0);
      Activity edit =
          startActivitySync(
              new Intent(c, EditActivity.class)
                  .putExtra("id", first.id)
                  .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
      capture(edit, "qa-native-editor.png");
      runOnMainSync(edit::finish);
      out.putString("result", "PASS: native window renders");
      finish(Activity.RESULT_OK, out);
    } catch (Throwable e) {
      out.putString("failure", e.toString());
      finish(Activity.RESULT_CANCELED, out);
    }
  }
}
