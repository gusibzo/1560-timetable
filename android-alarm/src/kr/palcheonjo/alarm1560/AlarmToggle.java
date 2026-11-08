package kr.palcheonjo.alarm1560;

import android.content.Context;
import android.graphics.*;
import android.view.View;
import android.view.accessibility.AccessibilityNodeInfo;

/** Large, labelled switch; the alarm store remains the source of checked state. */
final class AlarmToggle extends View {
  private final boolean checked;
  private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);

  AlarmToggle(Context context, boolean checked) {
    super(context);
    this.checked = checked;
    setFocusable(true);
  }

  @Override
  protected void onDraw(Canvas canvas) {
    super.onDraw(canvas);
    float border = Ui.dp(getContext(), 3), h = getHeight(), w = getWidth();
    RectF track = new RectF(border / 2, border / 2, w - border / 2, h - border / 2);
    paint.setStyle(Paint.Style.FILL);
    paint.setColor(checked ? Ui.GOLD : Ui.CARD);
    canvas.drawRoundRect(track, h / 2, h / 2, paint);
    paint.setStyle(Paint.Style.STROKE);
    paint.setStrokeWidth(border);
    paint.setColor(checked ? Ui.GOLD : 0xff96969b);
    canvas.drawRoundRect(track, h / 2, h / 2, paint);
    paint.setStyle(Paint.Style.FILL);
    paint.setColor(checked ? Ui.WHITE : 0xff96969b);
    canvas.drawCircle(checked ? w - h / 2 : h / 2, h / 2, h / 2 - Ui.dp(getContext(), 6), paint);
  }

  @Override
  public void onInitializeAccessibilityNodeInfo(AccessibilityNodeInfo info) {
    super.onInitializeAccessibilityNodeInfo(info);
    info.setClassName(android.widget.Switch.class.getName());
    info.setCheckable(true);
    info.setChecked(checked);
  }
}
